import streamlit as st
import pandas as pd
from supabase import create_client
from components.ai_generator import generate_ai_text

# --- Connect Supabase ---
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

st.title("🤖 Step 3 : Talent Insights")

st.markdown("""
Halaman ini menampilkan insight AI berdasarkan hasil *Talent Match*.
Masukkan Job Vacancy ID untuk melihat ranking dan deskripsi kandidat terbaik.
""")

job_vacancy_id = st.text_input("Masukkan Job Vacancy ID:", "J001")

if st.button("🔍 Generate Insights"):
    with st.spinner("Mengambil data hasil matching..."):
        response = supabase.rpc("get_talent_match", {"job_vacancy_id": job_vacancy_id}).execute()
        df = pd.DataFrame(response.data)

        if df.empty:
            st.warning("⚠️ Tidak ditemukan hasil matching untuk ID tersebut.")
        else:
            st.success(f"Ditemukan {len(df)} kandidat.")
            st.dataframe(df.head(10))

            top_candidate = df.iloc[0]
            summary_prompt = f"""
            Anda adalah HR Data Analyst. Berdasarkan hasil talent matching berikut:
            Kandidat terbaik: {top_candidate['fullname']}
            Directorate: {top_candidate['directorate']}
            Grade: {top_candidate['grade']}
            Final match rate: {top_candidate['final_match_rate']}%
            Kategori: {top_candidate['match_category']}
            
            Jelaskan dalam bahasa Indonesia mengapa kandidat ini memiliki tingkat kecocokan tertinggi
            berdasarkan profil kompetensi, psikometrik, dan strength behavior.
            Gunakan nada analitis dan profesional.
            """

            ai_text = generate_ai_text(summary_prompt)
            st.subheader("🧠 AI Insight:")
            st.write(ai_text)
