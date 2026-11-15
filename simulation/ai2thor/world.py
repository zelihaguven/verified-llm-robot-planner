"""Seviye 2 simülasyon: AI2-THOR (iTHOR) üzerinde çalışan World uygulaması.

Konumlar sahnedeki sabit taşıyıcılardır (receptacle=True ve pickupable=False, Floor hariç); kimlikleri
THOR objectId'leridir, örn. "CounterTop|-01.87|+00.95|-01.21". Alınabilir taşıyıcılar (kupa, tencere)
konum değil, sıradan nesnedir. Hiçbir konum boş değildir:
- Nesnenin konumu, bulunduğu sabit taşıyıcıdır (parentReceptacles'taki ilk sabit taşıyıcı). Geçerli bir
  taşıyıcısı yoksa nesneye en yakın sabit taşıyıcıdır; tutulan nesne robotun konumundadır.
- Robotun konumu, son navigate'in hedefidir; hiç navigate edilmediyse ajana en yakın sabit taşıyıcıdır.
Yakınlık, THOR dünya koordinatlarındaki öklid mesafesiyle ölçülür (_nearest_location).

Yetenekler SymbolicWorld ile aynı adlarla çağrılır. Başarısızlıkta dönebilecek nedenler:
  unknown_action       eylem adı navigate, pick, place, open, close'dan biri değil
  unknown_location     hedef, konum listesindeki bir taşıyıcı değil
  target_unreachable   hedefin görülebildiği erişilebilir bir nokta bulunamadı (navigate)
  object_not_found     nesne sahnede yok
  hand_full            robot zaten bir nesne tutuyor (pick)
  hand_empty           robot nesne tutmuyor (place)
  not_pickupable       nesne alınabilir değil (pick)
  not_openable         nesne açılıp kapanabilir değil (open, close)
  robot_not_at_object  nesne ajanın görüş ve erişim mesafesinde değil (pick, open, close)
  robot_not_at_target  hedef taşıyıcı ajanın görüş ve erişim mesafesinde değil (place)
  door_closed          hedef taşıyıcı kapalı (place)
  pick_failed          önkoşullar sağlandı ama THOR PickupObject'i reddetti
  place_failed         önkoşullar sağlandı ama THOR PutObject'i reddetti
  open_failed          önkoşullar sağlandı ama THOR OpenObject'i reddetti
  close_failed         önkoşullar sağlandı ama THOR CloseObject'i reddetti
AI2-THOR yalnızca reset() içinde içe aktarılır; kurulu olmasa da bu modül yüklenebilir.
"""
import io
import math

from src.interfaces import Location, RobotState, SceneGraph, SceneObject, SkillResult, World

_MAX_NAVIGATE_CANDIDATES = 60   # hedefe en yakın bu kadar erişilebilir noktada görünürlük denenir
_CAMERA_HORIZON = 30            # tezgah ve masa üstü nesneleri görmek için kamera hafif aşağı bakar


def _room_of(scene_id: str) -> str:
    """iTHOR numaralandırması: 1-30 mutfak, 201-230 oturma odası, 301-330 yatak odası, 401-430 banyo."""
    number = int("".join(ch for ch in scene_id if ch.isdigit()) or 0)
    return {0: "kitchen", 2: "living_room", 3: "bedroom", 4: "bathroom"}.get(number // 100, "unknown")


class AI2ThorWorld(World):
    def __init__(self, scene_id: str | None = None, width: int = 640, height: int = 480):
        self._width, self._height = width, height
        self._controller = None
        self._scene_id: str | None = None
        self._location: str | None = None   # son navigate hedefi; hiç navigate edilmediyse None
        if scene_id:
            self.reset(scene_id)

    # --- World arayüzü ------------------------------------------------------

    def reset(self, scene_id: str) -> None:
        if self._controller is None:
            from ai2thor.controller import Controller
            self._controller = Controller(scene=scene_id, width=self._width, height=self._height)
        else:
            self._controller.reset(scene=scene_id)
        self._scene_id = scene_id
        self._location = None

    def get_scene_graph(self) -> SceneGraph:
        event = self._event()
        things = event.metadata["objects"]
        fixed = [o for o in things if self._is_location(o)]
        fixed_ids = {o["objectId"] for o in fixed}
        robot_location = self._location or self._nearest_location(event.metadata["agent"]["position"], fixed)

        def location_of(o: dict) -> str:
            if o["objectId"] in fixed_ids:           # sabit taşıyıcının kendisi: robot ona gidip açabilir
                return o["objectId"]
            if o["isPickedUp"]:
                return robot_location
            parent = next((p for p in (o["parentReceptacles"] or []) if p in fixed_ids), None)
            return parent or self._nearest_location(o["position"], fixed)

        objects = []
        for o in things:
            if not (o["pickupable"] or o["openable"]) or o["objectType"] == "Floor":
                continue
            properties = {"pickupable": o["pickupable"], "openable": o["openable"]}
            if o["openable"]:
                properties["open"] = o["isOpen"]
            objects.append(SceneObject(id=o["objectId"], type=o["objectType"],
                                       location=location_of(o), properties=properties))
        room = _room_of(self._scene_id or "")
        locations = [Location(id=i, room=room) for i in sorted(fixed_ids)]
        held = event.metadata["inventoryObjects"]
        robot = RobotState(location=robot_location, holding=held[0]["objectId"] if held else None)
        return SceneGraph(objects=objects, locations=locations, robot=robot)

    def get_camera_image(self) -> bytes | None:
        from PIL import Image
        buffer = io.BytesIO()
        Image.fromarray(self._event().frame).save(buffer, format="PNG")
        return buffer.getvalue()

    def execute_skill(self, action: str, args: dict[str, str]) -> SkillResult:
        handler = {
            "navigate": self._navigate,
            "pick": self._pick,
            "place": self._place,
            "open": lambda a: self._set_open(a, True),
            "close": lambda a: self._set_open(a, False),
        }.get(action)
        if handler is None:
            return SkillResult(success=False, reason="unknown_action")
        return handler(args)

    def close(self) -> None:
        """Unity sürecini kapatır."""
        if self._controller is not None:
            self._controller.stop()
            self._controller = None

    # --- Yetenekler ---------------------------------------------------------

    def _navigate(self, args: dict[str, str]) -> SkillResult:
        target = self._find(args.get("target"))
        if target is None or not self._is_location(target):
            return SkillResult(success=False, reason="unknown_location")
        goal = target["position"]
        spots = self._controller.step(action="GetReachablePositions").metadata["actionReturn"] or []
        spots = sorted(spots, key=lambda p: (p["x"] - goal["x"]) ** 2 + (p["z"] - goal["z"]) ** 2)
        for spot in spots[:_MAX_NAVIGATE_CANDIDATES]:
            yaw = math.degrees(math.atan2(goal["x"] - spot["x"], goal["z"] - spot["z"])) % 360
            event = self._controller.step(action="Teleport", position=spot, horizon=_CAMERA_HORIZON,
                                          rotation={"x": 0, "y": yaw, "z": 0}, standing=True)
            if event.metadata["lastActionSuccess"] and self._find(target["objectId"])["visible"]:
                self._location = target["objectId"]
                return SkillResult(success=True)
        return SkillResult(success=False, reason="target_unreachable")

    def _pick(self, args: dict[str, str]) -> SkillResult:
        obj = self._find(args.get("object"))
        if obj is None:
            return SkillResult(success=False, reason="object_not_found")
        if self._event().metadata["inventoryObjects"]:
            return SkillResult(success=False, reason="hand_full")
        if not obj["pickupable"]:
            return SkillResult(success=False, reason="not_pickupable")
        if not obj["visible"]:
            return SkillResult(success=False, reason="robot_not_at_object")
        ok = self._controller.step(action="PickupObject", objectId=obj["objectId"]).metadata["lastActionSuccess"]
        return SkillResult(success=ok, reason=None if ok else "pick_failed")

    def _place(self, args: dict[str, str]) -> SkillResult:
        if not self._event().metadata["inventoryObjects"]:
            return SkillResult(success=False, reason="hand_empty")
        target = self._find(args.get("target"))
        if target is None or not self._is_location(target):
            return SkillResult(success=False, reason="unknown_location")
        if not target["visible"]:
            return SkillResult(success=False, reason="robot_not_at_target")
        if target["openable"] and not target["isOpen"]:
            return SkillResult(success=False, reason="door_closed")
        ok = self._controller.step(action="PutObject", objectId=target["objectId"]).metadata["lastActionSuccess"]
        return SkillResult(success=ok, reason=None if ok else "place_failed")

    def _set_open(self, args: dict[str, str], is_open: bool) -> SkillResult:
        obj = self._find(args.get("object"))
        if obj is None:
            return SkillResult(success=False, reason="object_not_found")
        if not obj["openable"]:
            return SkillResult(success=False, reason="not_openable")
        if not obj["visible"]:
            return SkillResult(success=False, reason="robot_not_at_object")
        if obj["isOpen"] == is_open:
            return SkillResult(success=True)
        action = "OpenObject" if is_open else "CloseObject"
        ok = self._controller.step(action=action, objectId=obj["objectId"]).metadata["lastActionSuccess"]
        return SkillResult(success=ok, reason=None if ok else f"{action[:-6].lower()}_failed")

    # --- Yardımcılar --------------------------------------------------------

    def _event(self):
        if self._controller is None:
            raise RuntimeError("Önce reset(scene_id) çağrılmalı")
        return self._controller.last_event

    def _find(self, object_id: str | None) -> dict | None:
        return next((o for o in self._event().metadata["objects"] if o["objectId"] == object_id), None)

    @staticmethod
    def _is_location(o: dict) -> bool:
        return o["receptacle"] and not o["pickupable"] and o["objectType"] != "Floor"

    @staticmethod
    def _nearest_location(position: dict, locations: list[dict]) -> str:
        """Verilen konuma en yakın sabit taşıyıcının kimliği (konumsuz nesne ve robot için)."""
        def squared_distance(o: dict) -> float:
            return sum((o["position"][axis] - position[axis]) ** 2 for axis in "xyz")
        return min(locations, key=squared_distance)["objectId"]
