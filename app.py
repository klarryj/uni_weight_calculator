import json
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
    return " ".join(
        [f'<span class="scheme-badge">{scheme}</span>' for scheme in schemes]
    )


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


def result_key(result) -> str:
    return f"{result.programme.university}::{result.programme.code}"


def is_shortlisted(result) -> bool:
    return result_key(result) in st.session_state.shortlist


def add_to_shortlist(result) -> None:
    key = result_key(result)
    if key not in st.session_state.shortlist:
        st.session_state.shortlist.append(key)


def remove_from_shortlist(result) -> None:
    key = result_key(result)
    if key in st.session_state.shortlist:
        st.session_state.shortlist.remove(key)


def serialize_result(result) -> dict:
    return {
        "university": result.programme.university,
        "code": result.programme.code,
        "programme_name": result.programme.programme_name,
        "schemes": result.programme.schemes,
        "weight": result.weight,
        "eligible": result.eligible,
        "status": result.status,
        "best_scheme": result.best_scheme,
        "reason": result.reason,
    }


def build_download_payload(student, results) -> dict:
    return {
        "student_profile": {
            "gender": student.gender,
            "citizenship": student.citizenship,
            "district": student.district,
            "general_paper": student.general_paper,
            "sub_math_or_ict": student.sub_math_or_ict,
            "alevel_subjects": [
                {"subject": s.subject, "grade": s.grade}
                for s in student.alevel_subjects
            ],
            "olevel": {
                "distinctions": student.olevel.distinctions,
                "credits": student.olevel.credits,
                "passes": student.olevel.passes,
            },
        },
        "summary": results["summary"],
        "top_recommendations": [
            serialize_result(r) for r in results["top_recommendations"]
        ],
        "alternatives": [
            serialize_result(r) for r in results["alternatives"]
        ],
        "all_results": [
            serialize_result(r) for r in results["all_results"]
        ],
        "integrity_report": results.get("integrity_report", {}),
    }


def render_result_card(
    result,
    compact: bool = False,
    allow_shortlist: bool = False,
    button_namespace: str = "default",
) -> None:
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

    with st.expander(f"Why this recommendation? - {result.programme.code}"):
        st.write(result.reason or "No explanation available.")

        if result.status == "SAFE":
            st.success("Strong option. Prioritize this in your applications.")
        elif result.status == "BORDERLINE":
            st.warning("Possible but competitive. Consider safer backups.")
        elif result.status == "RISKY":
            st.error("High risk. Apply only if you have safer alternatives.")
        elif result.status == "NO_CUTOFF":
            st.info("No cutoff data. Treat this as exploratory.")
        elif result.status == "NOT_ELIGIBLE":
            st.error("You do not meet minimum requirements.")

    if allow_shortlist and not compact:
        action_label = (
            f"Remove from shortlist - {result.programme.code} - {result.programme.university}"
            if is_shortlisted(result)
            else f"Add to shortlist - {result.programme.code} - {result.programme.university}"
        )

        unique_button_key = f"shortlist_{button_namespace}_{result_key(result)}"

        if st.button(action_label, key=unique_button_key):
            if is_shortlisted(result):
                remove_from_shortlist(result)
            else:
                add_to_shortlist(result)
            st.rerun()


def render_result_group(
    title: str,
    subtitle: str,
    results,
    limit: int | None = None,
    allow_shortlist: bool = False,
    button_namespace: str = "group",
) -> None:
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
    for i, result in enumerate(items):
        render_result_card(
            result,
            allow_shortlist=allow_shortlist,
            button_namespace=f"{button_namespace}_{i}",
        )

    if limit and len(results) > limit:
        st.caption(f"Showing {limit} of {len(results)} results in this section.")


def render_results_dashboard(student, results) -> None:
    summary = results["summary"]
    top = results["top_recommendations"]
    alternatives = results["alternatives"]
    grouped = results["grouped"]
    all_results = results["all_results"]

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        download_payload = build_download_payload(student, results)
        st.download_button(
            label="Download Results (JSON)",
            data=json.dumps(download_payload, indent=2),
            file_name="uni_compass_results.json",
            mime="application/json",
        )

    with action_col2:
        if st.button("Start New Analysis"):
            st.session_state.latest_results = None
            st.session_state.latest_student = None
            st.session_state.shortlist = []
            st.rerun()

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

    if summary["safe"] > 0:
        highlight_message = (
            f"You currently have {summary['safe']} safe option(s). Focus on these first."
        )
    elif summary["borderline"] > 0:
        highlight_message = (
            f"You have {summary['borderline']} borderline option(s). "
            "You should balance ambition with safer backups."
        )
    else:
        highlight_message = (
            "Your current profile looks competitive mainly in risky or no-cutoff "
            "categories. Backup choices will matter a lot."
        )

    st.markdown(
        f"""
        <div class="highlight-strip">
            <strong>Quick guidance:</strong> {highlight_message}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-card">
            <h3 style="margin-bottom:0.35rem;">Recommended application strategy</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if summary["safe"] >= 3:
        st.success("Apply to at least 2–3 SAFE programmes as your main choices.")
    elif summary["safe"] > 0:
        st.warning("You have limited safe options. Combine SAFE + BORDERLINE wisely.")
    elif summary["borderline"] > 0:
        st.warning("Focus on BORDERLINE options but include less competitive backups.")
    else:
        st.error("Prioritize less competitive programmes and diploma options.")

    if top:
        best = top[0]
        st.markdown(
            f"""
            <div class="highlight-strip">
                <strong>Top match:</strong> {best.programme.programme_name} at {best.programme.university}
                <br/>Status: <strong>{best.status}</strong> | Weight: <strong>{best.weight}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_result_group(
        "Top recommendations",
        "These are your strongest current options based on the engine.",
        top,
        limit=5,
        allow_shortlist=True,
        button_namespace="top",
    )

    render_result_group(
        "Alternative options",
        "These are useful backups in case your first choices are too competitive.",
        alternatives,
        limit=5,
        allow_shortlist=True,
        button_namespace="alternatives",
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

    sort_option = st.selectbox(
        "Sort results by",
        [
            "Best weight first",
            "Programme name (A-Z)",
            "University name (A-Z)",
            "Status",
        ],
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

    status_order = {
        "SAFE": 0,
        "BORDERLINE": 1,
        "RISKY": 2,
        "NO_CUTOFF": 3,
        "NOT_ELIGIBLE": 4,
    }

    if sort_option == "Best weight first":
        chosen_results = sorted(chosen_results, key=lambda x: x.weight, reverse=True)
    elif sort_option == "Programme name (A-Z)":
        chosen_results = sorted(
            chosen_results,
            key=lambda x: x.programme.programme_name.lower(),
        )
    elif sort_option == "University name (A-Z)":
        chosen_results = sorted(
            chosen_results,
            key=lambda x: x.programme.university.lower(),
        )
    elif sort_option == "Status":
        chosen_results = sorted(
            chosen_results,
            key=lambda x: (status_order.get(x.status, 99), -x.weight),
        )

    max_items = st.slider(
        "How many results to show",
        min_value=5,
        max_value=50,
        value=12,
        step=1,
    )

    if chosen_results:
        for i, result in enumerate(chosen_results[:max_items]):
            render_result_card(
                result,
                allow_shortlist=True,
                button_namespace=f"explore_{selected_group}_{i}",
            )
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

    st.markdown(
        """
        <div class="section-card">
            <h3 style="margin-bottom:0.35rem;">Your shortlist</h3>
            <div class="mini-note">Save promising options here and compare them more easily.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    shortlisted_results = [
        result for result in all_results
        if result_key(result) in st.session_state.shortlist
    ]

    if shortlisted_results:
        st.write(f"You have {len(shortlisted_results)} programme(s) in your shortlist.")

        for i, result in enumerate(shortlisted_results):
            render_result_card(
                result,
                allow_shortlist=True,
                button_namespace=f"shortlist_view_{i}",
            )

        compare_options = [
            f"{r.programme.programme_name} | {r.programme.university} | {r.programme.code}"
            for r in shortlisted_results
        ]

        selected_compare = st.multiselect(
            "Select up to 3 programmes to compare",
            compare_options,
            max_selections=3,
        )

        selected_compare_results = [
            r for r in shortlisted_results
            if f"{r.programme.programme_name} | {r.programme.university} | {r.programme.code}" in selected_compare
        ]

        if selected_compare_results:
            compare_rows = []
            for result in selected_compare_results:
                compare_rows.append(
                    {
                        "Programme": result.programme.programme_name,
                        "University": result.programme.university,
                        "Code": result.programme.code,
                        "Status": result.status,
                        "Weight": result.weight,
                        "Best Scheme": result.best_scheme or "-",
                        "Eligible": "Yes" if result.eligible else "No",
                    }
                )

            st.markdown("### Comparison table")
            st.table(compare_rows)
    else:
        st.info("Your shortlist is empty. Add programmes from the results above.")

    integrity_report = results.get("integrity_report") or {}
    problem_count = sum(len(v) for v in integrity_report.values())

    if problem_count > 0:
        with st.expander("Data integrity notes"):
            st.write("These are internal dataset warnings that may help during build and cleanup.")
            st.json(integrity_report)


def main() -> None:
    if "latest_results" not in st.session_state:
        st.session_state.latest_results = None

    if "latest_student" not in st.session_state:
        st.session_state.latest_student = None

    if "shortlist" not in st.session_state:
        st.session_state.shortlist = []

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

        district = st.text_input(
            "Home District",
            placeholder="Optional, useful for District Quota",
        )

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

        subject_3_options = [
            s for s in SUBJECT_OPTIONS if s not in {subject_1, subject_2}
        ]
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
            distinctions = st.number_input(
                "Distinctions",
                min_value=0,
                max_value=12,
                value=0,
            )
        with o2:
            credits = st.number_input(
                "Credits",
                min_value=0,
                max_value=12,
                value=0,
            )
        with o3:
            passes = st.number_input(
                "Passes",
                min_value=0,
                max_value=12,
                value=0,
            )

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

        st.session_state.latest_results = results
        st.session_state.latest_student = student

    if (
        st.session_state.latest_results is not None
        and st.session_state.latest_student is not None
    ):
        render_results_dashboard(
            st.session_state.latest_student,
            st.session_state.latest_results,
        )


if __name__ == "__main__":
    main()
