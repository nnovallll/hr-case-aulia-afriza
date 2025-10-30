import streamlit as st
import pandas as pd
from supabase import create_client
from components.visual_utils import plot_tgv_summary

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

st.title("📊 Benchmark Dashboard")
st.markdown("Lihat hasil matching kandidat berdasarkan benchmark yang telah dibuat.")

job_vacancy_id = st.text_input("Masukkan Job Vacancy ID:", "J001")

if st.button("🚀 Jalankan Matching"):
    with st.spinner("Mengambil hasil matching..."):
        response = supabase.rpc("get_talent_match", {"job_vacancy_id": job_vacancy_id}).execute()
        df = pd.DataFrame(response.data)

        if df.empty:
            st.warning("⚠️ Tidak ditemukan hasil matching.")
        else:
            st.success(f"Ditemukan {len(df)} kandidat.")
            st.dataframe(df.head(10))

            avg_score = df["final_match_rate"].mean()
            top_score = df["final_match_rate"].max()
            st.metric("Rata-rata Match Rate", f"{avg_score:.2f}%")
            st.metric("Skor Tertinggi", f"{top_score:.2f}%")

            fig = plot_tgv_summary(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
