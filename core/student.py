from typing import Dict, List, Tuple

from core.models import OLevelSummary, StudentProfile, SubjectGrade
from core.normalization import (
    normalize_citizenship,
    normalize_gender,
    normalize_grade,
    normalize_subject_name,
)


def _clean_int(value, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return max(int(value), 0)
    except (TypeError, ValueError):
        return default


def build_student_profile(
    gender: str,
    alevel_subjects: List[dict],
    general_paper: str | None,
    sub_math_or_ict: bool,
    distinctions: int,
    credits: int,
    passes: int,
    district: str | None = None,
    citizenship: str | None = "Ugandan",
) -> StudentProfile:
    """
    Convert raw UI-like inputs into a normalized StudentProfile.
    """
    normalized_subjects: List[SubjectGrade] = []
    seen_subjects = set()

    for item in alevel_subjects:
        raw_subject = item.get("subject")
        raw_grade = item.get("grade")

        subject = normalize_subject_name(raw_subject)
        grade = normalize_grade(raw_grade)

        if not subject or not grade:
            continue

        if subject in seen_subjects:
            continue

        normalized_subjects.append(SubjectGrade(subject=subject, grade=grade))
        seen_subjects.add(subject)

    student = StudentProfile(
        gender=normalize_gender(gender) or "Male",
        alevel_subjects=normalized_subjects,
        general_paper=normalize_grade(general_paper) if general_paper else None,
        sub_math_or_ict=bool(sub_math_or_ict),
        olevel=OLevelSummary(
            distinctions=_clean_int(distinctions),
            credits=_clean_int(credits),
            passes=_clean_int(passes),
        ),
        district=(district or "").strip() or None,
        citizenship=normalize_citizenship(citizenship) or "Ugandan",
    )

    return student


def validate_student_profile(student: StudentProfile) -> Dict[str, List[str]]:
    """
    Returns validation messages without throwing.
    This is better for Streamlit UX.
    """
    issues = {
        "errors": [],
        "warnings": [],
    }

    if len(student.alevel_subjects) < 3:
        issues["errors"].append("At least 3 principal A-Level subjects are required.")

    subject_names = [item.subject for item in student.alevel_subjects]
    if len(subject_names) != len(set(subject_names)):
        issues["errors"].append("Duplicate A-Level subjects detected.")

    for item in student.alevel_subjects:
        if not item.grade:
            issues["errors"].append(f"Missing grade for subject: {item.subject}")

    total_olevel = (
        student.olevel.distinctions
        + student.olevel.credits
        + student.olevel.passes
    )
    if total_olevel == 0:
        issues["warnings"].append("No O-Level summary entered.")

    if not student.district:
        issues["warnings"].append("District not provided. District Quota interpretation may be limited.")

    if student.citizenship != "Ugandan":
        issues["warnings"].append("Government sponsorship and district quota may not apply for non-Ugandan candidates.")

    return issues


def student_subject_map(student: StudentProfile) -> Dict[str, str]:
    """
    Returns canonical subject -> grade.
    Example:
        {"Mathematics": "A", "Physics": "B", "Economics": "C"}
    """
    return {item.subject: item.grade for item in student.alevel_subjects}


def student_subject_names(student: StudentProfile) -> List[str]:
    return [item.subject for item in student.alevel_subjects]


def has_subject(student: StudentProfile, subject_name: str) -> bool:
    normalized = normalize_subject_name(subject_name)
    return normalized in student_subject_names(student)


def get_subject_grade(student: StudentProfile, subject_name: str) -> str | None:
    normalized = normalize_subject_name(subject_name)
    for item in student.alevel_subjects:
        if item.subject == normalized:
            return item.grade
    return None


def is_female(student: StudentProfile) -> bool:
    return student.gender == "Female"


def is_ugandan(student: StudentProfile) -> bool:
    return student.citizenship == "Ugandan"
