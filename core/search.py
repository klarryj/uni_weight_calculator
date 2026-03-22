from typing import List

from core.models import Programme, ProgrammeResult


def search_programmes(programmes: List[Programme], query: str) -> List[Programme]:
    q = query.strip().lower()
    if not q:
        return programmes

    matches = []
    for programme in programmes:
        haystack = " ".join([
            programme.programme_name,
            programme.university,
            programme.code,
            programme.notes or "",
        ]).lower()

        if q in haystack:
            matches.append(programme)

    return matches


def search_results(results: List[ProgrammeResult], query: str) -> List[ProgrammeResult]:
    q = query.strip().lower()
    if not q:
        return results

    matches = []
    for result in results:
        haystack = " ".join([
            result.programme.programme_name,
            result.programme.university,
            result.programme.code,
            result.programme.notes or "",
            result.status,
            result.best_scheme or "",
        ]).lower()

        if q in haystack:
            matches.append(result)

    return matches
