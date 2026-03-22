import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from core.models import CutoffRecord, Programme, RuleBlock, SubjectRule, University


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

UNIVERSITIES_FILE = DATA_DIR / "universities.json"
PROGRAMMES_FILE = DATA_DIR / "programmes.json"
CUTOFFS_FILE = DATA_DIR / "cutoffs_2025_2026.json"
SUBJECT_RULES_FILE = DATA_DIR / "subject_rules.json"


def _clean_str(value: Any, upper: bool = False, lower: bool = False) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if not text or text.lower() in {"nan", "none", "null"}:
        return ""

    if upper:
        return text.upper()

    if lower:
        return text.lower()

    return text


def _clean_list_of_str(values: Any, upper: bool = False, lower: bool = False) -> List[str]:
    if not values:
        return []

    if not isinstance(values, list):
        values = [values]

    cleaned: List[str] = []
    for value in values:
        text = _clean_str(value, upper=upper, lower=lower)
        if text:
            cleaned.append(text)

    return cleaned


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing required data file: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _normalize_key(text: str) -> str:
    return " ".join(_clean_str(text, lower=True).split())


def make_programme_key(university: str, code: str) -> Tuple[str, str]:
    return (_normalize_key(university), _clean_str(code, upper=True))


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or _clean_str(value) == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _build_rule_block(data: Dict[str, Any] | None) -> RuleBlock | None:
    if not data or not isinstance(data, dict):
        return None

    known_keys = {
        "type",
        "subjects",
        "count",
        "weight",
        "subject_sets",
        "min_count",
        "max_count",
        "source_text",
    }
    extra = {key: value for key, value in data.items() if key not in known_keys}

    subjects = data.get("subjects")
    if isinstance(subjects, list):
        subjects = _clean_list_of_str(subjects)
    elif subjects is not None:
        subjects = [_clean_str(subjects)] if _clean_str(subjects) else None
    else:
        subjects = None

    subject_sets = data.get("subject_sets")
    if isinstance(subject_sets, list):
        cleaned_sets = []
        for subject_set in subject_sets:
            if isinstance(subject_set, list):
                cleaned = _clean_list_of_str(subject_set)
                if cleaned:
                    cleaned_sets.append(cleaned)
            elif isinstance(subject_set, dict):
                cleaned_dict = {}
                for key, value in subject_set.items():
                    if isinstance(value, list):
                        cleaned_dict[key] = _clean_list_of_str(value)
                    else:
                        cleaned_dict[key] = value
                cleaned_sets.append(cleaned_dict)
            else:
                cleaned = _clean_str(subject_set)
                if cleaned:
                    cleaned_sets.append(cleaned)
        subject_sets = cleaned_sets or None
    else:
        subject_sets = None

    return RuleBlock(
        type=_clean_str(data.get("type")),
        subjects=subjects,
        count=data.get("count"),
        weight=_safe_int(data.get("weight"), default=0),
        subject_sets=subject_sets,
        min_count=data.get("min_count"),
        max_count=data.get("max_count"),
        source_text=_clean_str(data.get("source_text")),
        extra=extra,
    )


def load_universities() -> List[University]:
    raw_items = _read_json(UNIVERSITIES_FILE)
    universities: List[University] = []

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        name = _clean_str(item.get("name"))
        short_code = _clean_str(item.get("short_code"), upper=True)
        display_order = _safe_int(item.get("display_order"), default=9999)

        if not name or not short_code:
            continue

        universities.append(
            University(
                name=name,
                short_code=short_code,
                display_order=display_order,
            )
        )

    universities.sort(key=lambda u: u.display_order)
    return universities


def load_programmes() -> List[Programme]:
    raw_items = _read_json(PROGRAMMES_FILE)
    programmes: List[Programme] = []

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        university = _clean_str(item.get("university"))
        code = _clean_str(item.get("code"), upper=True)
        programme_name = _clean_str(item.get("programme_name"))
        level = _clean_str(item.get("level"))
        schemes = _clean_list_of_str(item.get("schemes", []), upper=True)

        if not university or not code or not programme_name:
            continue

        programmes.append(
            Programme(
                university=university,
                code=code,
                programme_name=programme_name,
                duration_years=item.get("duration_years"),
                level=level,
                schemes=schemes,
                has_cutoff_2025_2026=bool(item.get("has_cutoff_2025_2026", False)),
            )
        )

    return programmes


def load_cutoffs() -> List[CutoffRecord]:
    raw_items = _read_json(CUTOFFS_FILE)
    cutoffs: List[CutoffRecord] = []

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        university = _clean_str(item.get("university"))
        code = _clean_str(item.get("code"), upper=True)
        academic_year = _clean_str(item.get("academic_year"))
        cutoff_type = _clean_str(item.get("cutoff_type"), lower=True) or "none"
        gender = _clean_str(item.get("gender"), lower=True)
        scheme = _clean_str(item.get("scheme"), upper=True)

        if not university or not code:
            continue

        cutoffs.append(
            CutoffRecord(
                university=university,
                code=code,
                academic_year=academic_year,
                cutoff_type=cutoff_type,
                value=item.get("value"),
                gender=gender,
                scheme=scheme,
            )
        )

    return cutoffs


def load_subject_rules() -> List[SubjectRule]:
    raw_items = _read_json(SUBJECT_RULES_FILE)
    rules: List[SubjectRule] = []

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        university = _clean_str(item.get("university"))
        code = _clean_str(item.get("code"), upper=True)
        programme_name = _clean_str(item.get("programme_name"))

        if not university or not code or not programme_name:
            continue

        rules.append(
            SubjectRule(
                university=university,
                code=code,
                programme_name=programme_name,
                essential=_build_rule_block(item.get("essential")),
                relevant=_build_rule_block(item.get("relevant")),
                desirable=_build_rule_block(item.get("desirable")),
                raw_essential_text=_clean_str(
                    item.get("raw_essential_text") or item.get("essential_text")
                ),
                raw_relevant_text=_clean_str(
                    item.get("raw_relevant_text") or item.get("relevant_text")
                ),
                raw_desirable_text=_clean_str(
                    item.get("raw_desirable_text") or item.get("desirable_text")
                ),
                source_pages=item.get("source_pages", []),
                match_confidence=item.get("match_confidence"),
                normalization_status=_clean_str(item.get("normalization_status")),
                special_requirements=_clean_list_of_str(
                    item.get("special_requirements", [])
                ),
            )
        )

    return rules


def index_programmes(programmes: List[Programme]) -> Dict[Tuple[str, str], Programme]:
    indexed: Dict[Tuple[str, str], Programme] = {}
    for programme in programmes:
        key = make_programme_key(programme.university, programme.code)
        indexed[key] = programme
    return indexed


def index_cutoffs(cutoffs: List[CutoffRecord]) -> Dict[Tuple[str, str], CutoffRecord]:
    indexed: Dict[Tuple[str, str], CutoffRecord] = {}
    for cutoff in cutoffs:
        key = make_programme_key(cutoff.university, cutoff.code)
        indexed[key] = cutoff
    return indexed


def index_subject_rules(rules: List[SubjectRule]) -> Dict[Tuple[str, str], SubjectRule]:
    indexed: Dict[Tuple[str, str], SubjectRule] = {}
    for rule in rules:
        key = make_programme_key(rule.university, rule.code)
        indexed[key] = rule
    return indexed


def validate_data_integrity(
    programmes: List[Programme],
    cutoffs: List[CutoffRecord],
    subject_rules: List[SubjectRule],
) -> Dict[str, List[str]]:
    issues = {
        "missing_cutoffs_for_programmes": [],
        "missing_rules_for_programmes": [],
        "cutoffs_without_programmes": [],
        "rules_without_programmes": [],
        "duplicate_programmes": [],
        "duplicate_cutoffs": [],
        "duplicate_rules": [],
    }

    programme_keys_seen = set()
    for programme in programmes:
        key = make_programme_key(programme.university, programme.code)
        if key in programme_keys_seen:
            issues["duplicate_programmes"].append(f"{programme.university} :: {programme.code}")
        programme_keys_seen.add(key)

    cutoff_keys_seen = set()
    for cutoff in cutoffs:
        key = make_programme_key(cutoff.university, cutoff.code)
        if key in cutoff_keys_seen:
            issues["duplicate_cutoffs"].append(f"{cutoff.university} :: {cutoff.code}")
        cutoff_keys_seen.add(key)

    rule_keys_seen = set()
    for rule in subject_rules:
        key = make_programme_key(rule.university, rule.code)
        if key in rule_keys_seen:
            issues["duplicate_rules"].append(f"{rule.university} :: {rule.code}")
        rule_keys_seen.add(key)

    programme_keys = {make_programme_key(p.university, p.code) for p in programmes}
    cutoff_keys = {make_programme_key(c.university, c.code) for c in cutoffs}
    rule_keys = {make_programme_key(r.university, r.code) for r in subject_rules}

    for programme in programmes:
        key = make_programme_key(programme.university, programme.code)
        if key not in cutoff_keys:
            issues["missing_cutoffs_for_programmes"].append(f"{programme.university} :: {programme.code}")
        if key not in rule_keys:
            issues["missing_rules_for_programmes"].append(f"{programme.university} :: {programme.code}")

    for cutoff in cutoffs:
        key = make_programme_key(cutoff.university, cutoff.code)
        if key not in programme_keys:
            issues["cutoffs_without_programmes"].append(f"{cutoff.university} :: {cutoff.code}")

    for rule in subject_rules:
        key = make_programme_key(rule.university, rule.code)
        if key not in programme_keys:
            issues["rules_without_programmes"].append(f"{rule.university} :: {rule.code}")

    return issues


def load_all_data() -> Dict[str, Any]:
    universities = load_universities()
    programmes = load_programmes()
    cutoffs = load_cutoffs()
    subject_rules = load_subject_rules()

    integrity_report = validate_data_integrity(programmes, cutoffs, subject_rules)

    return {
        "universities": universities,
        "programmes": programmes,
        "cutoffs": cutoffs,
        "subject_rules": subject_rules,
        "programme_index": index_programmes(programmes),
        "cutoff_index": index_cutoffs(cutoffs),
        "subject_rule_index": index_subject_rules(subject_rules),
        "integrity_report": integrity_report,
    }
