import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.models import CutoffRecord, Programme, RuleBlock, SubjectRule, University


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

UNIVERSITIES_FILE = DATA_DIR / "universities.json"
PROGRAMMES_FILE = DATA_DIR / "programmes.json"
CUTOFFS_FILE = DATA_DIR / "cutoffs_2025_2026.json"
SUBJECT_RULES_FILE = DATA_DIR / "subject_rules.json"


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing required data file: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _clean_str(value: Any, upper: bool = False, lower: bool = False) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if not text:
        return ""

    if text.lower() in {"nan", "none", "null"}:
        return ""

    if upper:
        return text.upper()

    if lower:
        return text.lower()

    return text


def _clean_optional_str(value: Any, upper: bool = False, lower: bool = False) -> Optional[str]:
    text = _clean_str(value, upper=upper, lower=lower)
    return text or None


def _clean_list_of_str(values: Any, upper: bool = False, lower: bool = False) -> List[str]:
    if values is None:
        return []

    if not isinstance(values, list):
        values = [values]

    cleaned: List[str] = []
    for value in values:
        text = _clean_str(value, upper=upper, lower=lower)
        if text:
            cleaned.append(text)

    return cleaned


def _safe_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    if value is None:
        return default

    text = _clean_str(value)
    if not text:
        return default

    try:
        return int(float(text))
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    if value is None:
        return default

    text = _clean_str(value)
    if not text:
        return default

    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _normalize_key(text: str) -> str:
    return " ".join(_clean_str(text, lower=True).split())


def make_programme_key(university: str, code: str) -> Tuple[str, str]:
    return (_normalize_key(university), _clean_str(code, upper=True))


def _build_rule_block(data: Any) -> Optional[RuleBlock]:
    if not isinstance(data, dict):
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

    raw_subjects = data.get("subjects")
    subjects = _clean_list_of_str(raw_subjects) if raw_subjects is not None else None
    if subjects == []:
        subjects = None

    raw_subject_sets = data.get("subject_sets")
    subject_sets: Optional[List[List[str]]] = None

    if isinstance(raw_subject_sets, list):
        cleaned_sets: List[List[str]] = []

        for item in raw_subject_sets:
            if isinstance(item, list):
                cleaned = _clean_list_of_str(item)
                if cleaned:
                    cleaned_sets.append(cleaned)
            elif isinstance(item, dict):
                nested_values: List[str] = []
                for value in item.values():
                    if isinstance(value, list):
                        nested_values.extend(_clean_list_of_str(value))
                    else:
                        text = _clean_str(value)
                        if text:
                            nested_values.append(text)

                if nested_values:
                    cleaned_sets.append(nested_values)
            else:
                text = _clean_str(item)
                if text:
                    cleaned_sets.append([text])

        if cleaned_sets:
            subject_sets = cleaned_sets

    return RuleBlock(
        type=_clean_str(data.get("type")),
        subjects=subjects,
        count=_safe_int(data.get("count")),
        weight=_safe_int(data.get("weight"), default=0) or 0,
        subject_sets=subject_sets,
        min_count=_safe_int(data.get("min_count")),
        max_count=_safe_int(data.get("max_count")),
        source_text=_clean_optional_str(data.get("source_text")),
        extra=extra,
    )


def load_universities() -> List[University]:
    raw_items = _read_json(UNIVERSITIES_FILE)
    universities: List[University] = []

    if not isinstance(raw_items, list):
        return universities

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
                display_order=display_order if display_order is not None else 9999,
            )
        )

    universities.sort(key=lambda x: x.display_order)
    return universities


def load_programmes() -> List[Programme]:
    raw_items = _read_json(PROGRAMMES_FILE)
    programmes: List[Programme] = []

    if not isinstance(raw_items, list):
        return programmes

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        university = _clean_str(item.get("university"))
        code = _clean_str(item.get("code"), upper=True)
        programme_name = _clean_str(item.get("programme_name"))
        duration_years = _safe_int(item.get("duration_years"))
        level = _clean_optional_str(item.get("level"))
        schemes = _clean_list_of_str(item.get("schemes"), upper=True)
        has_cutoff = bool(item.get("has_cutoff_2025_2026", False))

        if not university or not code or not programme_name:
            continue

        programmes.append(
            Programme(
                university=university,
                code=code,
                programme_name=programme_name,
                duration_years=duration_years,
                level=level,
                schemes=schemes,
                has_cutoff_2025_2026=has_cutoff,
            )
        )

    return programmes


def load_cutoffs() -> List[CutoffRecord]:
    raw_items = _read_json(CUTOFFS_FILE)
    cutoffs: List[CutoffRecord] = []

    if not isinstance(raw_items, list):
        return cutoffs

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        university = _clean_str(item.get("university"))
        code = _clean_str(item.get("code"), upper=True)
        academic_year = _clean_str(item.get("academic_year"))
        cutoff_type = _clean_str(item.get("cutoff_type"), lower=True) or "none"

        if not university or not code:
            continue

        value = _safe_float(item.get("value"))
        female = _safe_float(item.get("female"))
        male = _safe_float(item.get("male"))

        gender = _clean_str(item.get("gender"), lower=True)
        if gender == "female" and value is not None and female is None:
            female = value
        elif gender == "male" and value is not None and male is None:
            male = value

        options = item.get("options")
        if not isinstance(options, dict):
            options = None

        scheme = _clean_str(item.get("scheme"), upper=True)
        if scheme:
            if options is None:
                options = {}
            if "scheme" not in options:
                options["scheme"] = scheme

        cutoffs.append(
            CutoffRecord(
                university=university,
                code=code,
                academic_year=academic_year,
                cutoff_type=cutoff_type,
                value=value,
                female=female,
                male=male,
                options=options,
            )
        )

    return cutoffs


def load_subject_rules() -> List[SubjectRule]:
    raw_items = _read_json(SUBJECT_RULES_FILE)
    rules: List[SubjectRule] = []

    if not isinstance(raw_items, list):
        return rules

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        university = _clean_str(item.get("university"))
        code = _clean_str(item.get("code"), upper=True)
        programme_name = _clean_str(item.get("programme_name"))

        if not university or not code or not programme_name:
            continue

        source_pages_raw = item.get("source_pages")
        source_pages: List[int] = []
        if isinstance(source_pages_raw, list):
            for page in source_pages_raw:
                page_num = _safe_int(page)
                if page_num is not None:
                    source_pages.append(page_num)

        rules.append(
            SubjectRule(
                university=university,
                code=code,
                programme_name=programme_name,
                essential=_build_rule_block(item.get("essential")),
                relevant=_build_rule_block(item.get("relevant")),
                desirable=_build_rule_block(item.get("desirable")),
                raw_essential_text=_clean_optional_str(
                    item.get("raw_essential_text") or item.get("essential_text")
                ),
                raw_relevant_text=_clean_optional_str(
                    item.get("raw_relevant_text") or item.get("relevant_text")
                ),
                raw_desirable_text=_clean_optional_str(
                    item.get("raw_desirable_text") or item.get("desirable_text")
                ),
                source_pages=source_pages,
                match_confidence=_clean_optional_str(item.get("match_confidence")),
                normalization_status=_clean_optional_str(item.get("normalization_status")),
                special_requirements=_clean_list_of_str(item.get("special_requirements")),
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

        if key not in indexed:
            indexed[key] = CutoffRecord(
                university=cutoff.university,
                code=cutoff.code,
                academic_year=cutoff.academic_year,
                cutoff_type=cutoff.cutoff_type,
                value=cutoff.value,
                female=cutoff.female,
                male=cutoff.male,
                options=dict(cutoff.options) if isinstance(cutoff.options, dict) else None,
            )
            continue

        existing = indexed[key]

        if not existing.academic_year and cutoff.academic_year:
            existing.academic_year = cutoff.academic_year

        if existing.cutoff_type in {"", "none"} and cutoff.cutoff_type:
            existing.cutoff_type = cutoff.cutoff_type

        if existing.value is None and cutoff.value is not None:
            existing.value = cutoff.value

        if existing.female is None and cutoff.female is not None:
            existing.female = cutoff.female

        if existing.male is None and cutoff.male is not None:
            existing.male = cutoff.male

        if cutoff.options:
            if existing.options is None:
                existing.options = {}
            existing.options.update(cutoff.options)

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
    issues: Dict[str, List[str]] = {
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
        key = (
            make_programme_key(cutoff.university, cutoff.code),
            cutoff.academic_year,
            cutoff.cutoff_type,
            cutoff.value,
            cutoff.female,
            cutoff.male,
        )
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
    cutoff_programme_keys = {make_programme_key(c.university, c.code) for c in cutoffs}
    rule_programme_keys = {make_programme_key(r.university, r.code) for r in subject_rules}

    for programme in programmes:
        key = make_programme_key(programme.university, programme.code)
        if key not in cutoff_programme_keys:
            issues["missing_cutoffs_for_programmes"].append(
                f"{programme.university} :: {programme.code}"
            )
        if key not in rule_programme_keys:
            issues["missing_rules_for_programmes"].append(
                f"{programme.university} :: {programme.code}"
            )

    for cutoff in cutoffs:
        key = make_programme_key(cutoff.university, cutoff.code)
        if key not in programme_keys:
            issues["cutoffs_without_programmes"].append(
                f"{cutoff.university} :: {cutoff.code}"
            )

    for rule in subject_rules:
        key = make_programme_key(rule.university, rule.code)
        if key not in programme_keys:
            issues["rules_without_programmes"].append(
                f"{rule.university} :: {rule.code}"
            )

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
