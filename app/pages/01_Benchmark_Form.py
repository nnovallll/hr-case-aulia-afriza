import streamlit as st
import pandas as pd
from supabase import create_client

# --- Supabase Connection ---
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

st.title("📋 Benchmark Form")

st.markdown("""
Gunakan halaman ini untuk membuat dan menyimpan benchmark role baru.
Silakan pilih employee dengan rating tinggi (5) untuk dijadikan acuan.
""")

# --- Ambil daftar employees ---
with st.spinner("Mengambil daftar karyawan..."):
    data = supabase.table("employees").select("employee_id, fullname").execute()
    df_employees = pd.DataFrame(data.data)

if not df_employees.empty:
    selected = st.multiselect(
        "Pilih hingga 3 benchmark employees:",
        df_employees["employee_id"] + " - " + df_employees["fullname"],
        max_selections=3
    )

    job_vacancy_id = st.text_input("Job Vacancy ID", "J001")
    role_name = st.text_input("Role Name", "Data Analyst")
    grade = st.text_input("Grade", "G5")
    role_purpose = st.text_area("Role Purpose", "Analisis dan visualisasi data HR untuk mendukung keputusan strategis.")

    if st.button("💾 Simpan Benchmark"):
        if selected:
            ids = [x.split(" - ")[0] for x in selected]
            supabase.table("talent_benchmarks").insert({
                "job_vacancy_id": job_vacancy_id,
                "role_name": role_name,
                "job_level": grade,
                "role_purpose": role_purpose,
                "selected_talent_ids": ids
            }).execute()
            st.success("✅ Benchmark berhasil disimpan ke database Supabase!")
        else:
            st.warning("⚠️ Pilih minimal satu benchmark employee terlebih dahulu.")
else:
    st.error("Gagal mengambil data employees dari Supabase.")
