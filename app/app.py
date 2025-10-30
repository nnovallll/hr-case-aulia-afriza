# =========================================
# app/app.py
# Talent Match Intelligence Dashboard
# Step 3 — Final Visualization
# =========================================

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# ========== LOAD ENVIRONMENT VARIABLES ==========
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# Build connection string
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Talent Match Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Talent Match Intelligence Dashboard")
st.caption("Step 3 — Final Visualization | powered by Streamlit + PostgreSQL")

# ========== LOAD DATA FUNCTION ==========
@st.cache_data(ttl=600)
def load_data():
    query_path = os.path.join("app","queries", "step2_final_output.sql")
    try:
        with open(query_path, "r", encoding="utf-8") as f:
            query = f.read()
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# ========== LOAD DATA ==========
df = load_data()

if df.empty:
    st.warning("⚠️ Data tidak tersedia atau gagal dimuat. Periksa koneksi database & query SQL kamu.")
    st.stop()
else:
    st.success(f"✅ Data berhasil dimuat ({len(df):,} baris)")

# ========== SIDEBAR FILTER ==========
st.sidebar.header("🔍 Filters")

directorate_filter = st.sidebar.multiselect("Select Directorate", sorted(df["directorate"].dropna().unique()))
grade_filter = st.sidebar.multiselect("Select Grade", sorted(df["grade"].dropna().unique()))

df_filtered = df.copy()
if directorate_filter:
    df_filtered = df_filtered[df_filtered["directorate"].isin(directorate_filter)]
if grade_filter:
    df_filtered = df_filtered[df_filtered["grade"].isin(grade_filter)]

# ========== LAYOUT: 3 MAIN TABS ==========
tab1, tab2, tab3 = st.tabs(["📈 Overview", "🧩 Competency vs Psychometric", "🏁 Benchmark Insights"])

# =========================================
# TAB 1 — OVERVIEW
# =========================================
with tab1:
    st.subheader("Employee Match Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Employees", len(df_filtered))
    col2.metric("Avg Final Match (%)", round(df_filtered["final_match_rate"].mean(), 2))
    col3.metric("Highest Match (%)", round(df_filtered["final_match_rate"].max(), 2))
    col4.metric("Lowest Match (%)", round(df_filtered["final_match_rate"].min(), 2))

    st.markdown("---")

    # Distribution of Final Match
    st.write("### Distribution of Final Match Rate")
    fig_hist = px.histogram(
        df_filtered,
        x="final_match_rate",
        nbins=25,
        title="Final Match Rate Distribution",
        color_discrete_sequence=["#636EFA"]
    )
    fig_hist.update_layout(xaxis_title="Final Match Rate", yaxis_title="Count of Employees")
    st.plotly_chart(fig_hist, use_container_width=True)

    # Average Match by Directorate
    st.write("### Average Final Match by Directorate")
    avg_dir = df_filtered.groupby("directorate")["final_match_rate"].mean().sort_values()
    fig_bar_dir = px.bar(
        avg_dir,
        x=avg_dir.values,
        y=avg_dir.index,
        orientation="h",
        title="Average Final Match Rate per Directorate",
        labels={"x": "Average Match (%)", "y": "Directorate"}
    )
    st.plotly_chart(fig_bar_dir, use_container_width=True)

    # Average Match by Grade
    st.write("### Average Final Match by Grade")
    avg_grade = df_filtered.groupby("grade")["final_match_rate"].mean().sort_values(ascending=False)
    fig_bar_grade = px.bar(
        avg_grade,
        x=avg_grade.index,
        y=avg_grade.values,
        title="Average Final Match Rate per Grade",
        labels={"x": "Grade", "y": "Average Match (%)"}
    )
    st.plotly_chart(fig_bar_grade, use_container_width=True)

# =========================================
# TAB 2 — COMPETENCY VS PSYCHOMETRIC
# =========================================
with tab2:
    st.subheader("Competency vs Psychometric Match")

    # Pivot TGV to columns for plotting
    try:
        tgv_pivot = (
            df_filtered.pivot_table(index="candidate_id", columns="tgv_name", values="tgv_match_rate")
            .reset_index()
            .rename_axis(None, axis=1)
        )
        merged = pd.merge(df_filtered[["candidate_id", "directorate", "grade", "final_match_rate"]].drop_duplicates(),
                          tgv_pivot, on="candidate_id", how="left")

        if "Competency" in merged.columns and "Psychometric" in merged.columns:
            fig_scatter = px.scatter(
                merged,
                x="Competency",
                y="Psychometric",
                size="final_match_rate",
                color="directorate",
                hover_data=["candidate_id", "grade"],
                title="Competency vs Psychometric Match Rates"
            )
            fig_scatter.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color="DarkSlateGrey")))
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Kolom Competency dan Psychometric tidak ditemukan di dataset ini.")
    except Exception as e:
        st.error(f"Error membuat visualisasi scatter: {e}")

# =========================================
# TAB 3 — BENCHMARK INSIGHTS
# =========================================
with tab3:
    st.subheader("Benchmark Profiles and Talent Variables")

    try:
        avg_tv = (
            df_filtered.groupby("tv_name")[["baseline_score", "user_score", "tv_match_rate"]]
            .mean()
            .sort_values("tv_match_rate", ascending=False)
            .reset_index()
        )

        st.write("### Average Match per Talent Variable")
        st.dataframe(avg_tv.style.format({
            "baseline_score": "{:.2f}",
            "user_score": "{:.2f}",
            "tv_match_rate": "{:.2f}"
        }))

        # Visual Gap
        fig_gap = px.bar(
            avg_tv,
            x="tv_name",
            y=["baseline_score", "user_score"],
            barmode="group",
            title="Baseline vs Candidate Average Score per Talent Variable",
            labels={"value": "Score", "tv_name": "Talent Variable"}
        )
        st.plotly_chart(fig_gap, use_container_width=True)

    except Exception as e:
        st.error(f"Gagal memuat benchmark insights: {e}")

# =========================================
# END OF APP
# =========================================
