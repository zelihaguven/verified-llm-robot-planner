"""Her simülatörün uyguladığı arayüz (PRD Bölüm 6)."""
from abc import ABC, abstractmethod

from .schemas import SceneGraph, SkillResult


class World(ABC):
    @abstractmethod
    def reset(self, scene_id: str) -> None: ...

    @abstractmethod
    def get_scene_graph(self) -> SceneGraph: ...

    @abstractmethod
    def get_camera_image(self) -> bytes | None:
        """PNG baytları; görüntü olmayan dünyada (SymbolicWorld) None."""

    @abstractmethod
    def execute_skill(self, action: str, args: dict[str, str]) -> SkillResult: ...
