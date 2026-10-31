import { useState, useEffect, Suspense } from "react";
import {
  Activity,
  BrainCircuit,
  Cpu,
  HardDrive,
  LayoutDashboard,
  Network,
  ShieldAlert,
  Terminal,
  Bot,
  Menu,
  X,
  CheckCircle,
  AlertTriangle
} from "lucide-react";

import Infrastructure3D from "./components/Infrastructure3D";
import "./App.css";
import { getSystemStatus } from "./services/api";

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [system, setSystem] = useState(null);
  const [logs, setLogs] = useState([]);
  const [isOnline, setIsOnline] = useState(false);

  const fetchSystemData = async () => {
    try {
      const data = await getSystemStatus();
      if (data){ 
      setSystem(data);
      setIsOnline(true);
      } else {
        setIsOnline(false);
      } 

    } catch (error) {
      console.error("API ERROR:", error);
      setIsOnline(false);
    }
  };

  const fetchAuditLogs = async () => {
    try {
      const res = await fetch("http://localhost:8000/audit-logs");
      const data = await res.json();
      setLogs(data.reverse());
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchSystemData();
    fetchAuditLogs();
    const interval = setInterval(() => {
      fetchSystemData();
      if (activePage === "System Logs") fetchAuditLogs();
    }, 2000);
    return () => clearInterval(interval);
  }, [activePage]);

  const navigation = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "Live Monitor", icon: Activity },
    { name: "Predictions", icon: BrainCircuit },
    { name: "Anomalies", icon: ShieldAlert },
    { name: "Agentic AI", icon: Bot },
    { name: "System Logs", icon: Terminal },
  ];

  return (
    <div className="app">
      <div className="background-grid"></div>
      <div className="background-glow glow-one"></div>
      <div className="background-glow glow-two"></div>

      <button className="mobile-menu" onClick={() => setMobileMenu(!mobileMenu)}>
        {mobileMenu ? <X /> : <Menu />}
      </button>

      <aside className={`sidebar ${mobileMenu ? "open" : ""}`}>
        <div className="brand">
          <div className="brand-core"><BrainCircuit size={24} /></div>
          <div>
            <h1>AI INFRA</h1>
            <span>USER SUPPORT</span>
          </div>
        </div>

        <div className={`system-status ${isOnline ? "online" : "offline"}`}>
          <span className="status-dot"></span>
          {isOnline ? "SYSTEM ONLINE" : "SERVER UNREACHABLE"}
        </div>

        <nav>
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.name}
                className={`nav-item ${activePage === item.name ? "active" : ""}`}
                disabled={!isOnline && item.name !== "System Logs"}
                onClick={() => {
                  setActivePage(item.name);
                  setMobileMenu(false);
                }}
              >
                <Icon size={19} />
                <span>{item.name}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="model-box">
            <span>ACTIVE MODEL</span>
            <strong>HIST GRADIENT BOOST</strong>
            <small>Isolation Forest + Explainable AI</small>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">AUTONOMOUS INFRASTRUCTURE</p>
            <h2>{activePage}</h2>
          </div>
          <div className="top-status">
            <div>
              <span className={`status-dot ${isOnline ? "active" : "inactive"}`}></span>
              {isOnline ? "Monitoring Active" : "Stream Disconnected"}
            </div>
            <div className="server-id">NODE-01</div>
          </div>
        </header>

        {!isOnline ? (
          <div className="api-error-fallback">
            <AlertTriangle size={40} color="#ff4a4a" />
            <h3>Data Stream Offline</h3>
            <p>Unable to connect to FastAPI endpoint at <code>http://localhost:8000/system-status</code>. Check backend runtime.</p>
          </div>
        ) : (
          <>

        {activePage === "Dashboard" && <Dashboard system={system} triggerRefresh={fetchSystemData} />}
        {activePage === "Live Monitor" && <LiveMonitor system={system} />}
        {activePage === "Predictions" && <Predictions system={system} />}
        {activePage === "Anomalies" && <Anomalies system={system} />}
        {activePage === "Agentic AI" && <AgenticAIView system={system} triggerRefresh={fetchSystemData} />}
        {activePage === "System Logs" && <SystemLogs />}
        </>
        )}
      </main>
    </div>
  );
}


function Dashboard({ system, triggerRefresh }) {
  const [actionMessage, setActionMessage] = useState("");
  const [selectedPid, setSelectedPid] = useState("");

  const handleAgentDecision = async (userChoice) => {
    let payload = { decision: userChoice };
    
    if (userChoice === "yes" && ["TOOL_RAM", "TOOL_CPU"].includes(system?.agent_recommended_tool)) {
      if (!selectedPid) {
        alert("Please select a target application profile to close safely.");
        return;
      }
      const targetObj = system.agent_candidates.find(c => c.pid === parseInt(selectedPid));
      payload.target_pid = targetObj.pid;
      payload.target_name = targetObj.name;
    }

    try {
      const response = await fetch("http://localhost:8000/action-confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision: userChoice })
      });
      const data = await response.json();
      setActionMessage(data.result);
      setSelectedPid("");
      triggerRefresh(); // Fetch latest optimized state metrics
      setTimeout(() => setActionMessage(""), 7000);
    } catch (err) {
      console.error("Action execution routing error:", err);
    }
  };

  const isProcessTool = ["TOOL_RAM", "TOOL_CPU"].includes(system?.agent_recommended_tool);


  return (
    <div className="dashboard">
      {system?.agent_active_alert && (
        <section className="agent-alert-banner">
          <div className="alert-header">
            <AlertTriangle color="#ff4a4a" size={24} />
            <h4>CRITICAL RISK SIGNATURE CAUGHT BY AGENTIC AI</h4>
          </div>
          <p className="alert-diagnosis"><strong>Diagnosis:</strong> {system.agent_explanation}</p>
          <p className="alert-action-call">Recommended Core Action Pipeline: <code>{system.agent_recommended_tool}</code></p>

          {isProcessTool && system.agent_candidates?.length > 0 && (
            <div className="process-safeguard-selection">
              <h5>Select Target Process to Terminate Safely:</h5>
              <div className="candidate-list">
                {system.agent_candidates.map((proc) => (
                  <label key={proc.pid} className={`candidate-row ${selectedPid === String(proc.pid) ? "selected" : ""}`}>
                    <input 
                      type="radio" 
                      name="candidate-pid" 
                      value={proc.pid} 
                      checked={selectedPid === String(proc.pid)}
                      onChange={(e) => setSelectedPid(e.target.value)}
                    />
                    <span><strong>{proc.name}</strong> (PID: {proc.pid}) Footprint: <code>{proc.metrics_value}</code></span>
                  </label>
                    ))}
              </div>
            </div>
          )}
          
          <div className="alert-action-footer">
            <span>Authorize internal execution mitigation framework tools?</span>
            <div className="btn-group">
              <button className="btn-approve" onClick={() => handleAgentDecision("yes")}>Allow Action</button>
              <button className="btn-deny" onClick={() => handleAgentDecision("no")}>Deny / View Manual Steps</button>
            </div>
          </div>
        </section>
      )}

      
      {actionMessage && (
        <div className="runtime-status-notification">
          <CheckCircle size={18} color="#4aff4a" />
          <span>{actionMessage}</span>
        </div>
      )}

      <section className="metrics">
        <MetricCard icon={<Cpu />} title="CPU Usage" value={system ? `${system.cpu_usage}%` : "--"} status={system?.cpu_usage > 70 ? "STRESS" : "NORMAL"} />
        <MetricCard icon={<Activity />} title="RAM Usage" value={system ? `${system.ram_usage}%` : "--"} status={system?.ram_usage > 80 ? "HIGH LOAD" : "NORMAL"} />
        <MetricCard icon={<HardDrive />} title="Disk Usage" value={system ? `${system.disk_usage}%` : "--"} status="NORMAL" />
        <MetricCard icon={<Network />} title="Network Activity" value={system ? `${system.process_count} Procs` : "--"} status="CONNECTED" />
      </section>

      <section className="visual-section">
        <div className="section-header">
          <div>
            <p className="eyebrow">LIVE INFRASTRUCTURE</p>
            <h3>System Intelligence Core</h3>
          </div>
          <div className="live-badge"><span className="pulse"></span>LIVE</div>
        </div>

      <div className="visual-layout">
          <div className="three-container">
            <Suspense fallback={<div style={{ color: '#a78bfa', padding: '20px', fontFamily: 'Space Mono', fontSize: '12px' }}>Loading 3D Core...</div>}>
            <Infrastructure3D />
            </Suspense>
          </div>
          
          <div className="health-panel">
            <div className="panel-heading">
              <span>SYSTEM HEALTH</span>
              <strong style={{ color: system?.agent_active_alert ? '#ff4a4a' : '#4aff4a' }}>
                {system?.agent_active_alert ? "72%" : "96%"}
              </strong>
            </div>
            <div className="health-bar">
              <div style={{ width: system?.agent_active_alert ? "72%" : "96%", backgroundColor: system?.agent_active_alert ? '#ff4a4a' : '#00ff88' }}></div>
            </div>

            <HealthRow label="CPU Load Core" value={system ? `${system.cpu_usage}%` : "--"} state={system?.cpu_usage > 70 ? "Stress Mode" : "Stable Bounds"} />
            <HealthRow label="RAM Capacity" value={system ? `${system.ram_usage}%` : "--"} state={system?.ram_usage > 80 ? "Throttling" : "Healthy Profile"} />
            <HealthRow label="Disk Profiles" value={system ? `${system.disk_usage}%` : "--"} state="Optimal Allocation" />

            </div>
        </div>
      </section>

      {system?.agent_active_alert && system?.agent_manual_steps?.length > 0 && (
        <section className="manual-steps-viewer">
          <h5>Manual Troubleshooting Backup Guidelines (If Auto-Fix Denied):</h5>
          <ul>
            {system.agent_manual_steps.map((step, i) => <li key={i}>{step}</li>)}
          </ul>
        </section>
      )}
    </div>
  );
}

function LiveMonitor({ system }) {
  return (
    <div className="dashboard-grid-view">
      <section className="metrics">
        <MetricCard icon={<Cpu />} title="Processor Load" value={system ? `${system.cpu_usage}%` : "--"} status="REALTIME" />
        <MetricCard icon={<Activity />} title="Memory Allocation" value={system ? `${system.ram_usage}%` : "--"} status="LIVE" />
        <MetricCard icon={<HardDrive />} title="Storage Sectors" value={system ? `${system.disk_usage}%` : "--"} status="MOUNTED" />
      </section>

      <div className="extended-telemetry-box">
        <h4>SIGNAL TELEMETRY MATRIX STRINGS</h4>
        <div className="telemetry-row">
          <span>Network Inbound:</span>
          <strong>{system ?.bytes_recv ? `${(system.bytes_recv / (1024 * 1024)).toFixed(2)} MB` : "--"}</strong>
        </div>
        <div className="telemetry-row">
          <span>Network Outbound:</span>
          <strong>{system ?.bytes_sent ? `${(system.bytes_sent / (1024 * 1024)).toFixed(2)} MB` : "--"}</strong>
        </div>
        <div className="telemetry-row">
          <span>Active Process Threads:</span>
          <strong>{system ? system.process_count : "--"} count</strong>
        </div>
      </div>
    </div>
  );
}

function Predictions({ system }) {
  return (
    <div className="extended-telemetry-box custom-prediction-view">
      <div className="panel-title">
        <BrainCircuit size={22} color="#00ff88" />
        <span>HISTGRADIENTBOOSTING HORIZON INTERFACE</span>
      </div>
      <div className="prediction-status-card">
        <h3>Current Lookahead State (Steps: -10)</h3>
        <p className="status-label">
          Status Check: {system?.agent_active_alert ? (
            <span style={{ color: '#ff4a4a', fontWeight: 'bold' }}>ANOMALY PROFILE DETECTED</span>
          ) : (
            <span style={{ color: '#00ff88' }}>HEALTH SPECTRUM CLEAR</span>
          )}
        </p>
        <small className="info-text">
          Model dynamically weighs parameters using SHAP value attribution algorithms to parse performance deviations.
        </small>
         </div>
    </div>
  );
}

function Anomalies({ system }) {
  return (
    <div className="extended-telemetry-box">
      <div className="panel-title">
        <ShieldAlert size={22} color="#ff4a4a" />
        <span>ISOLATION FOREST REALTIME OUTLIER LOGS</span>
      </div>
      <div className="outlier-status-layout">
        <div className="big-stat-number" style={{ color: system?.agent_active_alert ? '#ff4a4a' : '#cbd5e1' }}>
          {system?.agent_active_alert ? "1" : "0"}
          <span style={{ fontSize: '1rem', display: 'block', color: '#94a3b8' }}>ACTIVE ISOLATION ANOMALIES</span>
        </div>
        <div className="outlier-alert-message">{system?.agent_active_alert ? (
            <p>Machine parameters are currently operating outside learned multi-dimensional statistical boundaries.</p>
          ) : (
            <p>All metric vectors match standard operational cluster benchmarks.</p>
          )}
        </div>
      </div>
    </div>
  );
}

function AgenticAIView({ system }) {
  return (
    <div className="coming-soon">
      <Bot size={42} />
      <h3>Gemini AI Orchestrator Decision Log</h3>
      {system?.agent_active_alert ? (
        <div style={{ maxWidth: '600px', textAlign: 'left', background: '#1e293b', padding: '20px', borderRadius: '8px' }}>
          <p><strong>Active Brain:</strong> models/gemini-3.8-flash</p>
          <p><strong>Inference Reasoning:</strong> {system.agent_explanation}</p>
        </div>
      ):(
        <p>Agent status is currently idle. Listening to server signals...</p>
      )}
    </div>
  );
}

function SystemLogs() {
return (
  <div className="system-logs">
      <h4>Audit Stream Archive</h4>
      <p>System configuration mappings logged in 'agent_operations_log.json'.</p>
    </div>
  );
}

function MetricCard({ icon, title, value, status }) {
  return (
    <div className="metric-card">
      {icon}
      <h4>{title}</h4>
      <span className="metric-value">{value}</span>
      <small style={{ color: status === "STRESS" || status === "HIGH LOAD" ? "#ff4a4a" : "#00ff88" }}>
        {status}
      </small>
    </div>
  );
}

function HealthRow({ label, value, state }) {
  return (
    <div className="health-row">
      <span className="health-label">{label}</span>
      <span className="health-value">{value}</span>
      <span className="health-state">{state}</span>
    </div>
  );
}


export default App;
