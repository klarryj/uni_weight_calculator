# utils/constants.py

ALEVEL_POINTS = {
    "A": 6,
    "B": 5,
    "C": 4,
    "D": 3,
    "E": 2,
    "O": 1,
    "F": 0,
}

OLEVEL_WEIGHTS = {
    "DISTINCTION": 0.3,
    "CREDIT": 0.2,
    "PASS": 0.1,
}

CLASSIFICATION = {
    "SAFE_MARGIN": 1.0,
    "BORDERLINE_MARGIN": -0.5,
}

SCHEME_LABELS = {
    "DQ": "District Quota",
    "GS": "Government Sponsorship",
    "PS": "Private Sponsorship",
}

SUBJECT_ALIASES = {
    "math": "Mathematics",
    "mathematics": "Mathematics",
    "subsidiary mathematics": "Sub-Mathematics",
    "sub mathematics": "Sub-Mathematics",
    "sub-mathematics": "Sub-Mathematics",
    "sub maths": "Sub-Mathematics",
    "sub math": "Sub-Mathematics",
    "physics": "Physics",
    "chemistry": "Chemistry",
    "biology": "Biology",
    "economics": "Economics",
    "geography": "Geography",
    "history": "History",
    "literature": "Literature",
    "literature in english": "Literature",
    "entrepreneurship": "Entrepreneurship",
    "computer studies": "Computer Studies",
    "ict": "ICT",
    "information and communication technology": "ICT",
    "general paper": "General Paper",
    "gp": "General Paper",
    "fine art": "Fine Art",
    "art": "Fine Art",
    "agriculture": "Agriculture",
    "food and nutrition": "Food and Nutrition",
    "islamic religious education": "Islamic Religious Education",
    "ire": "Islamic Religious Education",
    "christian religious education": "Christian Religious Education",
    "cre": "Christian Religious Education",
    "divinity": "Divinity",
    "kiswahili": "Kiswahili",
    "french": "French",
    "german": "German",
    "luganda": "Luganda",
    "runyakitara": "Runyakitara",
    "music": "Music",
    "physical education": "Physical Education",
}

CANONICAL_SUBJECTS = sorted(set(SUBJECT_ALIASES.values()))

GRADE_ALIASES = {
    "A": "A",
    "B": "B",
    "C": "C",
    "D": "D",
    "E": "E",
    "O": "O",
    "F": "F",
    "a": "A",
    "b": "B",
    "c": "C",
    "d": "D",
    "e": "E",
    "o": "O",
    "f": "F",
}

GENDER_ALIASES = {
    "male": "Male",
    "m": "Male",
    "female": "Female",
    "f": "Female",
}

CITIZENSHIP_ALIASES = {
    "ugandan": "Ugandan",
    "non-ugandan": "Non-Ugandan",
    "non ugandan": "Non-Ugandan",
    "foreign": "Non-Ugandan",
}
