from typing import Iterable, List, Optional

from utils.constants import (
    CANONICAL_SUBJECTS,
    CITIZENSHIP_ALIASES,
    GENDER_ALIASES,
    GRADE_ALIASES,
    SUBJECT_ALIASES,
)


def _clean(text: str) -> str:
    return " ".join(text.strip().lower().split())


def normalize_subject_name(subject: Optional[str]) -> Optional[str]:
    if not subject:
        return None

    cleaned = _clean(subject)
    return SUBJECT_ALIASES.get(cleaned, subject.strip().title())


def normalize_subject_list(subjects: Optional[Iterable[str]]) -> List[str]:
    if not subjects:
        return []

    normalized = []
    seen = set()

    for subject in subjects:
        value = normalize_subject_name(subject)
        if value and value not in seen:
            normalized.append(value)
            seen.add(value)

    return normalized


def normalize_grade(grade: Optional[str]) -> Optional[str]:
    if grade is None:
        return None

    cleaned = grade.strip()
    return GRADE_ALIASES.get(cleaned, GRADE_ALIASES.get(cleaned.upper()))


def normalize_gender(gender: Optional[str]) -> Optional[str]:
    if not gender:
        return None

    cleaned = _clean(gender)
    return GENDER_ALIASES.get(cleaned, gender.strip().title())


def normalize_citizenship(citizenship: Optional[str]) -> Optional[str]:
    if not citizenship:
        return None

    cleaned = _clean(citizenship)
    return CITIZENSHIP_ALIASES.get(cleaned, citizenship.strip().title())


def normalize_text_list(values: Optional[Iterable[str]]) -> List[str]:
    if not values:
        return []

    return [value.strip() for value in values if value and value.strip()]


def subject_in_list(subject: str, allowed_subjects: Iterable[str]) -> bool:
    normalized_subject = normalize_subject_name(subject)
    normalized_allowed = set(normalize_subject_list(allowed_subjects))
    return normalized_subject in normalized_allowed


def canonical_subjects() -> List[str]:
    return CANONICAL_SUBJECTS[:]
