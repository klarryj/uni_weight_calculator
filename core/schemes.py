from typing import Dict, List

from core.models import Programme, ProgrammeResult, StudentProfile
from core.student import is_ugandan


def scheme_allowed(student: StudentProfile, scheme: str) -> bool:
    scheme = scheme.upper().strip()

    if scheme == "GS":
        return is_ugandan(student)

    if scheme == "DQ":
        return is_ugandan(student) and bool(student.district)

    if scheme == "PS":
        return True

    return True  # fallback


def get_available_schemes(student: StudentProfile, programme: Programme) -> List[str]:
    return [
        scheme for scheme in programme.schemes
        if scheme_allowed(student, scheme)
    ]


def attach_scheme_status(
    result: ProgrammeResult,
    student: StudentProfile,
) -> ProgrammeResult:
    """
    Assign scheme-level visibility and status.
    """

    scheme_statuses: Dict[str, str] = {}

    for scheme in result.programme.schemes:
        if not scheme_allowed(student, scheme):
            scheme_statuses[scheme] = "UNAVAILABLE"
        else:
            # for now, same classification applies to all schemes
            scheme_statuses[scheme] = result.status

    result.scheme_statuses = scheme_statuses

    # Determine best scheme (simple version)
    priority = ["SAFE", "BORDERLINE", "RISKY", "NO_CUTOFF", "UNAVAILABLE"]

    best_scheme = None
    best_rank = -1

    for scheme, status in scheme_statuses.items():
        if status not in priority:
            continue

        rank = priority.index(status)
        if best_scheme is None or rank < best_rank:
            best_scheme = scheme
            best_rank = rank

    result.best_scheme = best_scheme

    return result
