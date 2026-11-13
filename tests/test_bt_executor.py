from simulation.symbolic.world import SymbolicWorld
from src.execution.bt_executor import build_tree, execute, render
from src.interfaces import PlanStep

MUG_TO_OFFICE = [
    PlanStep(id=1, action="navigate", args={"target": "kitchen_table"}),
    PlanStep(id=2, action="pick", args={"object": "mug_1"}),
    PlanStep(id=3, action="navigate", args={"target": "office_desk"}),
    PlanStep(id=4, action="place", args={"target": "office_desk"}),
]


def mug(world):
    return next(o for o in world.get_scene_graph().objects if o.id == "mug_1")


def test_full_plan_succeeds():
    world = SymbolicWorld("home_office")
    result = execute(MUG_TO_OFFICE, world)
    assert result.success and result.failed_step is None
    assert mug(world).location == "office_desk"
    assert world.get_scene_graph().robot.holding is None


def test_root_sequence_keeps_memory():
    # Hafızasız kök, tamamlanmış ara adımları (mutfak masasına git) tekrar çalıştırırdı.
    assert build_tree(MUG_TO_OFFICE, SymbolicWorld("home_office")).memory is True


def test_failure_stops_at_failed_step():
    world = SymbolicWorld("home_office")
    plan = [PlanStep(id=1, action="pick", args={"object": "mug_1"}), *MUG_TO_OFFICE[2:]]
    result = execute(plan, world)
    assert not result.success
    assert result.failed_step == 1 and result.reason == "robot_not_at_object"
    assert world.get_scene_graph().robot.location == "kitchen_counter"  # sonraki adımlar çalışmadı


def test_already_satisfied_step_is_skipped():
    world = SymbolicWorld("home_office")
    world.execute_skill("navigate", {"target": "kitchen_table"})
    assert execute(MUG_TO_OFFICE, world).success


def test_unknown_action_fails():
    world = SymbolicWorld("home_office")
    result = execute([PlanStep(id=1, action="lift", args={"object": "laptop_1"})], world)
    assert result.failed_step == 1 and result.reason == "unknown_action"


def test_open_drawer():
    world = SymbolicWorld("home_office")
    plan = [PlanStep(id=1, action="navigate", args={"target": "office_desk"}),
            PlanStep(id=2, action="open", args={"object": "drawer_1"})]
    assert execute(plan, world).success


def test_render_shows_statuses():
    world = SymbolicWorld("home_office")
    root = build_tree([PlanStep(id=1, action="pick", args={"object": "mug_1"})], world)
    root.tick_once()
    text = render(root)
    assert "✕" in text and "1. pick object=mug_1" in text
