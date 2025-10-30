import streamlit as st
from components.db_utils import run_query
from components.visual_utils import plot_radar
from components.ai_generator import generate_ai_job_profile
import pandas as pd

st.title("🔍 Step 3: Talent Insights")

if "job_vacancy_id" not in st.session_state:
    st.warning("⚠️ Please complete Step 1 first.")
else:
    job_vacancy_id = st.session_state["job_vacancy_id"]
    df = run_query("app/queries/step2_final_output.sql", {"job_vacancy_id": job_vacancy_id})

    # ==============================
    # 1️⃣ Ranking top candidates
    # ==============================
    st.subheader("🏆 Top Candidates by Final Match Rate")
    top_candidates = (
        df.groupby(["employee_id", "fullname"])["final_match_rate"]
        .max()
        .reset_index()
        .sort_values("final_match_rate", ascending=False)
        .head(5)
    )
    st.dataframe(top_candidates)

    # ==============================
    # 2️⃣ Radar chart untuk satu kandidat
    # ==============================
    candidate_id = st.selectbox("Select Candidate for Radar", top_candidates["employee_id"])
    st.plotly_chart(plot_radar(df, candidate_id), use_container_width=True)

    # ==============================
    # 3️⃣ AI Insight Generator
    # ==============================
    st.subheader("🤖 AI-Generated HR Insight Summary")

    # Ambil data top 3 kandidat untuk context prompt
    top3 = top_candidates.head(3)
    summary_text = "\n".join(
        [f"{i+1}. {row['fullname']} ({row['employee_id']}) — {row['final_match_rate']}%" 
         for i, row in top3.iterrows()]
    )

    prompt = f"""
    You are an HR data analyst. Summarize insights based on candidate match data below.

    Job role ID: {job_vacancy_id}
    Top candidates:
    {summary_text}

    Explain:
    1. What patterns do you observe among the top performers?
    2. Which candidate shows the strongest alignment overall?
    3. What development recommendations can be made for moderate matches?

    Keep the language formal, concise, and in business tone (for HR presentation).
    """

    if st.button("🧠 Generate Insight Summary"):
        with st.spinner("Generating AI insight..."):
            ai_insight = generate_ai_job_profile("Talent Insight Summary", prompt)
            st.markdown(ai_insight)
