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
        padding-top: 1.5rem;
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
        padding: 1rem 1rem 0.8rem 1rem;
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
        margin-bottom: 0.8rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.05);
        border-left: 6px solid #0B6623;
    }

    .status-safe {
        color: #0B6623;
        font-weight: 700;
    }

    .status-borderline {
        color: #B8860B;
        font-weight: 700;
    }

    .status-risky {
        color: #B22222;
        font-weight: 700;
    }

    .status-no_cutoff {
        color: #6b7280;
        font-weight: 700;
    }

    .status-not_eligible {
        color: #374151;
        font-weight: 700;
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


def status_class_name(status: str) -> str:
    mapping = {
        "SAFE": "status-safe",
        "BORDERLINE": "status-borderline",
        "RISKY": "status-risky",
        "NO_CUTOFF": "status-no_cutoff",
        "NOT_ELIGIBLE": "status-not_eligible",
    }
    return mapping.get(status, "status-no_cutoff")


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


def render_result_card(result) -> None:
    status_css = status_class_name(result.status)
    schemes_html = render_scheme_badges(result.programme.schemes)

    with st.container():
        st.markdown(
            f"""
            <div class="result-card">
                <div style="display:flex; justify-content:space-between; gap:1rem; align-items:flex-start; flex-wrap:wrap;">
                    <div>
                        <div style="font-size:1.05rem; font-weight:700; color:#111;">{result.programme.programme_name}</div>
                        <div style="color:#555; margin-top:0.2rem;">{result.programme.university}</div>
                        <div style="margin-top:0.45rem;">{schemes_html}</div>
                    </div>
                    <div style="text-align:right; min-width:140px;">
                        <div class="{status_css}">{result.status.replace('_', ' ')}</div>
                        <div style="margin-top:0.25rem; color:#333;">Weight: <strong>{result.weight}</strong></div>
                        <div style="margin-top:0.15rem; color:#555;">Best Scheme: <strong>{result.best_scheme or '-'}</strong></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("See explanation"):
            st.write(result.reason or "No explanation available.")


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
                Enter your A-Level and O-Level performance, then run the analysis to see where you are competitive.
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

    if submitted:
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

        st.markdown(
            """
            <div class="section-card">
                <h3 style="margin-bottom:0.35rem;">Your results summary</h3>
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

        st.markdown(
            """
            <div class="section-card">
                <h3 style="margin-bottom:0.35rem;">Top recommendations</h3>
                <div class="mini-note">These are your strongest options based on the current engine evaluation.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if top:
            for result in top:
                render_result_card(result)
        else:
            st.info("No top recommendations found yet.")

        st.markdown(
            """
            <div class="section-card">
                <h3 style="margin-bottom:0.35rem;">Alternative options</h3>
                <div class="mini-note">These may still be worth considering as backups.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if alternatives:
            for result in alternatives[:8]:
                render_result_card(result)
        else:
            st.info("No alternative options found.")

        with st.expander("See safe options"):
            safe_results = grouped.get("SAFE", [])
            if safe_results:
                for result in safe_results:
                    render_result_card(result)
            else:
                st.info("No safe options found.")

        with st.expander("See borderline options"):
            borderline_results = grouped.get("BORDERLINE", [])
            if borderline_results:
                for result in borderline_results:
                    render_result_card(result)
            else:
                st.info("No borderline options found.")

        with st.expander("See risky options"):
            risky_results = grouped.get("RISKY", [])
            if risky_results:
                for result in risky_results:
                    render_result_card(result)
            else:
                st.info("No risky options found.")

        with st.expander("See results with no cutoff"):
            no_cutoff_results = grouped.get("NO_CUTOFF", [])
            if no_cutoff_results:
                for result in no_cutoff_results:
                    render_result_card(result)
            else:
                st.info("No no-cutoff results found.")

        with st.expander("See not eligible results"):
            not_eligible_results = grouped.get("NOT_ELIGIBLE", [])
            if not_eligible_results:
                for result in not_eligible_results:
                    render_result_card(result)
            else:
                st.info("No not-eligible results found.")

        integrity_report = results.get("integrity_report") or {}
        problem_count = sum(len(v) for v in integrity_report.values())

        if problem_count > 0:
            with st.expander("Data integrity notes"):
                st.write("These are internal dataset warnings that may help during build and cleanup.")
                st.json(integrity_report)


if __name__ == "__main__":
    main()
