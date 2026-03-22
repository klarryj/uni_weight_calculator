from typing import Optional

from core.models import ProgrammeResult
from utils.constants import CLASSIFICATION


def classify_result(
    result: ProgrammeResult,
    cutoff: Optional[float],
) -> ProgrammeResult:
    """
    Updates ProgrammeResult with status based on cutoff comparison.
    """

    # Case 1 — Already not eligible
    if not result.eligible:
        result.status = "NOT_ELIGIBLE"
        return result

    # Case 2 — No cutoff available
    if cutoff is None:
        result.status = "NO_CUTOFF"
        return result

    # Compute margin
    margin = result.weight - cutoff

    # SAFE
    if margin >= CLASSIFICATION["SAFE_MARGIN"]:
        result.status = "SAFE"
        return result

    # BORDERLINE
    if margin >= CLASSIFICATION["BORDERLINE_MARGIN"]:
        result.status = "BORDERLINE"
        return result

    # Otherwise → RISKY
    result.status = "RISKY"
    return result
