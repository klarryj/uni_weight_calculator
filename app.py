import json
from pathlib import Path
from typing import List

import streamlit as st

from core.engine import evaluate_programmes
from core.models import OLevelSummary, Programme, RuleBlock, StudentProfile, SubjectGrade
from core.recommendations import group_results_by_status, recommendation_summary, top_results
from core.search import search_results
from utils.formatters import explain_scheme_labels, format_matched_subjects, format_scheme_badges, format_scheme_statuses


DATA_DIR = Path(__file__).parent / "data"
PROGRAMMES_FILE = DATA_DIR / "programmes.json"


def load_programmes() -> List[Programme]:
    with open(PROGRAMMES_FILE, "r", encoding="utf-8") as file:
        raw_programmes = json.load(file)

    programmes = []
    for item in raw_programmes:
        programme = Programme(
            university=item["university"],
            programme_name=item["programme_name"],
            code=item["code"],
            duration=item.get("duration"),
            schemes=item.get("schemes", []),
            essential=RuleBlock(**item["essential"]),
            relevant=RuleBlock(**item["relevant"]) if item.get("relevant") else None,
            desirable=RuleBlock(**item["desirable"]) if item.get("desirable") else None,
            cutoffs=item.get("cutoffs", {}),
            notes=item.get("notes"),
        )
        programmes.append(programme)

    return programmes


def build_student_profile() -> StudentProfile:
    st.sidebar.header("Student Profile")

    gender = st.sidebar.selectbox("Gender", ["Male", "Female"])

    subject_options = [
        "Mathematics", "Physics", "Chemistry", "Biology", "Economics",
        "Geography", "History", "Literature", "Entrepreneurship"
    ]
    grade_options = ["A", "B", "C", "D", "E", "O", "F"]

    st.sidebar.subheader("A-Level Subjects")
    selected_subjects = []
    used_subject_names = set()

    for i in range(3):
        available_subjects = [subject for subject in subject_options if subject not in used_subject_names]
        subject = st.sidebar.selectbox(
            f"Subject {i + 1}",
            available_subjects,
            key=f"subject_{i}"
        )
        grade = st.sidebar.selectbox(
            f"Grade {i + 1}",
            grade_options,
            key=f"grade_{i}"
        )
        selected_subjects.append(SubjectGrade(subject=subject, grade=grade))
        used_subject_names.add(subject)

    st.sidebar.subheader("Additional Information")
    general_paper = st.sidebar.selectbox("General Paper Grade", ["", "A", "B", "C", "D", "E", "O", "F"])
    sub_math_or_ict = st.sidebar.checkbox("Passed Sub-Math / ICT / Computer Studies")
    district = st.sidebar.text_input("Home District (optional, useful for DQ)")
    citizenship = st.sidebar.selectbox("Citizenship", ["Ugandan", "Non-Ugandan"])

    st.sidebar.subheader("O-Level Summary")
    distinctions = st.sidebar.number_input("Distinctions", min_value=0, max_value=12, value=0)
    credits = st.sidebar.number_input("Credits", min_value=0, max_value=12, value=0)
    passes = st.sidebar.number_input("Passes", min_value=0, max_value=12, value=0)

    return StudentProfile(
        gender=gender,
        alevel_subjects=selected_subjects,
        general_paper=general_paper if general_paper else None,
        sub_math_or_ict=sub_math_or_ict,
        olevel=OLevelSummary(
            distinctions=int(distinctions),
            credits=int(credits),
            passes=int(passes),
        ),
        district=district or None,
        citizenship=citizenship,
    )


def render_summary(summary: dict) -> None:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Eligible", summary["eligible"])
    col2.metric("Safe", summary["safe"])
    col3.metric("Borderline", summary["borderline"])
    col4.metric("Risky", summary["risky"])
    col5.metric("Not Eligible", summary["not_eligible"])


def render_results_table(results) -> None:
    if not results:
        st.info("No results found.")
        return

    rows = []
    for result in results:
        rows.append({
            "Programme": result.programme.programme_name,
            "University": result.programme.university,
            "Code": result.programme.code,
            "Weight": result.weight,
            "Status": result.status,
            "Best Scheme": result.best_scheme or "-",
            "Schemes": format_scheme_badges(result.programme.schemes),
            "Scheme Statuses": format_scheme_statuses(result.scheme_statuses),
            "Matched Subjects": format_matched_subjects(result),
            "Reason": result.reason,
        })

    st.dataframe(rows, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Uni Compass Uganda", layout="wide")

    st.title("Uni Compass Uganda")
    st.write(
        "Find where your results may place you across Uganda's public universities."
    )

    st.caption(explain_scheme_labels())

    programmes = load_programmes()
    student = build_student_profile()

    if st.button("Run Analysis", type="primary"):
        results = evaluate_programmes(student, programmes)
        summary = recommendation_summary(results)
        grouped = group_results_by_status(results)

        st.subheader("Results Summary")
        render_summary(summary)

        st.subheader("Top Recommendations")
        render_results_table(top_results(results, limit=10, eligible_only=True))

        with st.expander("Safe Options"):
            render_results_table(grouped.get("SAFE", []))

        with st.expander("Borderline Options"):
            render_results_table(grouped.get("BORDERLINE", []))

        with st.expander("Risky Options"):
            render_results_table(grouped.get("RISKY", []))

        with st.expander("Not Eligible"):
            render_results_table(grouped.get("NOT_ELIGIBLE", []))

        st.subheader("Search for a Course")
        query = st.text_input("Search by programme name, university, or code")
        searched = search_results(results, query) if query else results
        render_results_table(searched)


if __name__ == "__main__":
    main()
