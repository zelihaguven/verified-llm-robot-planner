"""15 farklı görüş açısından kamera görüntüsü ve o görüntüde görünen nesnelerin listesini kaydeder.

Kullanım (depo kökünden, ai2thor kurulu olmalı):
    python -m simulation.ai2thor.capture_images

Çıktı: data/images/view_01.png ve aynı adlı view_01.json (01..15).
JSON'daki nesne listesi görüntünün kendisinden gelir: AI2-THOR'un instance segmentation
çıktısında en az MIN_PIXELS piksel kaplayan nesneler.
Görüş açıları rastgele değil, "en uzak nokta" yöntemiyle seçilir: her yeni görüntü, seçilmiş
olanlara konum ve bakış yönü bakımından en uzak olanıdır. Böylece 15 görüntü odanın farklı yerlerini
ve yönlerini kapsar. Sonuç her çalıştırmada aynıdır.
"""
import json
import math
from pathlib import Path

from PIL import Image

SCENE = "FloorPlan1"
NUM_VIEWS = 15
MIN_VISIBLE_OBJECTS = 4      # çok boş görüntüler atlanır
MIN_PIXELS = 500             # bundan küçük parçalar "görünür" sayılmaz
YAW_WEIGHT = 1.0             # 90 derecelik yön farkı, 1 metrelik konum farkı kadar sayılır
HORIZONS = (0, 30)           # kamera eğimi
YAWS = (0, 90, 180, 270)
OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "images"


def visible_objects(event) -> list[dict]:
    by_id = {o["objectId"]: o for o in event.metadata["objects"]}
    found = []
    for object_id, mask in event.instance_masks.items():
        pixels = int(mask.sum())
        if pixels < MIN_PIXELS or object_id not in by_id:
            continue
        o = by_id[object_id]
        found.append({"objectId": object_id, "objectType": o["objectType"], "pixels": pixels,
                      "pickupable": o["pickupable"], "openable": o["openable"], "isOpen": o["isOpen"],
                      "parentReceptacles": o["parentReceptacles"] or []})
    return sorted(found, key=lambda x: -x["pixels"])


def _view_distance(a: tuple, b: tuple) -> float:
    """İki görüş arasındaki uzaklık: konum (metre) ve bakış yönü farkı (90 derece = YAW_WEIGHT)."""
    (sa, ya), (sb, yb) = a[:2], b[:2]
    yaw_diff = min(abs(ya - yb), 360 - abs(ya - yb))
    return math.hypot(sa["x"] - sb["x"], sa["z"] - sb["z"]) + YAW_WEIGHT * yaw_diff / 90


def _pick_diverse(views: list[tuple], count: int) -> list[tuple]:
    """En çok nesne gören görüşten başlar, sonra her adımda seçilenlere en uzak olanı ekler."""
    chosen = [max(views, key=lambda v: len(v[3]))]
    while len(chosen) < min(count, len(views)):
        chosen.append(max((v for v in views if v not in chosen),
                          key=lambda v: min(_view_distance(v, c) for c in chosen)))
    return chosen


def main() -> None:
    from ai2thor.controller import Controller

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    controller = Controller(scene=SCENE, width=640, height=480, renderInstanceSegmentation=True)

    def look(spot: dict, yaw: int, horizon: int):
        return controller.step(action="TeleportFull", position=spot, horizon=horizon, standing=True,
                               rotation={"x": 0, "y": yaw, "z": 0})

    try:
        spots = controller.step(action="GetReachablePositions").metadata["actionReturn"]
        views = []                                       # (konum, yaw, eğim, görünen nesneler)
        for spot in spots:
            for yaw in YAWS:
                for horizon in HORIZONS:
                    event = look(spot, yaw, horizon)
                    objects = visible_objects(event) if event.metadata["lastActionSuccess"] else []
                    if len(objects) >= MIN_VISIBLE_OBJECTS:
                        views.append((spot, yaw, horizon, objects))
        for number, (spot, yaw, horizon, objects) in enumerate(_pick_diverse(views, NUM_VIEWS), start=1):
            name = f"view_{number:02d}"
            Image.fromarray(look(spot, yaw, horizon).frame).save(OUT_DIR / f"{name}.png")
            record = {"image": f"{name}.png", "scene": SCENE,
                      "agent": {"position": spot, "rotation_y": yaw, "camera_horizon": horizon},
                      "visible_objects": objects}
            (OUT_DIR / f"{name}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False),
                                                  encoding="utf-8")
        print(f"{min(NUM_VIEWS, len(views))} görüntü kaydedildi: {OUT_DIR}")
    finally:
        controller.stop()


if __name__ == "__main__":
    main()
