import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- Connect to Supabase ---
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

st.title("📊 Benchmark Dashboard - Talent Match")

# --- Input parameter ---
job_vacancy_id = st.text_input("Masukkan Job Vacancy ID:", "J001")

if st.button("🚀 Jalankan Matching Analysis"):
    with st.spinner("Menjalankan analisis..."):
        try:
            response = supabase.rpc("get_talent_match", {"job_vacancy_id": job_vacancy_id}).execute()
            df = pd.DataFrame(response.data)

            if not df.empty:
                st.success(f"✅ Ditemukan {len(df)} kandidat untuk {job_vacancy_id}")
                st.dataframe(df)

                # --- Optional: Visualisasi ---
                st.subheader("📈 Distribusi Final Match Rate")
                st.bar_chart(df["final_match_rate"])

                st.subheader("🏆 Top 10 Kandidat")
                st.table(df.head(10))
            else:
                st.warning("⚠️ Tidak ada hasil ditemukan untuk Job Vacancy ID tersebut.")
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan saat mengambil data: {e}")
