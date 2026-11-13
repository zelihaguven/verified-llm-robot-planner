"""Seviye 1 simülasyon: JSON sahne üzerinde çalışan sembolik dünya (PRD Bölüm 3).

Yetenekler nesne ve konum kimlikleriyle çağrılır (grounding sonrası), örn.
    world.execute_skill("pick", {"object": "mug_1"})
Ön koşul sağlanmazsa sahne değişmez ve SkillResult(success=False, reason=...) döner.
"""
import json
from pathlib import Path

from src.interfaces import SceneGraph, SceneObject, SkillResult, World

SCENES_DIR = Path(__file__).resolve().parent / "scenes"


class SymbolicWorld(World):
    def __init__(self, scene_id: str | None = None, scenes_dir: Path = SCENES_DIR):
        self._scenes_dir = Path(scenes_dir)
        self._scene: SceneGraph | None = None
        if scene_id:
            self.reset(scene_id)

    # --- World arayüzü ------------------------------------------------------

    def reset(self, scene_id: str) -> None:
        path = self._scenes_dir / f"{scene_id}.json"
        self._scene = SceneGraph.model_validate(json.loads(path.read_text(encoding="utf-8")))

    def get_scene_graph(self) -> SceneGraph:
        return self._require_scene().model_copy(deep=True)  # dışarıdan değiştirilemesin

    def get_camera_image(self) -> bytes | None:
        return None

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

    # --- Yetenekler ---------------------------------------------------------

    def _navigate(self, args: dict[str, str]) -> SkillResult:
        scene = self._require_scene()
        target = args.get("target")
        location = next((loc for loc in scene.locations if loc.id == target), None)
        if location is None:
            return SkillResult(success=False, reason="unknown_location")
        if not location.reachable:
            return SkillResult(success=False, reason="target_unreachable")
        if location.door:
            door = self._find_object(location.door)
            if door is None or not door.properties.get("open", False):
                return SkillResult(success=False, reason="door_closed")
        scene.robot.location = target
        if scene.robot.holding:  # tutulan nesne robotla birlikte taşınır
            self._find_object(scene.robot.holding).location = target
        return SkillResult(success=True)

    def _pick(self, args: dict[str, str]) -> SkillResult:
        scene = self._require_scene()
        obj = self._find_object(args.get("object"))
        if obj is None:
            return SkillResult(success=False, reason="object_not_found")
        if scene.robot.holding is not None:
            return SkillResult(success=False, reason="hand_full")
        if not obj.properties.get("pickupable", False):
            return SkillResult(success=False, reason="not_pickupable")
        if scene.robot.location != obj.location:
            return SkillResult(success=False, reason="robot_not_at_object")
        scene.robot.holding = obj.id
        return SkillResult(success=True)

    def _place(self, args: dict[str, str]) -> SkillResult:
        scene = self._require_scene()
        target = args.get("target")
        if scene.robot.holding is None:
            return SkillResult(success=False, reason="hand_empty")
        if all(loc.id != target for loc in scene.locations):
            return SkillResult(success=False, reason="unknown_location")
        if scene.robot.location != target:
            return SkillResult(success=False, reason="robot_not_at_target")
        self._find_object(scene.robot.holding).location = target
        scene.robot.holding = None
        return SkillResult(success=True)

    def _set_open(self, args: dict[str, str], is_open: bool) -> SkillResult:
        scene = self._require_scene()
        obj = self._find_object(args.get("object"))
        if obj is None:
            return SkillResult(success=False, reason="object_not_found")
        if not obj.properties.get("openable", False):
            return SkillResult(success=False, reason="not_openable")
        if scene.robot.location != obj.location:
            return SkillResult(success=False, reason="robot_not_at_object")
        obj.properties["open"] = is_open
        return SkillResult(success=True)

    # --- Yardımcılar --------------------------------------------------------

    def _require_scene(self) -> SceneGraph:
        if self._scene is None:
            raise RuntimeError("Önce reset(scene_id) çağrılmalı")
        return self._scene

    def _find_object(self, object_id: str | None) -> SceneObject | None:
        return next((o for o in self._require_scene().objects if o.id == object_id), None)
