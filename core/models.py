# core/models.py

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class SubjectGrade:
    subject: str
    grade: str


@dataclass
class OLevelSummary:
    distinctions: int
    credits: int
    passes: int


@dataclass
class StudentProfile:
    gender: str
    alevel_subjects: List[SubjectGrade]
    general_paper: Optional[str]
    sub_math_or_ict: bool
    olevel: OLevelSummary
    district: Optional[str] = None
    citizenship: Optional[str] = "Ugandan"


@dataclass
class RuleBlock:
    type: str  # e.g. "fixed", "best_of", "and_or", "remaining_best"
    subjects: Optional[List[str]] = None
    count: Optional[int] = None
    weight: int = 0


@dataclass
class Programme:
    university: str
    programme_name: str
    code: str
    duration: Optional[int]

    # Scheme availability (DQ, GS, PS, etc.)
    schemes: List[str]

    # Rule blocks
    essential: RuleBlock
    relevant: Optional[RuleBlock]
    desirable: Optional[RuleBlock]

    # Cutoffs per scheme
    cutoffs: Dict[str, Optional[float]]

    # Optional notes
    notes: Optional[str] = None


@dataclass
class ProgrammeResult:
    programme: Programme
    weight: float
    eligible: bool
    status: str  # SAFE / BORDERLINE / RISKY / NOT_ELIGIBLE
    reason: Optional[str] = None
