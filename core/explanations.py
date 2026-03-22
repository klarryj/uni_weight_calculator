from typing import Optional

from core.models import ProgrammeResult


def _format_subjects(subjects: list[str]) -> str:
    if not subjects:
        return "-"
    return ", ".join(subjects)


def explain_result(
    result: ProgrammeResult,
    cutoff: Optional[float],
) -> str:
    """
    Generates a human-readable explanation for a result.
    """

    # Case 1 — Not eligible
    if not result.eligible:
        return f"Not eligible: {result.reason}"

    lines = []

    # Programme info
    lines.append(f"{result.programme.programme_name} ({result.programme.university})")

    # Subjects used
    matched = result.matched_subjects or {}
    lines.append(
        f"Subjects used → "
        f"Essential: {_format_subjects(matched.get('essential', []))} | "
        f"Relevant: {_format_subjects(matched.get('relevant', []))} | "
        f"Desirable: {_format_subjects(matched.get('desirable', []))}"
    )

    # Weight
    lines.append(f"Computed weight: {result.weight}")

    # Cutoff
    if cutoff is None:
        lines.append("No cutoff available for this programme.")
    else:
        lines.append(f"Cutoff: {cutoff}")

        margin = round(result.weight - cutoff, 2)
        lines.append(f"Margin: {margin}")

    # Status
    if result.status == "SAFE":
        lines.append("You are highly competitive for this programme.")
    elif result.status == "BORDERLINE":
        lines.append("You have a fair chance; admission is uncertain.")
    elif result.status == "RISKY":
        lines.append("Chances are low based on previous cutoffs.")
    elif result.status == "NO_CUTOFF":
        lines.append("No cutoff available — cannot determine competitiveness.")
    elif result.status == "NOT_ELIGIBLE":
        lines.append("You do not meet the subject requirements.")

    # Scheme
    if result.best_scheme:
        lines.append(f"Best pathway: {result.best_scheme}")

    return "\n".join(lines)
