import streamlit as st
import pandas as pd

# 1. Configuration & Data Loading
st.set_page_config(page_title="Uganda Uni Weight Calculator", layout="centered")
df = pd.read_csv('courses.csv')

# Grade to Point Mapping
grade_points = {'A': 6, 'B': 5, 'C': 4, 'D': 3, 'E': 2, 'O': 1, 'F': 0}

st.title("🇺🇬 University Weighting Calculator")
st.write("Calculate your weight for Public Universities (2026/2027 Academic Year)")

# 2. User Inputs: Course Selection
target_course = st.selectbox("Select your target course:", df['Course_Name'].unique())
course_info = df[df['Course_Name'] == target_course].iloc[0]

st.info(f"**Weighting Criteria for {target_course}:** \n\n"
        f"Essential: {course_info['Essential_1']}, {course_info['Essential_2']} | "
        f"Relevant: {course_info['Relevant']}")

# 3. User Inputs: A-Level Grades
st.subheader("A-Level Results")
col1, col2, col3 = st.columns(3)

with col1:
    e1 = st.selectbox("Essential 1 Grade", ['A', 'B', 'C', 'D', 'E', 'O', 'F'])
with col2:
    e2 = st.selectbox("Essential 2 Grade", ['A', 'B', 'C', 'D', 'E', 'O', 'F'])
with col3:
    rel = st.selectbox("Relevant Grade", ['A', 'B', 'C', 'D', 'E', 'O', 'F'])

sub_passed = st.checkbox("Passed Sub-Math or ICT? (1 point)")
gp_passed = st.checkbox("Passed General Paper? (1 point)")

# 4. User Inputs: O-Level & Gender
st.subheader("O-Level & Other Factors")
o_dist = st.number_input("Number of Distinctions (D1-D2)", min_value=0, max_value=10, value=0)
o_cred = st.number_input("Number of Credits (C3-C6)", min_value=0, max_value=10, value=0)
o_pass = st.number_input("Number of Passes (P7-P8)", min_value=0, max_value=10, value=0)

gender = st.radio("Gender", ["Male", "Female"])

# 5. Calculation Logic
if st.button("Calculate Final Weight"):
    # A-Level Calculation
    a_level_score = (grade_points[e1] * 3) + (grade_points[e2] * 3) + (grade_points[rel] * 2)
    desirable_score = (1 if sub_passed else 0) + (1 if gp_passed else 0)
    
    # O-Level Calculation (D=0.3, C=0.2, P=0.1)
    o_level_score = (o_dist * 0.3) + (o_cred * 0.2) + (o_pass * 0.1)
    
    # Gender Bonus
    gender_bonus = 1.5 if gender == "Female" else 0
    
    total_weight = a_level_score + desirable_score + o_level_score + gender_bonus
    
    # Display Results
    st.success(f"### Your Total Weight: {total_weight:.2f}")
    
    with st.expander("See Weight Breakdown"):
        st.write(f"- A-Level Essentials & Relevant: {a_level_score}")
        st.write(f"- Desirable (GP/Sub): {desirable_score}")
        st.write(f"- O-Level Score: {o_level_score:.2f}")
        st.write(f"- Gender Bonus: {gender_bonus}")
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        color: white;
        background-color: #00ff00;
        border-radius: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
