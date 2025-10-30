import streamlit as st
import pandas as pd
from supabase import create_client
from components.ai_generator import generate_ai_text

# --- Supabase Connection ---
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

st.title("📋 Benchmark Form")

st.markdown("""
Gunakan halaman ini untuk membuat dan menyimpan benchmark role baru.  
Silakan pilih employee dengan rating tinggi (5) untuk dijadikan acuan.
""")

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
    role_purpose = st.text_area(
        "Role Purpose",
        "Analisis dan visualisasi data HR untuk mendukung keputusan strategis."
    )

    if st.button("💾 Simpan Benchmark"):
        if selected:
            ids = [x.split(" - ")[0] for x in selected]
            record = {
                "job_vacancy_id": job_vacancy_id.strip(),
                "role_name": role_name.strip(),
                "job_level": grade.strip(),
                "role_purpose": role_purpose.strip(),
                "selected_talent_ids": ids,
            }

            try:
                result = supabase.table("talent_benchmarks").upsert(record).execute()
                if result.data:
                    st.success("✅ Benchmark berhasil disimpan ke database Supabase!")
                else:
                    st.warning("⚠️ Insert tidak berhasil, periksa data input.")
            except Exception as e:
                st.error(f"🚨 Gagal menyimpan benchmark: {e}")
        else:
            st.warning("⚠️ Pilih minimal satu benchmark employee terlebih dahulu.")

    # --- AI Summary Generator ---
    if st.button("✨ Generate Job Summary (AI)"):
        prompt = f"""
        Anda adalah HR Analyst. Buatkan ringkasan profesional tentang role berikut:
        - Role: {role_name}
        - Grade: {grade}
        - Purpose: {role_purpose}
        Jelaskan kompetensi utama yang dibutuhkan dan karakteristik karyawan ideal.
        """
        ai_summary = generate_ai_text(prompt)
        st.subheader("🧠 AI-Generated Job Summary")
        st.write(ai_summary)
else:
    st.error("Gagal mengambil data employees dari Supabase.")
