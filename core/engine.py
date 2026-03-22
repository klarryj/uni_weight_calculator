from typing import Dict, List, Optional

from core.models import StudentProfile, Programme, ProgrammeResult
from core.eligibility import check_programme_eligibility
from utils.constants import (
    ALEVEL_POINTS,
    OLEVEL_WEIGHTS,
    CLASSIFICATION,
)


def _normalize(text: str) -> str:
    return text.strip().lower()


def _student_subject_points(student: StudentProfile) -> Dict[str, int]:
    return {
        _normalize(subject_grade.subject): ALEVEL_POINTS.get(subject_grade.grade.strip().upper(), 0)
        for subject_grade in student.alevel_subjects
    }


def _sum_subject_points(subjects: List[str], subject_points: Dict[str, int], multiplier: int) -> float:
    return sum(subject_points.get(_normalize(subject), 0) * multiplier for subject in subjects)


def _compute_olevel_weight(student: StudentProfile) -> float:
    return round(
        (student.olevel.distinctions * OLEVEL_WEIGHTS["DISTINCTION"])
        + (student.olevel.credits * OLEVEL_WEIGHTS["CREDIT"])
        + (student.olevel.passes * OLEVEL_WEIGHTS["PASS"]),
        2,
    )


def _compute_bonus_weight(student: StudentProfile) -> float:
    bonus = 0.0

    if student.gender.strip().lower() == "female":
        bonus += 1.5

    # Simple version for now. We can refine GP / Sub-Math handling later.
    if student.general_paper and student.general_paper.strip().upper() != "F":
        bonus += 1.0

    if student.sub_math_or_ict:
        bonus += 0.5

    return bonus


def _classify_against_cutoff(weight: float, cutoff: Optional[float]) -> str:
    if cutoff is None:
        return "NO_DATA"

    margin = weight - cutoff

    if margin >= CLASSIFICATION["SAFE_MARGIN"]:
        return "SAFE"

    if margin >= CLASSIFICATION["BORDERLINE_MARGIN"]:
        return "BORDERLINE"

    return "RISKY"


def _scheme_allowed_for_student(student: StudentProfile, scheme: str) -> bool:
    """
    Basic eligibility by scheme availability.
    We keep this simple in V1.
    """
    scheme = scheme.strip().upper()

    if scheme == "GS":
        return (student.citizenship or "").strip().lower() == "ugandan"

    if scheme == "DQ":
        return bool(student.district) and (student.citizenship or "").strip().lower() == "ugandan"

    if scheme == "PS":
        return True

    # Unknown schemes are treated as visible but not specially restricted.
    return True


def evaluate_programme(student: StudentProfile, programme: Programme) -> ProgrammeResult:
    eligible, matched_subjects, reason = check_programme_eligibility(student, programme)

    if not eligible:
        return ProgrammeResult(
            programme=programme,
            weight=0.0,
            eligible=False,
            status="NOT_ELIGIBLE",
            best_scheme=None,
            scheme_statuses={},
            matched_subjects=matched_subjects,
            reason=reason,
        )

    subject_points = _student_subject_points(student)

    essential_weight = _sum_subject_points(
        matched_subjects["essential"],
        subject_points,
        programme.essential.weight,
    )

    relevant_weight = 0.0
    if programme.relevant:
        relevant_weight = _sum_subject_points(
            matched_subjects["relevant"],
            subject_points,
            programme.relevant.weight,
        )

    desirable_weight = 0.0
    if programme.desirable:
        desirable_weight = _sum_subject_points(
            matched_subjects["desirable"],
            subject_points,
            programme.desirable.weight,
        )

    olevel_weight = _compute_olevel_weight(student)
    bonus_weight = _compute_bonus_weight(student)

    total_weight = round(
        essential_weight + relevant_weight + desirable_weight + olevel_weight + bonus_weight,
        2,
    )

    scheme_statuses: Dict[str, str] = {}
    best_scheme = None
    best_priority = -1

    # Priority ranking for selecting the "best" visible scheme status
    status_priority = {
        "SAFE": 4,
        "BORDERLINE": 3,
        "RISKY": 2,
        "NO_DATA": 1,
        "UNAVAILABLE": 0,
    }

    for scheme in programme.schemes:
        scheme_code = scheme.strip().upper()

        if not _scheme_allowed_for_student(student, scheme_code):
            scheme_statuses[scheme_code] = "UNAVAILABLE"
            continue

        cutoff = programme.cutoffs.get(scheme_code)
        scheme_status = _classify_against_cutoff(total_weight, cutoff)
        scheme_statuses[scheme_code] = scheme_status

        if status_priority[scheme_status] > best_priority:
            best_priority = status_priority[scheme_status]
            best_scheme = scheme_code

    final_status = scheme_statuses.get(best_scheme, "NO_DATA") if best_scheme else "NO_DATA"

    return ProgrammeResult(
        programme=programme,
        weight=total_weight,
        eligible=True,
        status=final_status,
        best_scheme=best_scheme,
        scheme_statuses=scheme_statuses,
        matched_subjects=matched_subjects,
        reason="Eligible and evaluated successfully",
    )


def evaluate_programmes(student: StudentProfile, programmes: List[Programme]) -> List[ProgrammeResult]:
    results = [evaluate_programme(student, programme) for programme in programmes]

    status_rank = {
        "SAFE": 4,
        "BORDERLINE": 3,
        "RISKY": 2,
        "NO_DATA": 1,
        "NOT_ELIGIBLE": 0,
    }

    results.sort(
        key=lambda result: (
            status_rank.get(result.status, -1),
            result.weight,
            result.programme.programme_name.lower(),
        ),
        reverse=True,
    )
    return results
