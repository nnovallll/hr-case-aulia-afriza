import plotly.express as px

def plot_tgv_summary(df):
    """Visualisasi distribusi skor kecocokan kandidat"""
    if "final_match_rate" not in df.columns:
        return None

    fig = px.histogram(
        df,
        x="final_match_rate",
        nbins=20,
        title="Distribusi Final Match Rate Kandidat",
        labels={"final_match_rate": "Final Match (%)"},
    )
    fig.update_layout(bargap=0.1, template="simple_white", title_x=0.5)
    return fig
