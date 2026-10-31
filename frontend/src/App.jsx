import { useState, useEffect,useRef, Suspense } from "react";
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
  const [alertPopup, setAlertPopup] = useState(null);
  const lastAlertSignature = useRef("");
  const alertTimer = useRef(null);
  const [incidentPopup, setIncidentPopup] = useState(null);
  const [manualGuide, setManualGuide] = useState(false);
  const lastIncident = useRef("");


  const fetchSystemData = async () => {
    try {
      const data = await getSystemStatus();
     if (!data) {
      setIsOnline(false);
      return;
    }

    setSystem(data);
    setIsOnline(true);


    const cpu = Number(data.cpu_usage ?? 0);
    const ram = Number(data.ram_usage ?? 0);
    const disk = Number(data.disk_usage ?? 0);
    
    const issues = [];

    if (cpu >= 75) {
      issues.push(`High CPU usage: ${cpu.toFixed(1)}%`);
    }

    if (ram >= 80) {
      issues.push(`High RAM usage: ${ram.toFixed(1)}%`);
    }

    if (disk >= 90) {
      issues.push(`High disk utilisation: ${disk.toFixed(1)}%`);
    }

    if (Number(data.model_isolation_anomaly) === 1) {
      issues.push("Isolation Forest detected an anomaly");
    }

    if (Number(data.model_future_risk) === 1) {
      issues.push("ML model predicts elevated risk");
    }

    const signature = issues.join(" | ");

    if (signature && signature !== lastIncident.current) {
      lastIncident.current = signature;

      setIncidentPopup({
        issues,
        cpu,
        ram,
        disk
      });
    }

    if (!signature) {
      lastIncident.current = "";
    }
  } catch (error) {
    console.error("API ERROR:", error);
    setIsOnline(false);
  }
};

      if (alertTimer.current) {
        clearTimeout(alertTimer.current);
      }

  useEffect(() => {
    fetchSystemData();
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

        <button
  onClick={() =>
    setIncidentPopup({
      issues: ["TEST ALERT: High RAM usage detected"],
      cpu: 68.8,
      ram: 83.3,
      disk: 70.3,
    })
  }
  style={{
    position: "fixed",
    bottom: "20px",
    right: "20px",
    zIndex: 200000,
    padding: "12px 18px",
    background: "#7655e8",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  }}
>
  Test Alert Popup
</button>

{incidentPopup && (
  <div
    role="dialog"
    aria-modal="true"
    style={{
      position: "fixed",
      inset: 0,
      zIndex: 100001,
      background: "rgba(0,0,0,0.8)",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      padding: "20px",
    }}
  >
    <div
      style={{
        background: "#101426",
        color: "white",
        border: "1px solid #ff4a4a",
        borderRadius: "16px",
        padding: "28px",
        width: "min(500px, 100%)",
        boxSizing: "border-box",
      }}
    >
      <h2 style={{ color: "#ff7777" }}>
        <AlertTriangle
          size={24}
          style={{ verticalAlign: "middle", marginRight: "10px" }}
        />
        System Anomaly Detected
      </h2>

      <ul style={{ lineHeight: 1.8 }}>
        {incidentPopup.issues.map((issue, index) => (
          <li key={index}>{issue}</li>
        ))}
      </ul>

      <p>CPU: {incidentPopup.cpu.toFixed(1)}%</p>
      <p>RAM: {incidentPopup.ram.toFixed(1)}%</p>
      <p>Disk: {incidentPopup.disk.toFixed(1)}%</p>

      <p>How would you like to resolve this issue?</p>

      <button
        onClick={() => {
          setIncidentPopup(null);
          setActivePage("Agentic AI");
        }}
        style={{
          width: "100%",
          padding: "12px",
          background: "#7655e8",
          color: "white",
          border: "none",
          borderRadius: "8px",
          cursor: "pointer",
          marginBottom: "10px",
        }}
      >
        Ask AI Agent for Assistance
      </button>

      <button
        onClick={() => {
          setIncidentPopup({
            ...incidentPopup,
            showManual: true,
          });
        }}
        style={{
          width: "100%",
          padding: "12px",
          background: "#1e293b",
          color: "white",
          border: "1px solid #64748b",
          borderRadius: "8px",
          cursor: "pointer",
        }}
      >
        I'll Handle It Myself
      </button>

      {incidentPopup.showManual && (
        <div style={{ marginTop: "18px", lineHeight: 1.7 }}>
          <h3>Manual Troubleshooting</h3>
          <ol>
            <li>Press Ctrl + Shift + Esc to open Task Manager.</li>
            <li>Check which applications are using the most memory.</li>
            <li>Save your work before closing unnecessary applications.</li>
            <li>Return to the dashboard to monitor the metrics.</li>
          </ol>
        </div>
      )}

      <button
        onClick={() => setIncidentPopup(null)}
        style={{
          marginTop: "16px",
          background: "transparent",
          color: "#94a3b8",
          border: "none",
          cursor: "pointer",
        }}
      >
        Close
      </button>
    </div>
  </div>
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
        body: JSON.stringify({ payload })
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

        {system?.live_shap_explanations?.length > 0 && (
          <div className="shap-explanation-panel" style={{ marginTop: '20px', background: '#0b1329', padding: '15px', borderRadius: '6px' }}>
           <h5 style={{ color: "#a78bfa", marginBottom: "10px" }}>Live Feature Attributions (Proxy SHAP Weights)</h5>
            {system.live_shap_explanations.map((exp, idx) => (
              <div key={idx} style={{ display: "flex", justifyContent: "space-between", padding: "5px 0", borderBottom: "1px solid #1e293b" }}>
                <span>{exp.feature} ({exp.value})</span>
                <strong style={{ color: exp.impact?.startsWith("+") ? "#ff4a4a" : "#4aff4a" }}>
                  {exp.impact}
                </strong>
              </div>
            ))}
          </div> 
                  )}
      </div>
    </div>
  );
}


function Anomalies({ system }) {
  const cpu = Number(system?.cpu_usage ?? 0);
  const ram = Number(system?.ram_usage ?? 0);
  const disk = Number(system?.disk_usage ?? 0);
  const mlAnomaly = Number(system?.model_isolation_anomaly ?? 0) === 1;
  const highCpu = cpu >= 75;
  const highRam = ram >= 80;
  const highDisk = disk >= 90;
  const alerts = [];

  if (mlAnomaly) {
    alerts.push({
      title: "Isolation Forest Anomaly",
      detail: "The ML model detected an unusual system metric pattern.",
    });
  }

  if (highCpu) {
    alerts.push({
      title: "High CPU Usage",
      detail: `CPU usage is ${cpu.toFixed(1)}%. Threshold: 75%.`,
    });
  }

  if (highRam) {
    alerts.push({
      title: "High RAM Usage",
      detail: `RAM usage is ${ram.toFixed(1)}%. Threshold: 80%.`,
    });
  }

  if (highDisk) {
    alerts.push({
      title: "High Disk Usage",
      detail: `Disk usage is ${disk.toFixed(1)}%. Threshold: 90%.`,
    });
  }

  const hasAlerts = alerts.length > 0;

  return (
    <div className="extended-telemetry-box">
      <div className="panel-title">
        <ShieldAlert
          size={22}
          color={hasAlerts ? "#ff4a4a" : "#00ff88"}
        />
        <span>SYSTEM ANOMALY & RESOURCE ALERTS</span>
      </div>
      <div className="outlier-status-layout">
        <div className="big-stat-number" style={{ color: hasAlerts ? "#ff4a4a" : "#00ff88", }}>
          {alerts.length}
          <span
            style={{
              fontSize: "1rem",
              display: "block",
              color: "#94a3b8",
            }}
          >
            ACTIVE SYSTEM ALERTS
          </span>
        </div>

        <div className="outlier-alert-message">
          {hasAlerts ? (
            <div>
              <h3 style={{ color: "#ff7777" }}>
                System Attention Required
              </h3>

              {alerts.map((alert, index) => (
                <div
                  key={index}
                  style={{
                    marginTop: "16px",
                    padding: "14px",
                    border: "1px solid #7f1d1d",
                    borderRadius: "8px",
                     background: "#25111b",
                  }}
                >
                  <strong style={{ color: "#ff7777" }}>
                    <AlertTriangle
                      size={16}
                      style={{
                        verticalAlign: "middle",
                        marginRight: "8px",
                      }}
                    />

                    {alert.title}
                  </strong>

                  <p style={{ marginBottom: 0 }}>
                    {alert.detail}
                  </p>
                </div>
              ))}

              <p style={{ marginTop: "18px", color: "#cbd5e1" }}>
                ML anomaly detected: {mlAnomaly ? "YES" : "NO"}
              </p>
            </div>
          ) : (
            <p style={{ color: "#00ff88" }}>
              No resource threshold alerts or Isolation Forest
              anomalies detected at this moment.
            </p>
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
  <div className="extended-telemetry-box" style={{ overflowX: "auto" }}>
      <h4>Live Incident & Audit Trail Records</h4>
      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "15px", textAlign: "left" }}>
        <thead>
          <tr style={{ color: "#a78bfa", borderBottom: "2px solid #1e293b" }}>
            <th style={{ padding: "8px" }}>Timestamp</th>
            <th style={{ padding: "8px" }}>Action Type</th>
            <th style={{ padding: "8px" }}>Status</th>
            <th style={{ padding: "8px" }}>Outcome Details</th>
          </tr>
        </thead>
        <tbody>
          {!logs || logs.length === 0 ? (
            <tr>
              <td colSpan={4} style={{ padding: "10px", color: "#94a3b8", textAlign: "center" }}>
                No recorded events found in agent_operations_log.json. Trigger an action to log here.
              </td>
            </tr>
          ) : (
            logs.map((log, idx) => (
              <tr key={idx} style={{ borderBottom: "1px solid #1e293b", fontSize: "13px" }}>
                <td style={{ padding: "8px", color: "#60a5fa", fontFamily: "monospace" }}>{log.Timestamp}</td>
                <td style={{ padding: "8px", fontWeight: "bold" }}>{log.action_type}</td>
                <td style={{ padding: "8px", color: log.status === "Success" ? "#4aff4a" : "#ffb84d" }}>{log.status}</td>
                <td style={{ padding: "8px", color: "#cbd5e1" }}>{log.details}</td>
              </tr>
            ))
          )}
        </tbody>
        </table>
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
