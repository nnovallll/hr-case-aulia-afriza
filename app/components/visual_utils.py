import plotly.express as px
import plotly.graph_objects as go

def plot_distribution(df):
    fig = px.histogram(df, x="final_match_rate", color="match_category",
                       nbins=20, title="Match Rate Distribution")
    fig.update_layout(xaxis_title="Match %", yaxis_title="Count")
    return fig

def plot_tgv_summary(df):
    tgv_summary = df.groupby("tgv_name")["tgv_match_rate"].mean().reset_index()
    return px.bar(tgv_summary, x="tgv_name", y="tgv_match_rate", color="tgv_name",
                  text_auto=True, title="Average Match per TGV")

def plot_radar(df, candidate_id):
    values = df[df["employee_id"] == candidate_id].groupby("tgv_name")["tgv_match_rate"].mean()
    fig = go.Figure(data=go.Scatterpolar(
        r=values.values, theta=values.index, fill='toself', name=candidate_id))
    fig.update_layout(title=f"TGV Radar - {candidate_id}",
                      polar=dict(radialaxis=dict(visible=True, range=[0,100])))
    return fig
