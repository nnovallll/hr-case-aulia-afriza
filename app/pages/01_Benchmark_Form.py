import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# ========== SETUP ==========
st.set_page_config(page_title="AI Talent Benchmark Generator", page_icon="⚙️", layout="wide")
load_dotenv()

# Database connection
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# ========== LOAD EMPLOYEE DATA ==========
@st.cache_data
def load_employee_list():
    query = "SELECT DISTINCT employee_id, fullname FROM employees ORDER BY employee_id;"
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df

try:
    df_emp = load_employee_list()
except Exception as e:
    st.error(f"❌ Failed to load employee list: {e}")
    st.stop()

# ========== PAGE HEADER ==========
st.title("⚙️ AI Talent Benchmark Generator")
st.caption("Step 3 — Input Role Information & Select Benchmark Employees")

st.markdown("---")

# ========== INPUT FORM ==========
with st.form("benchmark_form"):
    st.subheader("1️⃣ Role Information")
    role_name = st.text_input("**Role Name**", placeholder="e.g., Data Analyst")
    job_level = st.selectbox("**Job Level**", ["Junior", "Middle", "Senior"])
    role_purpose = st.text_area(
        "**Role Purpose**",
        placeholder="1–2 sentences to describe role outcomes.\nExample: Ensure production targets are met with optimal quality and cost efficiency.",
        height=80
    )

    st.markdown("---")
    st.subheader("2️⃣ Employee Benchmarking")
    st.caption("Select up to 3 employees to serve as benchmark (high performers).")

    selected_ids = st.multiselect(
        "Select Benchmark Employees",
        df_emp["employee_id"].tolist(),
        format_func=lambda x: f"{x} — {df_emp.loc[df_emp['employee_id'] == x, 'fullname'].values[0]}",
        max_selections=3
    )

    submitted = st.form_submit_button("🚀 Generate Benchmark Profile")

# ========== OUTPUT DISPLAY ==========
if submitted:
    if not role_name or not job_level or len(selected_ids) == 0:
        st.error("⚠️ Please fill all fields and select at least one benchmark employee.")
    else:
        st.success("✅ Inputs captured successfully!")
        st.write("### Summary of Inputs")
        summary = {
            "Role Name": role_name,
            "Job Level": job_level,
            "Role Purpose": role_purpose,
            "Selected Benchmark Employee IDs": ", ".join(selected_ids)
        }
        st.table(pd.DataFrame(summary.items(), columns=["Column", "Value"]))

        st.info("Next Step → Will recompute baseline and match profile dynamically.")
