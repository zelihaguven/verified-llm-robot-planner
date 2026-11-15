import pytest

pytest.importorskip("ai2thor")  # ai2thor kurulu değilse (ör. Windows) bu dosya atlanır

from simulation.ai2thor.world import AI2ThorWorld
from src.execution.bt_executor import execute
from src.interfaces import PlanStep

MUG_SOURCE = "CounterTop|-01.87|+00.95|-01.21"
MUG_TARGET = "CounterTop|+00.69|+00.95|-02.48"


@pytest.fixture(scope="module")
def world():
    w = AI2ThorWorld("FloorPlan1")
    yield w
    w.close()


def mug(world):
    return next(o for o in world.get_scene_graph().objects if o.type == "Mug")


def test_scene_graph_has_locations_and_objects(world):
    world.reset("FloorPlan1")
    scene = world.get_scene_graph()
    assert MUG_SOURCE in {loc.id for loc in scene.locations}
    assert all(loc.id.split("|")[0] != "Floor" for loc in scene.locations)
    assert mug(world).location == MUG_SOURCE
    assert scene.robot.holding is None


def assert_consistent(scene):
    location_ids = {loc.id for loc in scene.locations}
    assert all(obj.location in location_ids for obj in scene.objects)
    assert scene.robot.location in location_ids


def test_scene_graph_is_consistent_before_and_after_navigate(world):
    # tests/test_interfaces.py'deki sahne tutarlılık kontrolünün AI2ThorWorld karşılığı
    world.reset("FloorPlan1")
    assert_consistent(world.get_scene_graph())          # navigate öncesi
    assert world.execute_skill("navigate", {"target": MUG_TARGET}).success
    scene = world.get_scene_graph()
    assert_consistent(scene)
    assert scene.robot.location == MUG_TARGET
    assert all(loc.id.split("|")[0] not in ("Floor", "Mug", "Pot", "Cup") for loc in scene.locations)


def test_camera_image_is_png(world):
    world.reset("FloorPlan1")
    assert world.get_camera_image().startswith(b"\x89PNG")


def test_move_mug_between_counters(world):
    world.reset("FloorPlan1")
    mug_id = mug(world).id
    plan = [
        PlanStep(id=1, action="navigate", args={"target": MUG_SOURCE}),
        PlanStep(id=2, action="pick", args={"object": mug_id}),
        PlanStep(id=3, action="navigate", args={"target": MUG_TARGET}),
        PlanStep(id=4, action="place", args={"target": MUG_TARGET}),
    ]
    result = execute(plan, world)
    assert result.success and result.failed_step is None
    assert mug(world).location == MUG_TARGET
    assert world.get_scene_graph().robot.holding is None


def test_pick_without_navigating_fails_like_symbolic_world(world):
    world.reset("FloorPlan1")
    plan = [PlanStep(id=1, action="pick", args={"object": mug(world).id})]
    result = execute(plan, world)
    assert not result.success and result.reason == "robot_not_at_object"
