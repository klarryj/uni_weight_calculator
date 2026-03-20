# app.py
import streamlit as st
import pandas as pd
from engine import get_weight, GRADE_POINTS

st.set_page_config(page_title="Uganda Uni Compass", layout="wide")

# Load the CSV data
@st.cache_data
def load_data():
    return pd.read_csv('courses.csv')

df = load_data()

st.title("🧭 The Admissions Compass")
st.markdown("Enter your results below to discover every course you qualify for.")

# --- SIDEBAR: O-LEVEL & PROFILE ---
with st.sidebar:
    st.header("1. Personal Profile")
    gender = st.radio("Gender", ["Male", "Female"])
    
    st.header("2. O-Level Results")
    o_d = st.number_input("Distinctions (D1-D2)", 0, 10, 0)
    o_c = st.number_input("Credits (C3-C6)", 0, 10, 0)
    o_p = st.number_input("Passes (P7-P8)", 0, 10, 0)
    
    o_level_data = {'D': o_d, 'C': o_c, 'P': o_p}

# --- MAIN PAGE: A-LEVEL RESULTS ---
st.subheader("3. Your A-Level Grades")
col1, col2, col3 = st.columns(3)

# For testing, we let the user select subjects and grades
# In the final version, this will be more dynamic
with col1:
    subj1_name = st.selectbox("Subject 1", ["Biology", "Chemistry", "Physics", "Math", "Economics"])
    subj1_grade = st.selectbox("Grade 1", list(GRADE_POINTS.keys()))

with col2:
    subj2_name = st.selectbox("Subject 2", ["Biology", "Chemistry", "Physics", "Math", "Economics"], index=1)
    subj2_grade = st.selectbox("Grade 2", list(GRADE_POINTS.keys()))

with col3:
    subj3_name = st.selectbox("Subject 3", ["Biology", "Chemistry", "Physics", "Math", "Economics"], index=2)
    subj3_grade = st.selectbox("Grade 3", list(GRADE_POINTS.keys()))

c1, c2 = st.columns(2)
gp_pass = c1.checkbox("Passed General Paper?")
sub_pass = c2.checkbox("Passed Sub-Math/ICT?")

# Pack grades into a dictionary for the engine
user_grades = {
    subj1_name: subj1_grade,
    subj2_name: subj2_grade,
    subj3_name: subj3_grade,
    'GP': gp_pass,
    'Sub': sub_pass
}

# --- THE DISCOVERY ENGINE ---
if st.button("🚀 DISCOVER MY COURSES", use_container_width=True):
    results = []
    
    for _, row in df.iterrows():
        # Calculate weight using the engine
        try:
            score = get_weight(user_grades, row, o_level_data, gender)
            results.append({
                "Course": row['Course_Name'],
                "Code": row['Course_Code'],
                "Your Weight": score
            })
        except Exception as e:
            # Skip courses where subjects don't match the current test list
            continue

    if results:
        results_df = pd.DataFrame(results).sort_values(by="Your Weight", ascending=False)
        
        st.subheader("Your Discovery Dashboard")
        st.write(f"Showing {len(results_df)} courses you qualify for:")
        
        # Display as a clean table
        st.dataframe(results_df, use_container_width=True, hide_index=True)
        
        # Highlight top choice
        top_course = results_df.iloc[0]
        st.success(f"🌟 Your best fit is **{top_course['Course']}** with a weight of **{top_course['Your Weight']}**")
    else:
        st.warning("No courses found. Ensure your A-Level subjects match the requirements.")
