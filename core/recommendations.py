from typing import Dict, List

from core.models import ProgrammeResult


def group_results_by_status(results: List[ProgrammeResult]) -> Dict[str, List[ProgrammeResult]]:
    grouped = {
        "SAFE": [],
        "BORDERLINE": [],
        "RISKY": [],
        "NO_DATA": [],
        "NOT_ELIGIBLE": [],
    }

    for result in results:
        grouped.setdefault(result.status, []).append(result)

    return grouped


def filter_eligible_results(results: List[ProgrammeResult]) -> List[ProgrammeResult]:
    return [result for result in results if result.eligible]


def filter_results_by_university(results: List[ProgrammeResult], university: str) -> List[ProgrammeResult]:
    target = university.strip().lower()
    return [
        result for result in results
        if result.programme.university.strip().lower() == target
    ]


def filter_results_by_scheme(results: List[ProgrammeResult], scheme: str) -> List[ProgrammeResult]:
    target = scheme.strip().upper()
    filtered = []

    for result in results:
        if target in (result.programme.schemes or []):
            filtered.append(result)

    return filtered


def top_results(results: List[ProgrammeResult], limit: int = 10, eligible_only: bool = True) -> List[ProgrammeResult]:
    working = filter_eligible_results(results) if eligible_only else results
    return working[:limit]


def recommendation_summary(results: List[ProgrammeResult]) -> Dict[str, int]:
    summary = {
        "total": len(results),
        "eligible": 0,
        "safe": 0,
        "borderline": 0,
        "risky": 0,
        "no_data": 0,
        "not_eligible": 0,
    }

    for result in results:
        if result.eligible:
            summary["eligible"] += 1

        if result.status == "SAFE":
            summary["safe"] += 1
        elif result.status == "BORDERLINE":
            summary["borderline"] += 1
        elif result.status == "RISKY":
            summary["risky"] += 1
        elif result.status == "NO_DATA":
            summary["no_data"] += 1
        elif result.status == "NOT_ELIGIBLE":
            summary["not_eligible"] += 1

    return summary
