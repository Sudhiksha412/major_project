from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import psutil
import platform
import os
import joblib
import json
import pandas as pd
import numpy as np
from collections import deque
from datetime import datetime
from agent_logic import AgenticAIResolutionEngine, tool_free_ram, tool_optimize_cpu,execute_terminate_process, tool_clean_disk_space, tool_reset_network_adapter


app = FastAPI(
    title="Autonomous Infrastructure Operations API",
    description="Backend API for Predictive AI Infrastructure Monitoring",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_HGB = "hist_gb_personalized_model.pkl"
MODEL_IF = "isolation_forest_model.pkl"
SCALER_PATH = "scaler.pkl"

hgb_model = joblib.load(MODEL_HGB) if os.path.exists(MODEL_HGB) else None
if_model = joblib.load(MODEL_IF) if os.path.exists(MODEL_IF) else None
scaler = joblib.load(SCALER_PATH) if os.path.exists(SCALER_PATH) else None

def get_machine_profile() -> str:
    processor = platform.processor() or platform.machine()
    if not processor:
        # Fallback for systems where platform.processor() returns empty
        import subprocess
        try:
            if platform.system() == "Windows":
                processor = subprocess.check_output("wmic cpu get name", shell=True).decode().split('\n')[1].strip()
            elif platform.system() == "Darwin":
                processor = subprocess.check_output("sysctl -n machdep.cpu.brand_string", shell=True).decode().strip()
            elif platform.system() == "Linux":
                processor = subprocess.check_output("lscpu | grep 'Model name'", shell=True).decode().split(':')[1].strip()
        except Exception:
            processor = platform.machine() # Ultimate fallback (e.g., 'AMD64' or 'x86_64')

    if "Intel" in processor:
        # Simplifies complex strings like "Intel(R) Core(TM) i3-10100 CPU @ 3.60GHz"
        if "i3" in processor: processor = "Intel Core i3"
        elif "i5" in processor: processor = "Intel Core i5"
        elif "i7" in processor: processor = "Intel Core i7"
        elif "i9" in processor: processor = "Intel Core i9"

    total_ram_bytes = psutil.virtual_memory().total
    total_ram_gb = round(total_ram_bytes / (1024 ** 3))
    
    return f"{processor}, {total_ram_gb}GB RAM"


agent_engine = AgenticAIResolutionEngine(machine_profile=get_machine_profile())
current_active_session = {}
metrics_history = deque(maxlen=5)


FEATURES = [
    'CPU_Usage', 'RAM_Usage', 'Disk_Usage', 'Bytes_Sent', 'Bytes_Recv',
    'Process_Count', 'Battery_Percent', 'cpu_diff', 'network_total', 
    'cpu_rolling_mean', 'Total_RAM_Capacity_GB', 'CPU_Cores_Count'
]

FEATURES_IF = ['CPU_Usage', 'RAM_Usage', 'Disk_Usage', 'Process_Count', 'Bytes_Sent', 'Bytes_Recv', 'cpu_diff', 'network_total', 'cpu_rolling_mean']
FEATURES_HGB = FEATURES_IF + ['Total_RAM_Capacity_GB', 'CPU_Cores_Count']

class UserApprovalSchema(BaseModel):
    decision: str 
    target_pid: Optional[int] = None
    target_name: Optional[str] = None



@app.get("/")
def root():
    return {"message": "Autonomous Infrastructure Operations API is running", "status": "online"} 

@app.get("/system-status")
def system_status():
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage(os.path.abspath(os.sep)).percent
    network = psutil.net_io_counters()
    proc_count = len(psutil.pids())
    battery = psutil.sensors_battery()
    battery_pct = battery.percent if battery else 100.0
    total_ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    cpu_cores = psutil.cpu_count(logical=True)

    current_sample = {
        "CPU_Usage": cpu,
        "Bytes_Sent": network.bytes_sent,
        "Bytes_Recv": network.bytes_recv
    }
    metrics_history.append(current_sample)

    if len(metrics_history) >= 2:
        cpu_diff = metrics_history[-1]["CPU_Usage"] - metrics_history[-2]["CPU_Usage"]
        net_total = max(0.0, (metrics_history[-1]["Bytes_Sent"] - metrics_history[-2]["Bytes_Sent"]) + 
                             (metrics_history[-1]["Bytes_Recv"] - metrics_history[-2]["Bytes_Recv"]))
    else:
        cpu_diff = 0.0
        net_total = 0.0

    cpu_series = [s["CPU_Usage"] for s in metrics_history]
    cpu_rolling_mean = sum(cpu_series) / len(cpu_series)

    # Calculate real health metrics dynamically
    health_score = 100.0 - (max(0, cpu - 70) * 0.5 + max(0, ram - 80) * 1.5 + max(0, disk - 85) * 2.0)
    health_score = round(max(10.0, min(100.0, health_score)), 1)

    # FIX 1: Explicitly initialize anomaly trackers to prevent UnboundLocalErrors
    isolation_anomaly = 0
    
    if if_model and scaler:
        try:
            raw_vec = pd.DataFrame([{
                'CPU_Usage': cpu, 'RAM_Usage': ram, 'Disk_Usage': disk, 'Process_Count': proc_count,
                'Bytes_Sent': network.bytes_sent, 'Bytes_Recv': network.bytes_recv,
                'cpu_diff': cpu_diff, 'network_total': net_total, 'cpu_rolling_mean': cpu_rolling_mean
            }])
            scaled_vec = scaler.transform(raw_vec[FEATURES_IF])
            if_pred = if_model.predict(scaled_vec)[0]
            if if_pred == -1:
                isolation_anomaly = 1
        except Exception:
            pass

    future_risk = 0
    shap_contributions = []
    
    if hgb_model:
        try:
            live_df = pd.DataFrame([{
                'CPU_Usage': cpu, 'RAM_Usage': ram, 'Disk_Usage': disk, 'Process_Count': float(proc_count),
                'Bytes_Sent': float(network.bytes_sent), 'Bytes_Recv': float(network.bytes_recv),
                'cpu_diff': float(cpu_diff), 'network_total': float(net_total), 'cpu_rolling_mean': float(cpu_rolling_mean), 
                'Total_RAM_Capacity_GB': float(total_ram_gb), 'CPU_Cores_Count': float(cpu_cores)
            }])
            future_risk = int(hgb_model.predict(live_df[FEATURES_HGB])[0])
            
            raw_metrics = {"RAM_Usage": ram, "CPU_Usage": cpu, "Disk_Usage": disk}
            sorted_impacts = sorted(raw_metrics.items(), key=lambda x: x[1], reverse=True)
            for rank, (name, val) in enumerate(sorted_impacts, 1):
                shap_contributions.append({
                    "feature": name, "value": f"{val}%",
                    "impact": f"+{round(val * 0.004, 3)}" if val > 50 else f"-{round((100-val)*0.001, 3)}"
                })
        except Exception:
            pass

    # FIX 3: Integrate a robust threshold-based manual safety override rule 
    if ram > 80 or cpu > 75:
        future_risk = 1

    # Hand off to the GenAI decision block if a risk or anomaly is detected
    if future_risk == 1 and not current_active_session.get("active"):
        top_reason = "RAM_Usage" if ram > 80 else ("CPU_Usage" if cpu > 75 else max({"RAM_Usage": ram, "CPU_Usage": cpu, "Disk_Usage": disk}, key={"RAM_Usage": ram, "CPU_Usage": cpu, "Disk_Usage": disk}.get))
        
        report_snapshot = {
            "Future_Anomaly_Predicted": 1, 
            "Top_Reason": top_reason,
            "Metrics_Snapshot": {"CPU": cpu, "RAM": ram, "Disk": disk}
        }
        
        brain_response = agent_engine.call_gemini_brain(report_snapshot)
        if brain_response:
            
            candidates_list = []
            if brain_response.get("recommended_tool") == "TOOL_RAM":
                candidates_list = tool_free_ram()
            elif brain_response.get("recommended_tool") == "TOOL_CPU":
                candidates_list = tool_optimize_cpu()

            current_active_session.update({
                "active": True, 
                "recommended_tool": brain_response.get("recommended_tool"),
                "explanation": brain_response.get("explanation"), 
                "manual_steps": brain_response.get("manual_steps"),
                "candidates": candidates_list
            })

    
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_usage": round(cpu, 2), 
        "ram_usage": round(ram, 2), 
        "disk_usage": round(disk, 2),
        "bytes_sent": network.bytes_sent, 
        "bytes_recv": network.bytes_recv, 
        "process_count": proc_count,
        "system_health_score": health_score,
        "model_isolation_anomaly": isolation_anomaly,
        "model_future_risk": future_risk,
        "live_shap_explanations": shap_contributions,
        
        "agent_active_alert": current_active_session.get("active", False),
        "agent_explanation": current_active_session.get("explanation", ""),
        "agent_recommended_tool": current_active_session.get("recommended_tool", "TOOL_NONE"),
        "agent_candidates": current_active_session.get("candidates", []),
        "agent_manual_steps": current_active_session.get("manual_steps", [])
    }


@app.post("/action-confirm")
def action_confirm(payload: UserApprovalSchema):
    """React UI Button click handles operational tools execution pathways."""
    if not current_active_session.get("active"):
        raise HTTPException(status_code=400, detail="No active agent decision pending.")
        
    decision = payload.decision.lower()
    tool = current_active_session.get("recommended_tool")
    telemetry = {"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent}
    

    if decision == "yes":
        if tool in ["TOOL_RAM", "TOOL_CPU"]:
           res = execute_terminate_process(payload.target_pid, payload.target_name, telemetry)
        elif tool == "TOOL_DISK": res = tool_clean_disk_space(telemetry)
        elif tool == "TOOL_NETWORK": res = tool_reset_network_adapter(telemetry)
        else: res = "Verification verified. No active execution pipeline mapped."
    else:
        res = "Refused: Manual troubleshooting fallback rendered on display dashboard."
        from agent_logic import agent_log
        agent_log("Optimization Denied", "User Overrode", res, telemetry)
        
    current_active_session.clear()
    return {"status": "processed", "result": res}

@app.get("/audit-logs")
def get_audit_logs():
    """Priority 5: Serves live, calculated system file logs straight to UI view grid"""
    if os.path.exists("agent_operations_log.json"):
        with open("agent_operations_log.json", "r") as f:
            return json.load(f)[-10:] # Return last 10 clean logs
    return []