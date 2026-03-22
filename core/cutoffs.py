from typing import Dict, List

from core.models import Programme, ProgrammeResult, StudentProfile, SubjectRule
from core.rule_executor import execute_programme_rules
from core.student import get_subject_grade, is_female
from utils.constants import ALEVEL_POINTS, OLEVEL_WEIGHTS


def _subject_points(student: StudentProfile, subject: str) -> int:
    grade = get_subject_grade(student, subject)
    if not grade:
        return 0
    return ALEVEL_POINTS.get(grade.upper(), 0)


def _compute_bucket_weight(student: StudentProfile, subjects: List[str], multiplier: int) -> float:
    return sum(_subject_points(student, subject) * multiplier for subject in subjects)


def _compute_olevel_weight(student: StudentProfile) -> float:
    return (
        student.olevel.distinctions * OLEVEL_WEIGHTS["DISTINCTION"]
        + student.olevel.credits * OLEVEL_WEIGHTS["CREDIT"]
        + student.olevel.passes * OLEVEL_WEIGHTS["PASS"]
    )


def _compute_bonus(student: StudentProfile) -> float:
    bonus = 0.0

    if is_female(student):
        bonus += 1.5

    if student.general_paper and student.general_paper.upper() != "F":
        bonus += 1.0

    if student.sub_math_or_ict:
        bonus += 0.5

    return bonus


def compute_programme_weight(
    student: StudentProfile,
    programme: Programme,
    subject_rule: SubjectRule,
) -> ProgrammeResult:
    rule_result = execute_programme_rules(student, subject_rule)

    if not rule_result.eligible:
        return ProgrammeResult(
            programme=programme,
            weight=0.0,
            eligible=False,
            status="NOT_ELIGIBLE",
            matched_subjects=rule_result.matched_subjects,
            reason=rule_result.reason,
        )

    essential_subjects = rule_result.matched_subjects["essential"]
    relevant_subjects = rule_result.matched_subjects["relevant"]
    desirable_subjects = rule_result.matched_subjects["desirable"]

    essential_weight = _compute_bucket_weight(student, essential_subjects, 3)
    relevant_weight = _compute_bucket_weight(student, relevant_subjects, 2)
    desirable_weight = _compute_bucket_weight(student, desirable_subjects, 1)

    olevel_weight = _compute_olevel_weight(student)
    bonus = _compute_bonus(student)

    total_weight = round(
        essential_weight
        + relevant_weight
        + desirable_weight
        + olevel_weight
        + bonus,
        2,
    )

    return ProgrammeResult(
        programme=programme,
        weight=total_weight,
        eligible=True,
        status="PENDING",  # classification comes later
        matched_subjects=rule_result.matched_subjects,
        reason="Weight computed successfully",
    )


def compute_all_programmes(
    student: StudentProfile,
    programmes: List[Programme],
    subject_rule_index: Dict,
) -> List[ProgrammeResult]:
    results: List[ProgrammeResult] = []

    for programme in programmes:
        key = (programme.university.lower().strip(), programme.code.upper())

        subject_rule = subject_rule_index.get(key)

        if not subject_rule:
            results.append(
                ProgrammeResult(
                    programme=programme,
                    weight=0.0,
                    eligible=False,
                    status="NO_RULE",
                    reason="No subject rule found",
                )
            )
            continue

        result = compute_programme_weight(student, programme, subject_rule)
        results.append(result)

    return results
