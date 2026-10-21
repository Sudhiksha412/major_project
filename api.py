from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psutil
import os
from datetime import datetime
import json

from agent_logic import AgenticAIResolutionEngine, tool_free_ram, tool_optimize_cpu, tool_clean_disk_space, tool_reset_network_adapter

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


agent_engine = AgenticAIResolutionEngine(machine_profile="Intel Core i3, 8GB RAM")
current_active_session = {}

class UserApprovalSchema(BaseModel):
    decision: str 

@app.get("/")
def root():
    return {"message": "Autonomous Infrastructure Operations API is running", "status": "online"}

@app.get("/system-status")
def system_status():
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage(os.path.abspath(os.sep)).percent
    network = psutil.net_io_counters()
    
    
    future_anomaly = 1 if (ram > 80 or cpu > 70) else 0
    top_reason = "RAM_Usage" if ram > 80 else ("CPU_Usage" if cpu > 70 else "None")
    
    
    future_anomaly = 1 
    top_reason = "RAM_Usage"

   
    ai_analysis = {}
    if future_anomaly == 1 and not current_active_session.get("active"):
        report_snapshot = {
            "Future_Anomaly_Predicted": 1,
            "Top_Reason": top_reason,
            "Metrics_Snapshot": {"CPU": cpu, "RAM": ram, "Disk": disk}
        }
        
        brain_response = agent_engine.call_gemini_brain(report_snapshot)
        if brain_response:
            current_active_session["active"] = True
            current_active_session["recommended_tool"] = brain_response.get("recommended_tool")
            current_active_session["explanation"] = brain_response.get("explanation")
            current_active_session["manual_steps"] = brain_response.get("manual_steps")
            current_active_session["top_reason"] = top_reason

    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": round(cpu, 2),
        "ram": round(ram, 2),
        "disk": round(disk, 2),
        "bytes_sent": network.bytes_sent,
        "bytes_recv": network.bytes_recv,
        "processes": len(psutil.pids()),
        
        "agent_active_alert": current_active_session.get("active", False),
        "agent_explanation": current_active_session.get("explanation", ""),
        "agent_recommended_tool": current_active_session.get("recommended_tool", "TOOL_NONE"),
        "agent_manual_steps": current_active_session.get("manual_steps", [])
    }

@app.post("/action-confirm")
def action_confirm(payload: UserApprovalSchema):
    """React UI Button click handles operational tools execution pathways."""
    if not current_active_session.get("active"):
        raise HTTPException(status_code=400, detail="No active agent decision pending.")
        
    decision = payload.decision.lower()
    tool = current_active_session.get("recommended_tool")
    
    execution_result = ""
    if decision == "yes":
        if tool == "TOOL_RAM": execution_result = tool_free_ram()
        elif tool == "TOOL_CPU": execution_result = tool_optimize_cpu()
        elif tool == "TOOL_DISK": execution_result = tool_clean_disk_space()
        elif tool == "TOOL_NETWORK": execution_result = tool_reset_network_adapter()
        else: execution_result = "Notification: Analysis structure verified. No internal tool mapping."
    else:
        execution_result = "Fallback Sequence Initiated: Manual instructions framework mapped to user display dashboard."
        
   
    current_active_session.clear()
    return {"status": "processed", "result": execution_result}
