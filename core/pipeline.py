from typing import Dict, List

from core.classification import classify_result
from core.cutoffs import get_cutoff_record, resolve_cutoff
from core.engine import compute_all_programmes
from core.explanations import explain_result
from core.loaders import load_all_data
from core.models import ProgrammeResult, StudentProfile
from core.recommendations import (
    alternative_options,
    group_by_status,
    summary_counts,
    top_recommendations,
)
from core.schemes import attach_scheme_status


def run_full_analysis(student: StudentProfile) -> Dict:
    """
    Full pipeline execution.
    """

    # 1. Load data
    data = load_all_data()

    programmes = data["programmes"]
    subject_rule_index = data["subject_rule_index"]
    cutoff_index = data["cutoff_index"]

    # 2. Compute weights
    results: List[ProgrammeResult] = compute_all_programmes(
        student=student,
        programmes=programmes,
        subject_rule_index=subject_rule_index,
    )

    final_results: List[ProgrammeResult] = []

    # 3. Apply cutoffs + classification + schemes + explanations
    for result in results:
        cutoff_record = get_cutoff_record(
            cutoff_index,
            result.programme.university,
            result.programme.code,
        )

        cutoff_value, cutoff_reason = resolve_cutoff(student, cutoff_record)

        # classify
        result = classify_result(result, cutoff_value)

        # schemes
        result = attach_scheme_status(result, student)

        # explanation
        explanation = explain_result(result, cutoff_value)
        result.reason = explanation

        final_results.append(result)

    # 4. Organize output
    grouped = group_by_status(final_results)
    top = top_recommendations(final_results)
    alternatives = alternative_options(final_results)
    summary = summary_counts(final_results)

    return {
        "all_results": final_results,
        "grouped": grouped,
        "top_recommendations": top,
        "alternatives": alternatives,
        "summary": summary,
        "integrity_report": data.get("integrity_report"),
    }
