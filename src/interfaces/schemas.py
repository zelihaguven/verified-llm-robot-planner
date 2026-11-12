"""Modüller arası veri formatları (PRD Bölüm 6). Değişiklik: PR + dört kişinin onayı."""
from typing import Literal

from pydantic import BaseModel, Field


# --- Ortamın durumu ---------------------------------------------------------

class SceneObject(BaseModel):
    id: str                                   # örn. "mug_1"
    type: str                                 # örn. "mug"
    color: str | None = None
    location: str                             # bir Location.id
    properties: dict[str, bool] = Field(default_factory=dict)  # örn. {"pickupable": True}


class Location(BaseModel):
    id: str                                   # örn. "kitchen_table"
    room: str                                 # örn. "kitchen"
    reachable: bool = True


class RobotState(BaseModel):
    location: str                             # bir Location.id
    holding: str | None = None                # bir SceneObject.id


class SceneGraph(BaseModel):
    objects: list[SceneObject]
    locations: list[Location]
    robot: RobotState


# --- LLM çıktısı (Kişi 2) ---------------------------------------------------

class PlanStep(BaseModel):
    id: int
    # Bilinçli olarak serbest metin: LLM yetenek dışı bir eylem uydurursa
    # bunu şema değil doğrulama katmanı yakalar (issue: "not_capable").
    action: str
    args: dict[str, str] = Field(default_factory=dict)


class Plan(BaseModel):
    command: str
    status: Literal["ok", "needs_clarification"]
    clarification_question: str | None = None
    steps: list[PlanStep] = Field(default_factory=list)


# --- Grounding (Kişi 3) -----------------------------------------------------

class GroundingResult(BaseModel):
    mention: str                              # örn. "kırmızı kupa"
    status: Literal["unique", "ambiguous", "not_found"]
    candidates: list[str] = Field(default_factory=list)  # SceneObject.id listesi


# --- Doğrulama (Kişi 4) -----------------------------------------------------

IssueType = Literal[
    "object_not_found",
    "ambiguous_reference",
    "precondition_failed",
    "unsafe",
    "not_capable",
]


class VerificationIssue(BaseModel):
    step: int | None = None                   # sorunlu PlanStep.id
    type: IssueType
    detail: str


class VerificationResult(BaseModel):
    decision: Literal["execute", "clarify", "adapt", "safe_stop"]
    grounded_steps: list[PlanStep] = Field(default_factory=list)  # args içinde nesne id'leri
    issues: list[VerificationIssue] = Field(default_factory=list)
    message_to_user: str | None = None


# --- Yürütme (Kişi 1) -------------------------------------------------------

class SkillResult(BaseModel):
    success: bool
    reason: str | None = None                 # örn. "target_unreachable"


class ExecutionResult(BaseModel):
    success: bool
    failed_step: int | None = None
    reason: str | None = None
    log: list[str] = Field(default_factory=list)
