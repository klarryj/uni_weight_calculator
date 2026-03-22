from typing import Dict, List

from core.models import ProgrammeResult


STATUS_PRIORITY = {
    "SAFE": 5,
    "BORDERLINE": 4,
    "RISKY": 3,
    "NO_CUTOFF": 2,
    "NOT_ELIGIBLE": 1,
}


def sort_results(results: List[ProgrammeResult]) -> List[ProgrammeResult]:
    """
    Sort results by:
    1. Status priority
    2. Weight (descending)
    """

    return sorted(
        results,
        key=lambda r: (
            STATUS_PRIORITY.get(r.status, 0),
            r.weight,
        ),
        reverse=True,
    )


def group_by_status(results: List[ProgrammeResult]) -> Dict[str, List[ProgrammeResult]]:
    grouped = {
        "SAFE": [],
        "BORDERLINE": [],
        "RISKY": [],
        "NO_CUTOFF": [],
        "NOT_ELIGIBLE": [],
    }

    for result in results:
        grouped.setdefault(result.status, []).append(result)

    return grouped


def top_recommendations(
    results: List[ProgrammeResult],
    limit: int = 10,
    include_borderline: bool = True,
) -> List[ProgrammeResult]:
    """
    Returns top recommended programmes.
    """

    sorted_results = sort_results(results)

    selected = []

    for result in sorted_results:
        if result.status == "SAFE":
            selected.append(result)
        elif include_borderline and result.status == "BORDERLINE":
            selected.append(result)

        if len(selected) >= limit:
            break

    return selected


def alternative_options(
    results: List[ProgrammeResult],
    limit: int = 10,
) -> List[ProgrammeResult]:
    """
    Returns backup options (borderline + risky).
    """

    sorted_results = sort_results(results)

    alternatives = [
        r for r in sorted_results
        if r.status in ("BORDERLINE", "RISKY")
    ]

    return alternatives[:limit]


def filter_eligible(results: List[ProgrammeResult]) -> List[ProgrammeResult]:
    return [r for r in results if r.eligible]


def summary_counts(results: List[ProgrammeResult]) -> Dict[str, int]:
    summary = {
        "total": len(results),
        "safe": 0,
        "borderline": 0,
        "risky": 0,
        "no_cutoff": 0,
        "not_eligible": 0,
    }

    for r in results:
        if r.status == "SAFE":
            summary["safe"] += 1
        elif r.status == "BORDERLINE":
            summary["borderline"] += 1
        elif r.status == "RISKY":
            summary["risky"] += 1
        elif r.status == "NO_CUTOFF":
            summary["no_cutoff"] += 1
        elif r.status == "NOT_ELIGIBLE":
            summary["not_eligible"] += 1

    return summary
