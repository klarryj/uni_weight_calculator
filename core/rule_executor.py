from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from core.models import RuleBlock, StudentProfile, SubjectRule
from core.student import get_subject_grade, student_subject_names
from utils.constants import ALEVEL_POINTS


@dataclass
class RuleExecutionResult:
    eligible: bool
    matched_subjects: Dict[str, List[str]]
    reason: str


def _subject_points(student: StudentProfile, subject_name: str) -> int:
    grade = get_subject_grade(student, subject_name)
    if not grade:
        return -1
    return ALEVEL_POINTS.get(grade.upper(), -1)


def _sort_subjects_by_points(student: StudentProfile, subjects: List[str]) -> List[str]:
    unique_subjects = []
    seen = set()

    for subject in subjects:
        if subject not in seen:
            unique_subjects.append(subject)
            seen.add(subject)

    return sorted(
        unique_subjects,
        key=lambda subject: (_subject_points(student, subject), subject),
        reverse=True,
    )


def _available_student_subjects(student: StudentProfile, used_subjects: Optional[Set[str]] = None) -> List[str]:
    used_subjects = used_subjects or set()
    return [subject for subject in student_subject_names(student) if subject not in used_subjects]


def _match_fixed(student: StudentProfile, rule: RuleBlock, used_subjects: Set[str]) -> Tuple[bool, List[str], str]:
    required = rule.subjects or []
    available = set(_available_student_subjects(student, used_subjects))

    missing = [subject for subject in required if subject not in available]
    if missing:
        return False, [], f"Missing required subject(s): {', '.join(missing)}"

    return True, required[:], "Fixed rule satisfied"


def _match_best_of(student: StudentProfile, rule: RuleBlock, used_subjects: Set[str]) -> Tuple[bool, List[str], str]:
    allowed = rule.subjects or []
    count = rule.count or 0
    available = set(_available_student_subjects(student, used_subjects))

    matches = [subject for subject in allowed if subject in available]
    ranked = _sort_subjects_by_points(student, matches)

    if len(ranked) < count:
        return False, [], f"Requires at least {count} subject(s) from allowed list"

    return True, ranked[:count], "Best-of rule satisfied"


def _match_optional(student: StudentProfile, rule: RuleBlock, used_subjects: Set[str]) -> Tuple[bool, List[str], str]:
    allowed = rule.subjects or []
    count = rule.count or len(allowed)
    available = set(_available_student_subjects(student, used_subjects))

    matches = [subject for subject in allowed if subject in available]
    ranked = _sort_subjects_by_points(student, matches)

    return True, ranked[:count], "Optional rule processed"


def _match_remaining_best(student: StudentProfile, rule: RuleBlock, used_subjects: Set[str]) -> Tuple[bool, List[str], str]:
    count = rule.count or 0
    available = _available_student_subjects(student, used_subjects)
    ranked = _sort_subjects_by_points(student, available)

    if len(ranked) < count:
        return False, [], f"Requires at least {count} remaining subject(s)"

    return True, ranked[:count], "Remaining-best rule satisfied"


def _match_and_or(student: StudentProfile, rule: RuleBlock, used_subjects: Set[str]) -> Tuple[bool, List[str], str]:
    allowed = rule.subjects or []
    min_count = rule.min_count or 1
    max_count = rule.max_count or 1
    available = set(_available_student_subjects(student, used_subjects))

    matches = [subject for subject in allowed if subject in available]
    ranked = _sort_subjects_by_points(student, matches)

    if len(ranked) < min_count:
        return False, [], f"Requires at least {min_count} of: {', '.join(allowed)}"

    selected = ranked[:max_count]
    return True, selected, "And/or rule satisfied"


def _match_fixed_plus_best_of(student: StudentProfile, rule: RuleBlock, used_subjects: Set[str]) -> Tuple[bool, List[str], str]:
    """
    Expected structure:
    {
      "type": "fixed_plus_best_of",
      "subjects": ["Mathematics"],   # fixed
      "extra": {
        "best_of_subjects": [...],
        "best_of_count": 1
      }
    }
    """
    fixed_subjects = rule.subjects or []
    available = set(_available_student_subjects(student, used_subjects))

    missing = [subject for subject in fixed_subjects if subject not in available]
    if missing:
        return False, [], f"Missing fixed subject(s): {', '.join(missing)}"

    temp_used = set(used_subjects)
    temp_used.update(fixed_subjects)

    best_of_subjects = rule.extra.get("best_of_subjects", [])
    best_of_count = int(rule.extra.get("best_of_count", 0) or 0)

    best_candidates = [subject for subject in best_of_subjects if subject in _available_student_subjects(student, temp_used)]
    ranked = _sort_subjects_by_points(student, best_candidates)

    if len(ranked) < best_of_count:
        return False, [], f"Requires at least {best_of_count} additional subject(s) from allowed list"

    selected = fixed_subjects + ranked[:best_of_count]
    return True, selected, "Fixed-plus-best-of rule satisfied"


def _match_all_subjects_best(student: StudentProfile, rule: RuleBlock, used_subjects: Set[str]) -> Tuple[bool, List[str], str]:
    count = rule.count or 0
    available = _available_student_subjects(student, used_subjects)
    ranked = _sort_subjects_by_points(student, available)

    if len(ranked) < count:
        return False, [], f"Requires at least {count} subject(s) from all A-Level subjects"

    return True, ranked[:count], "All-subjects-best rule satisfied"


def _match_essential_set_remaining(
    student: StudentProfile,
    rule: RuleBlock,
    used_subjects: Set[str],
    essential_matches: List[str],
) -> Tuple[bool, List[str], str]:
    """
    For cases like 'Third better done of the essential set'
    """
    count = rule.count or 1
    candidate_set = [subject for subject in essential_matches if subject not in used_subjects]
    ranked = _sort_subjects_by_points(student, candidate_set)

    if len(ranked) < count:
        return False, [], f"Requires at least {count} remaining subject(s) from essential set"

    return True, ranked[:count], "Essential-set-remaining rule satisfied"


def execute_rule(
    student: StudentProfile,
    rule: Optional[RuleBlock],
    used_subjects: Optional[Set[str]] = None,
    essential_matches: Optional[List[str]] = None,
) -> Tuple[bool, List[str], str]:
    if rule is None:
        return True, [], "No rule provided"

    used_subjects = used_subjects or set()
    essential_matches = essential_matches or []

    rule_type = (rule.type or "").strip().lower()

    if rule_type == "fixed":
        return _match_fixed(student, rule, used_subjects)

    if rule_type == "best_of":
        return _match_best_of(student, rule, used_subjects)

    if rule_type == "optional":
        return _match_optional(student, rule, used_subjects)

    if rule_type == "remaining_best":
        return _match_remaining_best(student, rule, used_subjects)

    if rule_type == "and_or":
        return _match_and_or(student, rule, used_subjects)

    if rule_type == "fixed_plus_best_of":
        return _match_fixed_plus_best_of(student, rule, used_subjects)

    if rule_type == "all_subjects_best":
        return _match_all_subjects_best(student, rule, used_subjects)

    if rule_type == "essential_set_remaining":
        return _match_essential_set_remaining(student, rule, used_subjects, essential_matches)

    return False, [], f"Unsupported rule type: {rule.type}"


def execute_programme_rules(student: StudentProfile, subject_rule: SubjectRule) -> RuleExecutionResult:
    matched_subjects = {
        "essential": [],
        "relevant": [],
        "desirable": [],
    }
    used_subjects: Set[str] = set()

    essential_ok, essential_matches, essential_reason = execute_rule(
        student=student,
        rule=subject_rule.essential,
        used_subjects=used_subjects,
    )
    if not essential_ok:
        return RuleExecutionResult(
            eligible=False,
            matched_subjects=matched_subjects,
            reason=essential_reason,
        )

    matched_subjects["essential"] = essential_matches
    used_subjects.update(essential_matches)

    relevant_ok, relevant_matches, relevant_reason = execute_rule(
        student=student,
        rule=subject_rule.relevant,
        used_subjects=used_subjects,
        essential_matches=essential_matches,
    )
    if not relevant_ok:
        return RuleExecutionResult(
            eligible=False,
            matched_subjects=matched_subjects,
            reason=relevant_reason,
        )

    matched_subjects["relevant"] = relevant_matches
    used_subjects.update(relevant_matches)

    desirable_ok, desirable_matches, _ = execute_rule(
        student=student,
        rule=subject_rule.desirable,
        used_subjects=used_subjects,
        essential_matches=essential_matches,
    )
    if desirable_ok:
        matched_subjects["desirable"] = desirable_matches

    return RuleExecutionResult(
        eligible=True,
        matched_subjects=matched_subjects,
        reason="Programme rules executed successfully",
    )
