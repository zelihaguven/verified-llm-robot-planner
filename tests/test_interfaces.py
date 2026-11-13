import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.interfaces import Plan, SceneGraph, VerificationResult, World

SCENES = Path(__file__).resolve().parents[1] / "simulation" / "symbolic" / "scenes"


def test_scenes_are_valid_and_consistent():
    for path in SCENES.glob("*.json"):
        scene = SceneGraph.model_validate(json.loads(path.read_text(encoding="utf-8")))
        location_ids = {loc.id for loc in scene.locations}
        object_ids = [obj.id for obj in scene.objects]
        assert len(object_ids) == len(set(object_ids)), f"{path.name}: tekrar eden nesne id"
        assert all(obj.location in location_ids for obj in scene.objects), path.name
        assert scene.robot.location in location_ids, path.name
        assert all(loc.door in object_ids for loc in scene.locations if loc.door), path.name


def test_prd_plan_example_parses():
    plan = Plan.model_validate({
        "command": "Mutfaktaki kırmızı kupayı ofisteki masaya götür",
        "status": "ok",
        "steps": [
            {"id": 1, "action": "navigate", "args": {"target": "mutfak masası"}},
            {"id": 2, "action": "pick", "args": {"object": "kırmızı kupa"}},
        ],
    })
    assert plan.steps[1].action == "pick"


def test_unknown_action_is_left_to_verification():
    plan = Plan.model_validate({"command": "Masayı kaldır", "status": "ok",
                                "steps": [{"id": 1, "action": "lift", "args": {"object": "masa"}}]})
    assert plan.steps[0].action == "lift"


def test_invalid_decision_is_rejected():
    with pytest.raises(ValidationError):
        VerificationResult.model_validate({"decision": "maybe"})


def test_world_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        World()
