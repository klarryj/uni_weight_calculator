import streamlit as st

from core.pipeline import run_full_analysis
from core.student import build_student_profile, validate_student_profile


st.set_page_config(
    page_title="Uni Compass Uganda",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f7f7f7;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    h1, h2, h3 {
        color: #0B6623;
    }

    .hero-card {
        background: linear-gradient(135deg, #0B6623 0%, #145A32 100%);
        color: white;
        padding: 1.25rem 1.2rem;
        border-radius: 18px;
        margin-bottom: 1rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    }

    .hero-card h1, .hero-card h2, .hero-card h3, .hero-card p {
        color: white !important;
        margin: 0;
    }

    .section-card {
        background: white;
        padding: 1rem 1rem 0.9rem 1rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        border-top: 4px solid #C9A227;
    }

    .mini-note {
        color: #555;
        font-size: 0.95rem;
    }

    .result-card {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.05);
        border-left: 6px solid #0B6623;
    }

    .result-card.safe {
        border-left-color: #0B6623;
    }

    .result-card.borderline {
        border-left-color: #B8860B;
    }

    .result-card.risky {
        border-left-color: #B22222;
    }

    .result-card.no_cutoff {
        border-left-color: #6b7280;
    }

    .result-card.not_eligible {
        border-left-color: #374151;
    }

    .status-pill {
        display: inline-block;
        padding: 0.28rem 0.6rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
    }

    .status-safe {
        background: #e9f7ee;
        color: #0B6623;
    }

    .status-borderline {
        background: #fff8e1;
        color: #B8860B;
    }

    .status-risky {
        background: #fdecec;
        color: #B22222;
    }

    .status-no_cutoff {
        background: #f3f4f6;
        color: #6b7280;
    }

    .status-not_eligible {
        background: #eeeeee;
        color: #374151;
    }

    .scheme-badge {
        display: inline-block;
        padding: 0.15rem 0.45rem;
        border-radius: 999px;
        background: #eef5ef;
        color: #0B6623;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.25rem;
        margin-bottom: 0.25rem;
        border: 1px solid #d8e6d9;
    }

    .metric-box {
        background: white;
        padding: 1rem 0.8rem;
        border-radius: 14px;
        border-top: 4px solid #C9A227;
        box-shadow: 0 4px 14px rgba(0,0,0,0.05);
        text-align: center;
    }

    .metric-label {
        color: #555;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
    }

    .metric-value {
        color: #0B6623;
        font-size: 1.5rem;
        font-weight: 700;
    }

    .highlight-strip {
        background: #fff;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #C9A227;
        box-shadow: 0 4px 14px rgba(0,0,0,0.05);
    }

    .stButton > button {
        background-color: #0B6623;
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        padding: 0.65rem 1rem;
    }

    .stButton > button:hover {
        background-color: #094d1a;
        color: white;
    }

    div[data-testid="stForm"] {
        background: white;
        padding: 1rem;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        border-top: 4px solid #C9A227;
    }

    .small-meta {
        color: #666;
        font-size: 0.88rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


SUBJECT_OPTIONS = [
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Economics",
    "Geography",
    "History",
    "Literature",
    "Entrepreneurship",
    "Agriculture",
    "Fine Art",
    "Food and Nutrition",
    "Christian Religious Education",
    "Islamic Religious Education",
    "Divinity",
    "Computer Studies",
    "ICT",
    "French",
    "German",
    "Kiswahili",
    "Luganda",
    "Runyakitara",
    "Music",
    "Physical Education",
]

GRADE_OPTIONS = ["A", "B", "C", "D", "E", "O", "F"]
GP_OPTIONS = ["", "A", "B", "C", "D", "E", "O", "F"]


def status_css(status: str) -> str:
    mapping = {
        "SAFE": "status-safe",
        "BORDERLINE": "status-borderline",
        "RISKY": "status-risky",
        "NO_CUTOFF": "status-no_cutoff",
        "NOT_ELIGIBLE": "status-not_eligible",
    }
    return mapping.get(status, "status-no_cutoff")


def card_css(status: str) -> str:
    mapping = {
        "SAFE": "safe",
        "BORDERLINE": "borderline",
        "RISKY": "risky",
        "NO_CUTOFF": "no_cutoff",
        "NOT_ELIGIBLE": "not_eligible",
    }
    return mapping.get(status, "no_cutoff")


def render_scheme_badges(schemes) -> str:
    if not schemes:
        return ""
    return " ".join([f'<span class="scheme-badge">{scheme}</span>' for scheme in schemes])


def render_metric_box(label: str, value) -> None:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_card(result, compact: bool = False) -> None:
    schemes_html = render_scheme_badges(result.programme.schemes)
    status_class = status_css(result.status)
    card_class = card_css(result.status)

    if compact:
        st.markdown(
            f"""
            <div class="result-card {card_class}">
                <div style="display:flex; justify-content:space-between; gap:1rem; align-items:flex-start; flex-wrap:wrap;">
                    <div>
                        <div style="font-size:1rem; font-weight:700; color:#111;">{result.programme.programme_name}</div>
                        <div class="small-meta">{result.programme.university}</div>
                    </div>
                    <div style="text-align:right;">
                        <span class="status-pill {status_class}">{result.status.replace('_', ' ')}</span>
                        <div style="margin-top:0.35rem; color:#333;">Weight: <strong>{result.weight}</strong></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"""
        <div class="result-card {card_class}">
            <div style="display:flex; justify-content:space-between; gap:1rem; align-items:flex-start; flex-wrap:wrap;">
                <div style="flex:1; min-width:230px;">
                    <div style="font-size:1.05rem; font-weight:700; color:#111;">{result.programme.programme_name}</div>
                    <div class="small-meta" style="margin-top:0.2rem;">{result.programme.university}</div>
                    <div style="margin-top:0.45rem;">{schemes_html}</div>
                </div>
                <div style="text-align:right; min-width:155px;">
                    <span class="status-pill {status_class}">{result.status.replace('_', ' ')}</span>
                    <div style="margin-top:0.35rem; color:#333;">Weight: <strong>{result.weight}</strong></div>
                    <div style="margin-top:0.2rem; color:#555;">Best Scheme: <strong>{result.best_scheme or '-'}</strong></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("See explanation"):
        st.write(result.reason or "No explanation available.")


def render_result_group(title: str, subtitle: str, results, limit: int | None = None):
    st.markdown(
        f"""
        <div class="section-card">
            <h3 style="margin-bottom:0.25rem;">{title}</h3>
            <div class="mini-note">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not results:
        st.info("No results found in this section.")
        return

    items = results[:limit] if limit else results
    for result in items:
        render_result_card(result)

    if limit and len(results) > limit:
        st.caption(f"Showing {limit} of {len(results)} results in this section.")


def main() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <h1>🎓 Uni Compass Uganda</h1>
            <p style="margin-top:0.6rem; font-size:1rem;">
                Find where your results can place you across Uganda's public universities.
                See your strongest options, borderline choices, and backup paths.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-card">
            <h3 style="margin-bottom:0.35rem;">How it works</h3>
            <div class="mini-note">
                Enter your A-Level and O-Level performance, then run the analysis to see where you are strongest,
                where you are borderline, and which backup options are worth considering.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("student_input_form"):
        st.subheader("Your academic profile")

        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Gender", ["Male", "Female"])
        with col2:
            citizenship = st.selectbox("Citizenship", ["Ugandan", "Non-Ugandan"])

        district = st.text_input("Home District", placeholder="Optional, useful for District Quota")

        st.markdown("### A-Level subjects")
        s1_col, g1_col = st.columns([2, 1])
        with s1_col:
            subject_1 = st.selectbox("Subject 1", SUBJECT_OPTIONS, key="subject_1")
        with g1_col:
            grade_1 = st.selectbox("Grade 1", GRADE_OPTIONS, key="grade_1")

        subject_2_options = [s for s in SUBJECT_OPTIONS if s != subject_1]
        s2_col, g2_col = st.columns([2, 1])
        with s2_col:
            subject_2 = st.selectbox("Subject 2", subject_2_options, key="subject_2")
        with g2_col:
            grade_2 = st.selectbox("Grade 2", GRADE_OPTIONS, key="grade_2")

        subject_3_options = [s for s in SUBJECT_OPTIONS if s not in {subject_1, subject_2}]
        s3_col, g3_col = st.columns([2, 1])
        with s3_col:
            subject_3 = st.selectbox("Subject 3", subject_3_options, key="subject_3")
        with g3_col:
            grade_3 = st.selectbox("Grade 3", GRADE_OPTIONS, key="grade_3")

        st.markdown("### Additional information")
        extra1, extra2 = st.columns(2)
        with extra1:
            general_paper = st.selectbox("General Paper Grade", GP_OPTIONS)
        with extra2:
            sub_math_or_ict = st.checkbox("Passed Sub-Math / ICT / Computer Studies")

        st.markdown("### O-Level summary")
        o1, o2, o3 = st.columns(3)
        with o1:
            distinctions = st.number_input("Distinctions", min_value=0, max_value=12, value=0)
        with o2:
            credits = st.number_input("Credits", min_value=0, max_value=12, value=0)
        with o3:
            passes = st.number_input("Passes", min_value=0, max_value=12, value=0)

        submitted = st.form_submit_button("Run Analysis")

    if not submitted:
        return

    raw_subjects = [
        {"subject": subject_1, "grade": grade_1},
        {"subject": subject_2, "grade": grade_2},
        {"subject": subject_3, "grade": grade_3},
    ]

    student = build_student_profile(
        gender=gender,
        alevel_subjects=raw_subjects,
        general_paper=general_paper,
        sub_math_or_ict=sub_math_or_ict,
        distinctions=distinctions,
        credits=credits,
        passes=passes,
        district=district,
        citizenship=citizenship,
    )

    validation = validate_student_profile(student)

    if validation["errors"]:
        for error in validation["errors"]:
            st.error(error)
        return

    if validation["warnings"]:
        for warning in validation["warnings"]:
            st.warning(warning)

    with st.spinner("Analyzing your options..."):
        results = run_full_analysis(student)

    summary = results["summary"]
    top = results["top_recommendations"]
    alternatives = results["alternatives"]
    grouped = results["grouped"]
    all_results = results["all_results"]

    st.markdown(
        """
        <div class="section-card">
            <h3 style="margin-bottom:0.35rem;">Your results summary</h3>
            <div class="mini-note">This gives you a quick picture of how competitive your profile looks.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_box("Safe", summary["safe"])
    with m2:
        render_metric_box("Borderline", summary["borderline"])
    with m3:
        render_metric_box("Risky", summary["risky"])
    with m4:
        render_metric_box("Total", summary["total"])

    highlight_message = None
    if summary["safe"] > 0:
        highlight_message = f"You currently have {summary['safe']} safe option(s). Focus on these first."
    elif summary["borderline"] > 0:
        highlight_message = f"You have {summary['borderline']} borderline option(s). You should balance ambition with safer backups."
    else:
        highlight_message = "Your current profile looks competitive mainly in risky or no-cutoff categories. Backup choices will matter a lot."

    st.markdown(
        f"""
        <div class="highlight-strip">
            <strong>Quick guidance:</strong> {highlight_message}
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_result_group(
        "Top recommendations",
        "These are your strongest current options based on the engine.",
        top,
        limit=5,
    )

    render_result_group(
        "Alternative options",
        "These are useful backups in case your first choices are too competitive.",
        alternatives,
        limit=5,
    )

    st.markdown(
        """
        <div class="section-card">
            <h3 style="margin-bottom:0.35rem;">Explore all results</h3>
            <div class="mini-note">Use the filter below to inspect a specific group.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_group = st.selectbox(
        "Choose a result group",
        [
            "Safe",
            "Borderline",
            "Risky",
            "No Cutoff",
            "Not Eligible",
            "All Results",
        ],
    )

    if selected_group == "Safe":
        chosen_results = grouped.get("SAFE", [])
    elif selected_group == "Borderline":
        chosen_results = grouped.get("BORDERLINE", [])
    elif selected_group == "Risky":
        chosen_results = grouped.get("RISKY", [])
    elif selected_group == "No Cutoff":
        chosen_results = grouped.get("NO_CUTOFF", [])
    elif selected_group == "Not Eligible":
        chosen_results = grouped.get("NOT_ELIGIBLE", [])
    else:
        chosen_results = all_results

    max_items = st.slider("How many results to show", min_value=5, max_value=50, value=12, step=1)

    if chosen_results:
        for result in chosen_results[:max_items]:
            render_result_card(result)
    else:
        st.info("No results found in this group.")

    with st.expander("Quick preview of your best safe options"):
        safe_results = grouped.get("SAFE", [])
        if safe_results:
            for result in safe_results[:5]:
                render_result_card(result, compact=True)
        else:
            st.info("No safe options found.")

    with st.expander("Quick preview of your borderline options"):
        borderline_results = grouped.get("BORDERLINE", [])
        if borderline_results:
            for result in borderline_results[:5]:
                render_result_card(result, compact=True)
        else:
            st.info("No borderline options found.")

    integrity_report = results.get("integrity_report") or {}
    problem_count = sum(len(v) for v in integrity_report.values())

    if problem_count > 0:
        with st.expander("Data integrity notes"):
            st.write("These are internal dataset warnings that may help during build and cleanup.")
            st.json(integrity_report)


if __name__ == "__main__":
    main()
