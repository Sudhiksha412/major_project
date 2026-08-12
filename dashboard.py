import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

st.set_page_config(page_title="AI System Monitor", layout="wide")

st.title("AI-Based System Monitoring Dashboard")

refresh_interval = 10 # seconds


def load_data():
    return pd.read_csv("system_with_agent_response.csv")


placeholder = st.empty()

while True:
    df = load_data()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    latest = df.iloc[-1]

    with placeholder.container():

        
        col1, col2, col3 = st.columns(3)

        col1.metric("CPU Usage (%)", round(latest["CPU_Usage"], 2))
        col2.metric("RAM Usage (%)", round(latest["RAM_Usage"], 2))
        col3.metric("Disk Usage (%)", round(latest["Disk_Usage"], 2))

        
        def get_severity(row):
            if row["CPU_Usage"] > 80 or row["RAM_Usage"] > 85:
                return "HIGH"
            elif row["CPU_Usage"] > 60:
                return "MEDIUM"
            else:
                return "LOW"

        df["Severity"] = df.apply(get_severity, axis=1)

        
        def create_graph(metric, title):

            fig = go.Figure()

            
            normal = df[df["Anomaly"] == 0]
            fig.add_trace(go.Scatter(
                x=normal["Timestamp"],
                y=normal[metric],
                mode='lines',
                name='Normal',
                hovertemplate=f"{metric}: %{{y}}<extra></extra>"
            ))

            
            anomalies = df[df["Anomaly"] == 1]
            fig.add_trace(go.Scatter(
                x=anomalies["Timestamp"],
                y=anomalies[metric],
                mode='markers',
                marker=dict(size=8, color='red'),
                name='Anomaly',
                hovertemplate=f"{metric}: %{{y}}<extra></extra>"
            ))

            fig.update_layout(
                title=title,
                xaxis_title="Time",
                yaxis_title=metric,
                hovermode="x unified"
            )

            return fig

        
        st.subheader("System Metrics (Live)")

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(create_graph("CPU_Usage", "CPU Usage"), use_container_width=True, key="cpu")

            st.plotly_chart(create_graph("RAM_Usage", "RAM Usage"), use_container_width=True, key="ram")

        with col2:
            st.plotly_chart(create_graph("Disk_Usage", "Disk Usage"), use_container_width=True, key="disk")

        
        st.subheader("Agent Insights")

        if latest["Anomaly"] == 1:
            st.error(f"{latest['Agent_Response']}")
        else:
            st.success("System Operating Normally")

       
        with st.expander("View Recent Logs"):
            st.dataframe(df.tail(20))

    

    time.sleep(refresh_interval)
    st.rerun()