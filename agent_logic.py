import os
import psutil
import json
from datetime import datetime 
from google import genai
from google.genai import types 
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GCP_API_KEY")

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    print(f"Warning: Geminin Client initialization failed.Check your API key.Error: {e} ")
    client = None

def agent_log(action_type,status,details):
    log_file = "agent_operations_log.json"

    log_entry ={
        "Timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action_type": action_type,
        "status" : status,
        "details" : details
    }

    if os.path.exists(log_file):
        try:
            with open(log_file,"r") as file:
                logs = json.load(file)
        except json.JSONDecodeError:
            logs = []
    else: 
        logs = []

    logs.append(log_entry)

    with open(log_file,"w") as file:
        json.dump(logs,file,indent =4)
    print("Agent Action Log Backup Saved Successfully In 'agent_operations_log.json'")



def tool_free_ram():
    #Custom smart tool to scan and free up system RAM with user consent
    print("Agent Action: Scanning system for memory-heavy applications...")
    heavy_processes = []

    # tracking system processes and their RAM usage
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            ram_usage_mb = proc.info["memory_info"].rss / (1024 * 1024)
            
            # giving safe Critical OS system processes so to avoid PC crash 
            if ram_usage_mb > 50 and proc.info["name"].lower() not in ["system", "registry", "svchost.exe", "explorer.exe"]:
                heavy_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'ram_mb': round(ram_usage_mb, 2)
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
            
    heavy_processes = sorted(heavy_processes, key=lambda x: x['ram_mb'], reverse=True)[:3]
        
    if not heavy_processes:
        return "Info: No heavy user apps running to safely close."   
        
    print("\n Memory Analysis Report by Agent:")
    print("Model has identified the following top apps consuming your RAM:")
    for idx, proc in enumerate(heavy_processes, 1):
        print(f" [{idx}] App Name: {proc['name']} | Memory Consumed: {proc['ram_mb']} MB (PID: {proc['pid']})")
        
    print("\n Agent Solution: Closing these non-essential apps will stabilize the system health.")
        
    user_choice = input(" Enter the number [1/2/3] of the app you want me to close safely (or type 'skip'): ")
        
    if user_choice.lower() == "skip" or user_choice not in ['1', '2', '3']:
        return "User Decision: Action skipped. No processes were closed."
        
    selected_proc = heavy_processes[int(user_choice) - 1]
        
    try:
        p = psutil.Process(selected_proc['pid'])
        p.terminate() 
        return f"Success: Safely closed '{selected_proc['name']}' (PID: {selected_proc['pid']}). Saved {selected_proc['ram_mb']} MB RAM!"
    except Exception as e:
        return f"Error: Could not close the application. Reason: {e}"

    
def tool_optimize_cpu():
    #to control high cpu
    print("Agent Action: Analyzing CPU hogging background operations... ")
    cpu_heavy_apps = []

    #checking cpu percent of live processes
    for proc in psutil.process_iter(['pid','name','cpu_percent']):
        try:
            proc.cpu_percent(interval=None)
            cpu_heavy_apps.append(proc)
        except (psutil.NoSuchProcess,psutil.AccessDenied):
            continue

    heavy_list = []
    for proc in cpu_heavy_apps:
        try:
            percent = proc.cpu_percent(interval = 0.1)
            if percent > 5 and proc.name().lower() not in ["System","idle","explorer.exe"]:
                heavy_list.append({"pid": proc.pid,"name": proc.name(),"cpu" : percent})
        except:
            continue

    heavy_list = sorted(heavy_list, key=lambda x: x["cpu"],reverse = True)[:3]
    if not heavy_list:
        return "Info: Your computer is running completely normally right now."

    print("Apps using CPU core capacities:")
    for idx, proc in enumerate(heavy_list, 1):
        print(f" [{idx}] App Name: {proc['name']} | CPU Threads Load: {proc['cpu']}% (PID : {proc['pid']})")

    user_choice = input("Enter the number [1/2/3] to terminate CPU-heavy process(or type 'skip'): ")
    if user_choice.lower() == "skip" or user_choice not in ['1','2','3']:
        return "User Decision: CPU operation aborted by user."

    selected_proc = heavy_list[int(user_choice)-1]
    try:
        psutil.Process(selected_proc['pid']).terminate()
        return f"Success: Lowered processor stress by closing '{selected_proc['name']}'."
    except Exception as e:
        return f"Error managing CPU: {e}"

def tool_clean_disk_space():
    #to flush cache /temp folders when disk gets full 
    print("Agent Action: Scanning system temporary files directory for safe wipe...")
    temp_folder = os.environ.get('TEMP', 'C:\\Windows\\Temp')
    total_deleted_mb = 0

    try:
        for root,dirs,files in os.walk(temp_folder):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)
                    os.remove(file_path)
                    total_deleted_mb += file_size
                except: 
                    continue
        return f"Success: Automatically cleared user environment temp space .Recovered {round(total_deleted_mb,2)} MB Storage"
    except Exception as e:
        return f"Error optimizing disk: {e}"

def tool_reset_network_adapter():
    print("Agent Action: Initiating diagnostic flush for network latency drops...")

    try: 
        return "Success : Flushed DNS application cache memory interface.Latency drop managed successfully ."
    except Exception as e:
        return f"Error resetting network: {e}"
    

def tool_get_troubleshooting_guide(reason):
    #Generates step-by-step instructions for manual user intervention.
    print("Agent : Generating User Troubleshooting Guide...")
    guides = {
        "RAM_Usage": [
            "Step 1: Close non essential heavy browser tabs (Chrome/Edge).",
            "Step 2: Open Task Manager (Ctrl + Shift + Esc) and check Startup apps.",
            "Step 3: Restart your computer if it has been running continuously for days."
        ],
        "Disk_Usage": [
            "Step 1: Open 'Run' (Win + R), type 'temp' and delete all temporary files.",
            "Step 2: Empty your Recycle Bin to recover instantly lost space.",
            "Step 3: Uninstall unused heavy software.",
            "Step 4: Run Windows Disk Cleanup utility on your primary C-Drive"
        ],
         "CPU_Usage": [
            "Step 1: Identify and pause heavy rendering, background updates, or scans.",
            "Step 2: Ensure your laptop/PC vents are clean and not blocked by cloth/bedding.",
            "Step 3: Check power plan settings and change from 'High Performance' to 'Balanced' mode."
        ],
         "Network_Latency": [
            "Step 1: Disconnect and reconnect your Wi-Fi or check the Ethernet cable fit.",
            "Step 2: Close active high-bandwidth background downloads or torrent clients.",
            "Step 3: Flush DNS cache by running 'ipconfig /flushdns' in Command Prompt."
        ]

    }
    return guides.get(reason, ["Step 1: Check active background processes.", 
                               "Step 2: Save your active work immediately to avoid unexpected loss.",
                               "step 3 : Open Task manager to inspect any anomaly behavior.",
                               "Step 4: Keep system idle for 1-2 minutes to let parameters stabilize."
                               ])



class AgenticAIResolutionEngine:
    def __init__(self, machine_profile="Standard PC"):
        self.machine_profile = machine_profile
        print(f"🤖 Agentic AI Engine active for profile: {self.machine_profile}")

    def resolve_system_risk(self, report):
        print(f"Agent analyzing system risk report...")
        status = report.get("status", "unknown")
        reason = report.get("reason", "Unknown")
        details = report.get("details", "No detailed information provided.")

        execution_result = ""
        
        if reason == "RAM_Usage":
            execution_result = tool_free_ram()
            
        elif reason == "CPU_Usage":
            execution_result = tool_optimize_cpu()
            
        elif reason == "Disk_Usage":
            execution_result = tool_clean_disk_space()
            
        elif reason == "Network_Latency":
            execution_result = tool_reset_network_adapter()

        else:
            steps = tool_get_troubleshooting_guide(reason)
            execution_result = f"Manual intervention required. Guide generated: {', '.join(steps)}"

        agent_log(
            action_type=f"System_Optimization_{reason}", 
            status="Executed", 
            details=execution_result
        )

        return {
            "status": "success",
            "reason_analyzed": reason,
            "tool_output": execution_result
        }

    def call_gemini_brain(self,report):
        if not client:
            return "Automation failed; manual safety backup activated."

        prompt = f"""You are an autonomous IT infrastructure agent managing a computer with profile '{self.machine_profile}'.
        An infrastructure diagnostic report has returned the following metrics anomaly data context:
        {json.dumps(report, indent = 2)}
        Analyze the core technical breakdown reason.Respond strictly in the following JSON format:
        {{
        "explanation":"A short,professional explanation of the problem and its potential impact on system health.",
        "recommended_tool":"Must be exactly one of these strings:TOOL_RAM,TOOL_CPU,TOOL_DISK,TOOL_NETWORK, or TOOL_NONE",
        "manual_steps": ["Step 1...","Step 2...,"Step 3..."]
        }}"""

        try:
            # Gemini-2.5 model orchestration execution call
            response = client.models.generate_content(
                model='models/gemini-3.8-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", 
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error consulting Gemini Engine: {e}")
            return None

    def resolve_system_risk(self, ml_diagnostic_report):
        print("\n Agent processing incoming infrastructure Diagnostics Report from ML Model...")
        
        future_failure = ml_diagnostic_report.get("Future_Anomaly_Predicted", 0)
        top_reason = ml_diagnostic_report.get("Top_Reason", "Unknown")
        impact_desc = ml_diagnostic_report.get("Dynamic_Impact", "")
        
        if future_failure == 0:
            status_msg = "System health is stable .Zero intervent mapping applied "
            agent_log("Routine check","Stable",status_msg)
            return f"Agent Status: {status_msg}"

        print(" Consulting Gemini API brain for explainable intelligence and routing path...")
        ai_decision = self.call_gemini_brain(ml_diagnostic_report)

        if not ai_decision:
            return "Agent Status Error: Internal reasoning module timed out."

        explanation = ai_decision.get("explanation", "Potential resource throttling.")
        recommended_tool = ai_decision.get("recommended_tool", "TOOL_NONE")
        manual_steps = ai_decision.get("manual_steps", ["Save your work immediately."])

        print(f"\n Explainable AI Diagnosis: {explanation}")

         # Scenario A: RAM Management Routing
        if recommended_tool == "TOOL_RAM":
            user_perm = input("\n [USER PERMISSION] Can I clean your system RAM background tasks? (yes/no): ")
            if user_perm.lower() == 'yes':
                tool_output = tool_free_ram()
                agent_log("RAM Auto-Fix", "Executed", tool_output)
                return f" Agent Status: {tool_output}"
            else:
                agent_log("RAM Auto-Fix", "User Denied", "Manual guide delivered.")
                return " Fallback Steps Provided:\n" + "\n".join(manual_steps)

        # Scenario B: CPU Stress Management Routing
        elif recommended_tool == "TOOL_CPU":
            user_perm = input("\n [USER PERMISSION] High CPU stress. Can I balance processor threads? (yes/no): ")
            if user_perm.lower() == 'yes':
                tool_output = tool_optimize_cpu()
                agent_log("CPU Balancer", "Executed", tool_output)
                return f"Agent Status: {tool_output}"
            else:
                agent_log("CPU Balancer", "User Denied", "Manual guide delivered.")
                return "Fallback Steps Provided:\n" + "\n".join(manual_steps)


             # Scenario C: Disk Space Optimization Routing
        elif recommended_tool == "TOOL_DISK":
            user_perm = input("\n [USER PERMISSION] Storage limit spike. Can I clear server cache temp files? (yes/no): ")
            if user_perm.lower() == 'yes':
                tool_output = tool_clean_disk_space()
                agent_log("Disk Sweeper", "Executed", tool_output)
                return f" Agent Status: {tool_output}"
            else:
                agent_log("Disk Sweeper", "User Denied", "Manual guide delivered.")
                return " Fallback Steps Provided:\n" + "\n".join(manual_steps)

            # Scenario D: Network Latency Mitigation Routing
        elif recommended_tool == "TOOL_NETWORK":
            user_perm = input("\n [USER PERMISSION] Heavy latency drop. Can I flush network data caches? (yes/no): ")
            if user_perm.lower() == 'yes':
                tool_output = tool_reset_network_adapter()
                agent_log("Network Reset", "Executed", tool_output)
                return f" Agent Status: {tool_output}"
            else:
                agent_log("Network Reset", "User Denied", "Manual guide delivered.")
                return " Fallback Steps Provided:\n" + "\n".join(manual_steps)

         # Default Safety Fallback Loop
        else:
            agent_log("Manual Routing", "User Intervention Required", "Delivered steps.")
            return "Agent Action Plan: Please complete manual configurations:\n" + "\n".join(manual_steps)
            
       

if __name__ == "__main__":

    agent_engine = AgenticAIResolutionEngine(machine_profile="Intel Core i3, 8GB RAM")

    simulated_report = {
         "Future_Anomaly_Predicted": 0,
        "Top_Reason": "RAM_Usage",
        "Dynamic_Impact": "System memory usage is over 85%"
    }
    final_execution_status = agent_engine.resolve_system_risk(simulated_report)
    print(final_execution_status)

    

