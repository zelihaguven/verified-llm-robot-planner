"""Doğrulanmış planı Behavior Tree (py_trees) ile yürütür (PRD Bölüm 7, Kişi 1).

Her plan adımı "Make sure X" kalıbıyla sarılır (Ögren & Sprague 2022, s. 15-17):
    Fallback("Adım i") = [ Koşul: adım zaten sağlanmış mı?  ,  Eylem: world.execute_skill ]
Kök, hafızalı bir Sequence'tir: tamamlanan adımlar bir sonraki tick'te tekrar
değerlendirilmez. Hafızasız kök, plandaki ara hedefleri (ör. "mutfak masasına git")
sonradan tekrar "yapılmamış" görüp robotu geri gönderir; tek tek adım koşulları bunu
önleyemez. Beklenmedik bir olay planı bozarsa adım başarısız olur ve ExecutionResult
doğrulama katmanına döner, plan orada uyarlanır (Ögren & Sprague 2022, s. 21:
yürütmeyi izle, sapmada yeniden planla). Adım koşulu yine de işe yarar: adıma
gelindiğinde hedefi zaten sağlanmışsa eylem atlanır.
"""
from collections.abc import Callable

import py_trees
from py_trees.common import Status

from src.interfaces import ExecutionResult, PlanStep, SceneGraph, World


def _obj(scene: SceneGraph, object_id: str | None):
    return next((o for o in scene.objects if o.id == object_id), None)


def _done_check(step: PlanStep, placed_object: str | None) -> Callable[[SceneGraph], bool]:
    """Adımın hedefi dünyada zaten sağlanıyor mu? Bilinmeyen eylemde her zaman False."""
    a, args = step.action, step.args
    if a == "navigate":
        return lambda s: s.robot.location == args.get("target")
    if a == "pick":
        return lambda s: s.robot.holding == args.get("object")
    if a == "place":
        def placed(s: SceneGraph) -> bool:
            o = _obj(s, placed_object)
            return o is not None and o.location == args.get("target") and s.robot.holding != o.id
        return placed
    if a in ("open", "close"):
        want = a == "open"
        def state(s: SceneGraph) -> bool:
            o = _obj(s, args.get("object"))
            return o is not None and o.properties.get("open", False) == want
        return state
    return lambda s: False


class _Condition(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, world: World, check: Callable[[SceneGraph], bool]):
        super().__init__(name)
        self._world, self._check = world, check

    def update(self) -> Status:
        return Status.SUCCESS if self._check(self._world.get_scene_graph()) else Status.FAILURE


class _Action(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, world: World, step: PlanStep):
        super().__init__(name)
        self._world, self.step = world, step
        self.reason: str | None = None

    def update(self) -> Status:
        result = self._world.execute_skill(self.step.action, self.step.args)
        self.reason = result.reason
        return Status.SUCCESS if result.success else Status.FAILURE


def _label(step: PlanStep) -> str:
    return f"{step.id}. {step.action} " + " ".join(f"{k}={v}" for k, v in step.args.items())


def build_tree(steps: list[PlanStep], world: World) -> py_trees.composites.Sequence:
    """Doğrulanmış (grounded) adımlardan BT kurar. Adımlar nesne/konum kimlikleri taşımalı."""
    children, last_picked = [], None
    for step in steps:
        if step.action == "pick":
            last_picked = step.args.get("object")
        label = _label(step)
        children.append(py_trees.composites.Selector(
            f"Adım {label}", memory=False, children=[
                _Condition(f"zaten sağlandı mı? ({label})", world, _done_check(step, last_picked)),
                _Action(f"yap: {label}", world, step),
            ]))
    return py_trees.composites.Sequence("Plan", memory=True, children=children)


def render(root: py_trees.behaviour.Behaviour) -> str:
    """Ağacı durumlarıyla çizer: ✓ başarılı, ✕ başarısız, - çalışmadı."""
    return py_trees.display.unicode_tree(root, show_status=True)


def execute(steps: list[PlanStep], world: World, max_ticks: int = 10,
            on_tick: Callable[[str], None] | None = None) -> ExecutionResult:
    """Planı yürütür; başarı, ilk başarısız adım veya tick sınırında durur."""
    root = build_tree(steps, world)
    log: list[str] = []
    for tick in range(1, max_ticks + 1):
        root.tick_once()
        log.append(f"tick {tick}: {root.status.name}")
        if on_tick:
            on_tick(render(root))
        if root.status == Status.SUCCESS:
            return ExecutionResult(success=True, log=log)
        if root.status == Status.FAILURE:
            for step, node in zip(steps, root.children):
                if node.status == Status.FAILURE:
                    action = node.children[1]
                    log.append(f"adım {step.id} başarısız: {action.reason}")
                    return ExecutionResult(success=False, failed_step=step.id,
                                           reason=action.reason, log=log)
    return ExecutionResult(success=False, reason="max_ticks", log=log)
