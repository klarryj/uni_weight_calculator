from typing import Optional, Tuple

from core.models import CutoffRecord, StudentProfile
from core.student import is_female


def resolve_cutoff(
    student: StudentProfile,
    cutoff_record: Optional[CutoffRecord],
) -> Tuple[Optional[float], str]:
    """
    Returns:
        (cutoff_value, reason)
    """

    if not cutoff_record:
        return None, "No cutoff record found"

    cutoff_type = cutoff_record.cutoff_type

    # CASE 1 — No cutoff published
    if cutoff_type == "none":
        return None, "No cutoff available for this programme"

    # CASE 2 — Single cutoff
    if cutoff_type == "single":
        return cutoff_record.value, "Single cutoff applied"

    # CASE 3 — Gender split cutoff
    if cutoff_type == "gender_split":
        if is_female(student):
            return cutoff_record.female, "Female cutoff applied"
        else:
            return cutoff_record.male, "Male cutoff applied"

    # CASE 4 — Percentage (special case like LAW)
    if cutoff_type == "percentage_single":
        return cutoff_record.value, "Percentage cutoff applied"

    # CASE 5 — Option-based (rare, e.g. EDA, LIS)
    if cutoff_type == "options":
        return None, "Option-based cutoff — requires specific track selection"

    # Fallback
    return None, f"Unsupported cutoff type: {cutoff_type}"


def get_cutoff_record(
    cutoff_index: dict,
    university: str,
    code: str,
) -> Optional[CutoffRecord]:
    key = (university.lower().strip(), code.upper())
    return cutoff_index.get(key)
