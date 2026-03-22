from typing import List, Tuple, Dict, Set

from core.models import StudentProfile, RuleBlock


def _normalize(text: str) -> str:
    return text.strip().lower()


def _student_subject_map(student: StudentProfile) -> Dict[str, str]:
    """
    Returns a normalized subject -> grade map.
    """
    return {
        _normalize(subject_grade.subject): subject_grade.grade.strip().upper()
        for subject_grade in student.alevel_subjects
    }


def _available_subjects(student: StudentProfile) -> Set[str]:
    return set(_student_subject_map(student).keys())


def check_rule_eligibility(
    student: StudentProfile,
    rule: RuleBlock,
    used_subjects: Set[str] | None = None,
) -> Tuple[bool, List[str], str]:
    """
    Returns:
        eligible: bool
        matched_subjects: list[str]  (normalized subject names)
        reason: str
    """
    if used_subjects is None:
        used_subjects = set()

    subject_map = _student_subject_map(student)
    available = set(subject_map.keys()) - used_subjects

    rule_type = rule.type.strip().lower()
    rule_subjects = [_normalize(s) for s in (rule.subjects or [])]
    count = rule.count or 0

    if rule_type == "fixed":
        missing = [s for s in rule_subjects if s not in available]
        if missing:
            return False, [], f"Missing required subject(s): {', '.join(missing)}"
        return True, rule_subjects, "All fixed subjects matched"

    if rule_type == "best_of":
        matches = [s for s in rule_subjects if s in available]
        if len(matches) < count:
            return False, [], f"Requires at least {count} subject(s) from allowed list"
        return True, matches[:count], "Best-of rule satisfied"

    if rule_type == "optional":
        matches = [s for s in rule_subjects if s in available]
        return True, matches[:count] if count else matches, "Optional rule processed"

    if rule_type == "remaining_best":
        matches = list(available)
        if len(matches) < count:
            return False, [], f"Requires at least {count} remaining subject(s)"
        return True, matches[:count], "Remaining-best rule satisfied"

    if rule_type == "and_or":
        matches = [s for s in rule_subjects if s in available]
        if len(matches) < 1:
            return False, [], f"Requires at least one of: {', '.join(rule_subjects)}"
        # current version picks one; later we can make this smarter
        return True, matches[:1], "And/or rule satisfied"

    return False, [], f"Unsupported rule type: {rule.type}"


def check_programme_eligibility(student: StudentProfile, programme) -> Tuple[bool, Dict[str, List[str]], str]:
    """
    Checks essential and relevant rules for academic eligibility.
    Desirable is not used to reject the candidate.
    """
    used_subjects: Set[str] = set()
    matched: Dict[str, List[str]] = {
        "essential": [],
        "relevant": [],
        "desirable": [],
    }

    essential_ok, essential_matches, essential_reason = check_rule_eligibility(
        student, programme.essential, used_subjects
    )
    if not essential_ok:
        return False, matched, essential_reason

    matched["essential"] = essential_matches
    used_subjects.update(essential_matches)

    if programme.relevant:
        relevant_ok, relevant_matches, relevant_reason = check_rule_eligibility(
            student, programme.relevant, used_subjects
        )
        if not relevant_ok:
            return False, matched, relevant_reason
        matched["relevant"] = relevant_matches
        used_subjects.update(relevant_matches)

    if programme.desirable:
        desirable_ok, desirable_matches, _ = check_rule_eligibility(
            student, programme.desirable, used_subjects
        )
        if desirable_ok:
            matched["desirable"] = desirable_matches

    return True, matched, "Eligible"
