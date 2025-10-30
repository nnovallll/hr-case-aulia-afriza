import streamlit as st
import pandas as pd
from sqlalchemy import text
from components.db_utils import get_engine
from components.ai_generator import generate_ai_job_profile
import json

st.title("🧱 Step 1: Define Benchmark Role")

# ===============================
# 1️⃣ Ambil data employee dari DB
# ===============================
engine = get_engine()
with engine.connect() as conn:
    df_emp = pd.read_sql("""
        SELECT employee_id, fullname
        FROM employees
        ORDER BY fullname ASC
    """, conn)

# Gabungkan ID + nama untuk dropdown
df_emp["display_name"] = df_emp["fullname"] + " (" + df_emp["employee_id"] + ")"

# ===============================
# 2️⃣ Form input role benchmark
# ===============================
st.subheader("Benchmark Role Setup")

role_name = st.text_input("Role Name")
job_level = st.selectbox("Job Level", ["Junior", "Mid", "Senior"])
role_purpose = st.text_area("Role Purpose")

# Dropdown multi-select (maks 3)
selected_display = st.multiselect(
    "Select up to 3 Benchmark Employees:",
    options=df_emp["display_name"].tolist(),
    max_selections=3
)

# Ambil employee_id dari pilihan user
selected_ids = [
    row.split("(")[-1].replace(")", "").strip()
    for row in selected_display
]

st.caption(f"✅ Selected: {', '.join(selected_ids) if selected_ids else 'None'}")

# ===============================
# 3️⃣ Simpan ke database
# ===============================
if st.button("💾 Save Benchmark Role"):
    if not role_name or len(selected_ids) == 0:
        st.error("⚠️ Please fill in role name and select at least 1 employee.")
    elif len(selected_ids) > 3:
        st.error("⚠️ You can select a maximum of 3 benchmark employees.")
    else:
        jid = role_name.lower().replace(" ", "_")

        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO talent_benchmarks
                (job_vacancy_id, role_name, job_level, role_purpose, selected_talent_ids)
                VALUES (:jid, :rname, :jlevel, :rpurpose, :ids)
                ON CONFLICT (job_vacancy_id)
                DO UPDATE SET 
                    selected_talent_ids = EXCLUDED.selected_talent_ids,
                    role_purpose = EXCLUDED.role_purpose,
                    job_level = EXCLUDED.job_level;
            """), {
                "jid": jid,
                "rname": role_name,
                "jlevel": job_level,
                "rpurpose": role_purpose,
                "ids": selected_ids
            })

        st.session_state["job_vacancy_id"] = jid
        st.success(f"✅ Benchmark for '{role_name}' saved successfully!")

        # ===============================
        # 4️⃣ Generate AI Job Profile
        # ===============================
        with st.spinner("🤖 Generating AI-based Job Profile..."):
            ai_profile = generate_ai_job_profile(role_name, role_purpose)
            st.subheader("AI-Generated Job Profile")
            st.markdown(ai_profile)
