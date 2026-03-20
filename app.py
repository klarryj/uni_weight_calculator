# --- UNIVERSITY SELECTION ---
st.subheader("3. Select University")

# We define the official names here
universities = [
    "Makerere", "Kyambogo", "Mbarara", "Busitema", "Soroti", 
    "Muni", "Lira", "Gulu", "Mountains of the Moon", "Kabale"
]

uni_choice = st.selectbox("Which university would you like to check?", universities)

# This mapping connects the name in the dropdown to the exact file name in your 'data' folder
file_map = {
    "Makerere": "data/makerere.csv",
    "Kyambogo": "data/kyambogo.csv",
    "Mbarara": "data/mbarara.csv",
    "Busitema": "data/busitema.csv",
    "Soroti": "data/soroti.csv",
    "Muni": "data/muni.csv",
    "Lira": "data/lira.csv",
    "Gulu": "data/gulu.csv",
    "Mountains of the Moon": "data/mountains_of_the_moon.csv",
    "Kabale": "data/kabale.csv"
}

# --- DISCOVERY DASHBOARD ---
if st.button("🚀 RUN COMPASS ANALYSIS", use_container_width=True):
    # This line (line 57) will no longer throw a KeyError because every
    # choice in 'universities' is now a key in 'file_map'.
    try:
        csv_path = file_map[uni_choice]
        df = pd.read_csv(csv_path)
        
        # Clean up column names just in case there are hidden spaces from the CSV creation
        df.columns = df.columns.str.strip()
        
        # ... (rest of your calculation loop goes here)
