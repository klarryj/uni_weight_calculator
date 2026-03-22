from typing import Dict, List, Tuple

from core.models import StudentProfile, SubjectRule
from core.rule_executor import execute_programme_rules


def check_programme_eligibility(
    student: StudentProfile,
    subject_rule: SubjectRule,
) -> Tuple[bool, Dict[str, List[str]], str]:
    result = execute_programme_rules(student, subject_rule)
    return result.eligible, result.matched_subjects, result.reason
