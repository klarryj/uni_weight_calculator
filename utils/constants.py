# utils/constants.py

# A-Level grading points
ALEVEL_POINTS = {
    "A": 6,
    "B": 5,
    "C": 4,
    "D": 3,
    "E": 2,
    "O": 1,
    "F": 0
}

# O-Level weighting
OLEVEL_WEIGHTS = {
    "DISTINCTION": 0.3,
    "CREDIT": 0.2,
    "PASS": 0.1
}

# Subject weighting multipliers
WEIGHT_MULTIPLIERS = {
    "ESSENTIAL": 3,
    "RELEVANT": 2,
    "DESIRABLE": 1
}

# Result classification thresholds
CLASSIFICATION = {
    "SAFE_MARGIN": 1.0,
    "BORDERLINE_MARGIN": -0.5
}

# Scheme labels
SCHEME_LABELS = {
    "DQ": "District Quota",
    "GS": "Government Sponsorship",
    "PS": "Private Sponsorship"
}
