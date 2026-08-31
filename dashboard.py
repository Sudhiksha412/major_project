import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
import os

st.set_page_config(page_title="AI System Monitor", layout="wide")
st.title("AI-Based IT Infrasturcture Monitoring Dashboard")

st.markdown("""
<style>
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(255, 0, 0.0.7); }
    70% { box-shodow: 0 0 0 15px rgba(255, 0 ,0, 0); }
    100% { box-shodow: 0 0 0 0 rgba(255, 0, 0, 0);}
}

.alert-box{
    padding: 15px;
    border-radius: 10px;
    background-color: #ff4b4b;
    color: white;
    text-align: center;
    font-weight: bold;
    font-size: 22px;
    margin-top: 15px;
    animation: pulse 1.5s infinite;
}
</style>
""",unsafe_allow_html=True)


refresh_interval = 10 # seconds


def load_data():
    file_name = "system_with_agent_response.csv"
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    else:
        # Fallback dummy data generation so your UI doesn't crash if the backend pipeline hasn't run yet
        st.warning(f" '{file_name}' not found. Displaying real-time placeholder stream.")
        return pd.DataFrame([{
            "Timestamp": pd.Timestamp.now(), "CPU_Usage": 25.0, "RAM_Usage": 45.0, 
            "Disk_Usage": 30.0, "Severity": "NORMAL", "Anomaly": 0, 
            "Risk_Prediction": 0, "Agent_Response": "System operating normally."
        }])

def create_graph(df, metric, title):
    fig = go.Figure()

    normal = df[df["Severity"] == "NORMAL"]
    if not normal.empty:
        fig.add_trace(go.Scatter(
            x=normal["Timestamp"], y=normal[metric],
            mode="lines+markers", name="Normal",
            marker=dict(color="green", size=5),
            line=dict(color="green"),
            customdata=normal[["CPU_Usage", "RAM_Usage", "Disk_Usage", "Severity"]],
            hovertemplate="Time: %{x}<br>" + f"{metric}: %{{y:.2f}}%<br>" +
                          "CPU: %{customdata[0]:.2f}%<br>RAM: %{customdata[1]:.2f}%<br>" +
                          "Disk: %{customdata[2]:.2f}%<br>Severity: %{customdata[3]}<extra></extra>"
        ))

    medium = df[df["Severity"] == "MEDIUM"]
    if not medium.empty:
        fig.add_trace(go.Scatter(
            x=medium["Timestamp"], y=medium[metric],
            mode="markers", name="Medium Alert",
            marker=dict(color="orange", size=10),
            customdata=medium[["CPU_Usage", "RAM_Usage", "Disk_Usage", "Severity"]],
            hovertemplate="Time: %{x}<br>" + f"{metric}: %{{y:.2f}}%<br>" +
                          "CPU: %{customdata[0]:.2f}%<br>RAM: %{customdata[1]:.2f}%<br>" +
                          "Disk: %{customdata[2]:.2f}%<br>Severity: %{customdata[3]}<extra></extra>"
        ))

    high = df[df["Severity"] == "HIGH"]
    if not high.empty:
        fig.add_trace(go.Scatter(
            x=high["Timestamp"], y=high[metric],
            mode="markers", name="High Alert",
            marker=dict(color="red", size=12),
            customdata=high[["CPU_Usage", "RAM_Usage", "Disk_Usage", "Severity"]],
            hovertemplate="Time: %{x}<br>" + f"{metric}: %{{y:.2f}}%<br>" +
                          "CPU: %{customdata[0]:.2f}%<br>RAM: %{customdata[1]:.2f}%<br>" +
                          "Disk: %{customdata[2]:.2f}%<br>Severity: %{customdata[3]}<extra></extra>"
        ))

    fig.update_layout(title=title, xaxis_title="Time", yaxis_title=f"{metric} (%)", hovermode="closest")
    return fig  

placeholder = st.empty()

while True:
    df = load_data()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    latest = df.iloc[-1]

    with placeholder.container():
        st.subheader("Live Resource Status")
        col1, col2, col3 = st.columns(3)

        col1.metric("CPU Usage (%)",f"{round(latest["CPU_Usage"], 2)} %")
        col2.metric("RAM Usage", f"{round(latest['RAM_Usage'], 2)} %")
        col3.metric("Disk Usage", f"{round(latest['Disk_Usage'], 2)} %")

        st.subheader("Historical Logs Summary")
        normal_count = (df["Severity"] == "NORMAL").sum()
        medium_count = (df["Severity"] == "MEDIUM").sum()
        high_count = (df["Severity"] == "HIGH").sum()

        col_c1, col_c2, col_c3 = st.columns(3)
        col_c1.metric("🟢 Normal Logs", normal_count)
        col_c2.metric("🟡 Medium Alerts", medium_count)
        col_c3.metric("🔴 High Alerts", high_count)

        st.subheader(" Resource Allocations & Live Metric Breakdowns")

        layout_col1, layout_col2 = st.columns([1, 2])
        
        with layout_col1:
            pie_data = {
                "Resource": ["CPU", "RAM", "Disk"],
                "Usage": [latest["CPU_Usage"], latest["RAM_Usage"], latest["Disk_Usage"]]
            }
            fig_pie = px.pie(pd.DataFrame(pie_data), names="Resource", values="Usage", title="Instantaneous Load Balance")
            st.plotly_chart(fig_pie, use_container_width=True)

        with layout_col2:
            # FIX: Swapped columns out for the proper naming variable 'Risk_Prediction'
            fig_pred = go.Figure()
            if "Risk_Prediction" in df.columns:
                fig_pred.add_trace(go.Scatter(x=df["Timestamp"], y=df["Risk_Prediction"], mode="lines", name="Failure Probability", line=dict(color="purple", width=3)))
            fig_pred.update_layout(title=" Predictive Machine Learning Risk Matrix", yaxis_title="Risk Scale (0=Safe, 1=Imminent Failure)", xaxis_title="Time")
            st.plotly_chart(fig_pred, use_container_width=True, key="prediction_chart")


        graph_col1, graph_col2 = st.columns(2)
        with graph_col1:
            st.plotly_chart(create_graph(df, "CPU_Usage", " Time Series CPU Load Data"), use_container_width=True, key="cpu_live")
            st.plotly_chart(create_graph(df, "RAM_Usage", " Time Series Memory Load Data"), use_container_width=True, key="ram_live")
        with graph_col2:
            st.plotly_chart(create_graph(df, "Disk_Usage", " Time Series Disk Consumption Data"), use_container_width=True, key="disk_live")

        st.subheader(" Agentic AI Resolution Engine Insights")
        severity_status = latest["Severity"]
        
        if severity_status == "NORMAL":
            st.markdown("""<div style="background-color:#d4edda; padding:20px; border-radius:12px; border-left:8px solid green; font-size:18px; color:#155724;">
                🟢 <b>HEALTH MONITOR STATE: EXCELLENT</b><br>No anomalous infrastructure deviations recorded. All processes are balanced.
                </div>""", unsafe_allow_html=True)
            st.success(f"Agent Feedback: {latest['Agent_Response']}")
        elif severity_status == "MEDIUM":
            st.markdown("""<div style="background-color:#fff3cd; padding:20px; border-radius:12px; border-left:8px solid #ffc107; font-size:18px; color:#856404;">
                🟡 <b>HEALTH MONITOR STATE: WARNING (MEDIUM RISKS DETECTED)</b><br>Unusual activity signature observed. System resource fluctuations under review.
                </div>""", unsafe_allow_html=True)
            st.warning(f"Agent Recommendation: {latest['Agent_Response']}")
        else:
            st.markdown("""<div style="background-color:#f8d7da; padding:20px; border-radius:12px; border-left:8px solid red; font-size:18px; color:#721c24;">
                🔴 <b>HEALTH MONITOR STATE: CRITICAL ALERT (HIGH IMPENDING COLLAPSE RISK)</b><br>Catastrophic performance indicators recorded. System stability is compromised.
                </div>""", unsafe_allow_html=True)
            st.error(f"Agent Action Plan: {latest['Agent_Response']}")

        with st.expander(" View Complete Real-Time Session Audit Trail"):
            st.dataframe(df.tail(20), use_container_width=True)

        if latest["Anomaly"] == 1:
            st.markdown('<div class="alert-box"> INTERRASTRUCTURE ANOMALY SIGNATURE DETECTED </div>', unsafe_allow_html=True)
    time.sleep(refresh_interval)
    st.rerun()