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
    type: str  # fixed, best_of, optional, remaining_best, and_or
    subjects: Optional[List[str]] = None
    count: Optional[int] = None
    weight: int = 0


@dataclass
class Programme:
    university: str
    programme_name: str
    code: str
    duration: Optional[int]
    schemes: List[str]
    essential: RuleBlock
    relevant: Optional[RuleBlock]
    desirable: Optional[RuleBlock]
    cutoffs: Dict[str, Optional[float]]
    notes: Optional[str] = None


@dataclass
class ProgrammeResult:
    programme: Programme
    weight: float
    eligible: bool
    status: str
    best_scheme: Optional[str] = None
    scheme_statuses: Optional[Dict[str, str]] = None
    matched_subjects: Optional[Dict[str, List[str]]] = None
    reason: Optional[str] = None
