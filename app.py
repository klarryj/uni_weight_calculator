import streamlit as st
import pandas as pd
import os
from engine import get_weight, get_color_status, GRADE_POINTS

st.set_page_config(page_title="Uganda Admissions Compass 2.0", layout="wide")

st.title("🧭 The Admissions Compass 2.0")
st.write("Compare your weight against historical cut-offs across 7 Public Universities.")

# --- SIDEBAR & INPUTS ---
# (Keep the same Sidebar and A-Level Grade logic from our last version)
with st.sidebar:
    st.header("1. Personal Profile")
    gender = st.radio("Gender", ["Male", "Female"])
    o_d = st.number_input("Distinctions (D1-D2)", 0, 10, 0)
    o_c = st.number_input("Credits (C3-C6)", 0, 10, 0)
    o_p = st.number_input("Passes (P7-P8)", 0, 10, 0)
    o_level_data = {'D': o_d, 'C': o_c, 'P': o_p}

# Subject Input Section
st.subheader("2. Your A-Level Grades")
col1, col2, col3 = st.columns(3)
with col1:
    s1_n = st.selectbox("Subject 1", ["Biology", "Chemistry", "Physics", "Math", "Economics", "History", "Literature", "Geography"])
    s1_g = st.selectbox("Grade 1", list(GRADE_POINTS.keys()))
with col2:
    s2_n = st.selectbox("Subject 2", ["Biology", "Chemistry", "Physics", "Math", "Economics", "History", "Literature", "Geography"], index=1)
    s2_g = st.selectbox("Grade 2", list(GRADE_POINTS.keys()))
with col3:
    s3_n = st.selectbox("Subject 3", ["Biology", "Chemistry", "Physics", "Math", "Economics", "History", "Literature", "Geography"], index=2)
    s3_g = st.selectbox("Grade 3", list(GRADE_POINTS.keys()))

c1, c2 = st.columns(2)
gp_p = c1.checkbox("Passed General Paper?")
sub_p = c2.checkbox("Passed Sub-Math/ICT?")

user_grades = {s1_n: s1_g, s2_n: s2_g, s3_n: s3_g, 'GP': gp_p, 'Sub': sub_p}

# --- UNIVERSITY SELECTION ---
st.subheader("3. Select University")
# This looks at your 'data' folder and finds all CSVs
uni_choice = st.selectbox("Which university would you like to check?", 
                          ["Makerere", "Kyambogo", "Mbarara", "Gulu", "Busitema", "Muni", "Kabale"])

# Map choice to file name
file_map = {
    "Makerere": "data/makerere.csv",
    "Kyambogo": "data/kyambogo.csv",
    "Mbarara": "data/mbarara.csv"
    # ... add the rest here
}

# --- DISCOVERY DASHBOARD ---
if st.button("🚀 RUN COMPASS ANALYSIS", use_container_width=True):
    try:
        df = pd.read_csv(file_map[uni_choice])
        results = []

        for _, row in df.iterrows():
            weight = get_weight(user_grades, row, o_level_data, gender)
            status, color = get_color_status(weight, row['Cut_off'])
            
            results.append({
                "Course": row['Course_Name'],
                "Your Weight": weight,
                "Last Cut-off": row['Cut_off'],
                "Status": status,
                "color": color
            })

        # Display results with Color Coding
        res_df = pd.DataFrame(results).sort_values(by="Your Weight", ascending=False)
        
        st.subheader(f"Analysis for {uni_choice} University")
        
        # We use a custom loop to show colored boxes for each course
        for index, row in res_df.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{row['Course']}**")
                c2.write(f"Weight: {row['Your Weight']}")
                c3.markdown(f'<p style="background-color:{row["color"]}; color:white; padding:5px; border-radius:5px; text-align:center;">{row["Status"]}</p>', unsafe_allow_html=True)
                st.divider()

    except FileNotFoundError:
        st.error(f"Data file for {uni_choice} not found. Please upload {file_map[uni_choice]} to your GitHub.")
