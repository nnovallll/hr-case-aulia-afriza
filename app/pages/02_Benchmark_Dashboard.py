import streamlit as st
from components.db_utils import run_query
from components.visual_utils import plot_distribution, plot_tgv_summary

st.title("📈 Step 2: Benchmark Dashboard")

if "job_vacancy_id" not in st.session_state:
    st.warning("Please define a benchmark role in Step 1 first.")
else:
    job_vacancy_id = st.session_state["job_vacancy_id"]
    df = run_query("app\queries/step2_final_output.sql", {"job_vacancy_id": job_vacancy_id})

    st.subheader("Match Rate Overview")
    st.plotly_chart(plot_distribution(df), use_container_width=True)

    st.subheader("TGV Performance Summary")
    st.plotly_chart(plot_tgv_summary(df), use_container_width=True)

    st.dataframe(df.head(50))
