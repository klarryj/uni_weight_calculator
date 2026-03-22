from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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
    type: str
    subjects: Optional[List[str]] = None
    count: Optional[int] = None
    weight: int = 0
    subject_sets: Optional[List[List[str]]] = None
    min_count: Optional[int] = None
    max_count: Optional[int] = None
    source_text: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Programme:
    university: str
    code: str
    programme_name: str
    duration_years: Optional[int]
    level: Optional[str]
    schemes: List[str]
    has_cutoff_2025_2026: bool = False


@dataclass
class CutoffRecord:
    university: str
    code: str
    academic_year: str
    cutoff_type: str
    value: Optional[float] = None
    female: Optional[float] = None
    male: Optional[float] = None
    options: Optional[Dict[str, Any]] = None


@dataclass
class SubjectRule:
    university: str
    code: str
    programme_name: str
    essential: Optional[RuleBlock]
    relevant: Optional[RuleBlock]
    desirable: Optional[RuleBlock]
    raw_essential_text: Optional[str] = None
    raw_relevant_text: Optional[str] = None
    raw_desirable_text: Optional[str] = None
    source_pages: List[int] = field(default_factory=list)
    match_confidence: Optional[str] = None
    normalization_status: Optional[str] = None
    special_requirements: List[str] = field(default_factory=list)


@dataclass
class University:
    name: str
    short_code: str
    display_order: int


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
