from typing import Dict, List

from core.models import ProgrammeResult
from utils.constants import SCHEME_LABELS


def format_scheme_badges(schemes: List[str]) -> str:
    if not schemes:
        return ""

    return " ".join([f"[{scheme.upper()}]" for scheme in schemes])


def format_scheme_statuses(scheme_statuses: Dict[str, str] | None) -> str:
    if not scheme_statuses:
        return "-"

    parts = []
    for scheme, status in scheme_statuses.items():
        parts.append(f"{scheme}: {status}")
    return " | ".join(parts)


def format_matched_subjects(result: ProgrammeResult) -> str:
    if not result.matched_subjects:
        return "-"

    parts = []
    for bucket in ["essential", "relevant", "desirable"]:
        values = result.matched_subjects.get(bucket, [])
        if values:
            pretty = ", ".join([value.title() for value in values])
            parts.append(f"{bucket.title()}: {pretty}")

    return " | ".join(parts) if parts else "-"


def explain_scheme_labels() -> str:
    parts = []
    for code, meaning in SCHEME_LABELS.items():
        parts.append(f"{code} = {meaning}")
    return " • ".join(parts)
