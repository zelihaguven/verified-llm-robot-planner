import json

import pytest

from simulation.symbolic.world import SymbolicWorld


@pytest.fixture
def world():
    return SymbolicWorld("home_office")


def obj(world, object_id):
    return next(o for o in world.get_scene_graph().objects if o.id == object_id)


def test_red_mug_to_office_desk(world):
    for action, args in [
        ("navigate", {"target": "kitchen_table"}),
        ("pick", {"object": "mug_1"}),
        ("navigate", {"target": "office_desk"}),
        ("place", {"target": "office_desk"}),
    ]:
        assert world.execute_skill(action, args).success, action
    scene = world.get_scene_graph()
    assert scene.robot.holding is None
    assert obj(world, "mug_1").location == "office_desk"


def test_held_object_moves_with_robot(world):
    world.execute_skill("navigate", {"target": "kitchen_table"})
    world.execute_skill("pick", {"object": "mug_1"})
    world.execute_skill("navigate", {"target": "office_shelf"})
    assert obj(world, "mug_1").location == "office_shelf"


@pytest.mark.parametrize("action, args, reason", [
    ("fly", {}, "unknown_action"),
    ("navigate", {"target": "garage"}, "unknown_location"),
    ("pick", {"object": "apple_1"}, "object_not_found"),
    ("pick", {"object": "mug_1"}, "robot_not_at_object"),      # robot tezgahta, kupa masada
    ("place", {"target": "kitchen_counter"}, "hand_empty"),
    ("open", {"object": "mug_2"}, "not_openable"),
    ("open", {"object": "drawer_1"}, "robot_not_at_object"),
])
def test_failed_preconditions(world, action, args, reason):
    before = world.get_scene_graph()
    result = world.execute_skill(action, args)
    assert not result.success and result.reason == reason
    assert world.get_scene_graph() == before  # başarısız yetenek sahneyi değiştirmez


def test_hand_full_and_not_pickupable(world):
    world.execute_skill("pick", {"object": "mug_2"})
    assert world.execute_skill("pick", {"object": "mug_2"}).reason == "hand_full"
    world.execute_skill("navigate", {"target": "office_desk"})
    world.execute_skill("place", {"target": "office_desk"})
    assert world.execute_skill("pick", {"object": "laptop_1"}).reason == "not_pickupable"


def test_place_requires_being_at_target(world):
    world.execute_skill("pick", {"object": "mug_2"})
    assert world.execute_skill("place", {"target": "office_desk"}).reason == "robot_not_at_target"


def test_open_and_close_drawer(world):
    world.execute_skill("navigate", {"target": "office_desk"})
    assert world.execute_skill("open", {"object": "drawer_1"}).success
    assert obj(world, "drawer_1").properties["open"] is True
    assert world.execute_skill("close", {"object": "drawer_1"}).success
    assert obj(world, "drawer_1").properties["open"] is False


def test_unreachable_location(tmp_path):
    scene = {
        "locations": [{"id": "a", "room": "r", "reachable": True},
                      {"id": "b", "room": "r", "reachable": False}],
        "objects": [],
        "robot": {"location": "a", "holding": None},
    }
    (tmp_path / "s.json").write_text(json.dumps(scene), encoding="utf-8")
    world = SymbolicWorld("s", scenes_dir=tmp_path)
    assert world.execute_skill("navigate", {"target": "b"}).reason == "target_unreachable"


def test_scene_graph_is_a_copy(world):
    world.get_scene_graph().robot.location = "office_desk"
    assert world.get_scene_graph().robot.location == "kitchen_counter"


def test_reset_restores_scene(world):
    world.execute_skill("pick", {"object": "mug_2"})
    world.reset("home_office")
    assert world.get_scene_graph().robot.holding is None


def test_requires_reset():
    with pytest.raises(RuntimeError):
        SymbolicWorld().get_scene_graph()
