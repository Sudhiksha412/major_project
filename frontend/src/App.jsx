import { useState, useEffect } from "react";
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

  const fetchSystemData = async () => {
    try {
      const data = await getSystemStatus();
      if (data) 
      setSystem(data);
    } catch (error) {
      console.error("API ERROR:", error);
    }
  };

  useEffect(() => {
    fetchSystemData();
    const interval = setInterval(fetchSystemData, 2000);
    return () => clearInterval(interval);
  }, []);

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
            <span>COMMAND CENTER</span>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>SYSTEM ONLINE
        </div>

        <nav>
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.name}
                className={`nav-item ${activePage === item.name ? "active" : ""}`}
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
            <div><span className="status-dot"></span>Monitoring Active</div>
            <div className="server-id">NODE-01</div>
          </div>
        </header>

        {activePage === "Dashboard" && <Dashboard system={system} triggerRefresh={fetchSystemData} />}
        {activePage === "Live Monitor" && <LiveMonitor system={system} />}
        {activePage === "Predictions" && <Predictions system={system} />}
        {activePage === "Anomalies" && <Anomalies system={system} />}
        {activePage === "Agentic AI" && <AgenticAIView system={system} triggerRefresh={fetchSystemData} />}
        {activePage === "System Logs" && <SystemLogs />}
      </main>
    </div>
  );
}


function Dashboard({ system, triggerRefresh }) {
  const [actionMessage, setActionMessage] = useState("");

  const handleAgentDecision = async (userChoice) => {
    try {
      const response = await fetch("http://localhost:8000/action-confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision: userChoice })
      });
      const data = await response.json();
      setActionMessage(data.result);
      triggerRefresh(); // Fetch latest optimized state metrics
      setTimeout(() => setActionMessage(""), 7000);
    } catch (err) {
      console.error("Action execution routing error:", err);
    }
  };

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
        <MetricCard icon={<Cpu />} title="CPU Usage" value={system ? `${system.cpu}%` : "--"} status={system?.cpu > 70 ? "STRESS" : "NORMAL"} />
        <MetricCard icon={<Activity />} title="RAM Usage" value={system ? `${system.ram}%` : "--"} status={system?.ram > 80 ? "HIGH LOAD" : "NORMAL"} />
        <MetricCard icon={<HardDrive />} title="Disk Usage" value={system ? `${system.disk}%` : "--"} status="NORMAL" />
        <MetricCard icon={<Network />} title="Network Activity" value={system ? `${system.processes} Procs` : "--"} status="CONNECTED" />
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
          <div className="three-container"><Infrastructure3D /></div>
          
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

            <HealthRow label="CPU Load Core" value={system ? `${system.cpu}%` : "--"} state={system?.cpu > 70 ? "Stress Mode" : "Stable Bounds"} />
            <HealthRow label="RAM Capacity" value={system ? `${system.ram}%` : "--"} state={system?.ram > 80 ? "Throttling" : "Healthy Profile"} />
            <HealthRow label="Disk Profiles" value={system ? `${system.disk}%` : "--"} state="Optimal Allocation" />
            
            <div className="prediction-box" style={{ borderColor: system?.agent_active_alert ? '#ff4a4a' : '#1e293b' }}>
              <div className="prediction-icon"><BrainCircuit size={20} /></div>
              <div>
                <span>AI FAILURE PREDICTION</span>
                <strong>{system?.agent_active_alert ? "CRITICAL RISK PROFILE DETECTED" : "LOW RISK SPECTRUM"}</strong>
                <small>Probability: {system?.agent_active_alert ? "89%" : "12%"}</small>
              </div>
            </div>
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
    <div className="coming-soon">
      <Cpu size={42} />
      <h3>Real-time Signal Telemetry</h3>
      <p>CPU: {system?.cpu}% | RAM: {system?.ram}% | Disk: {system?.disk}%</p>
    </div>
  );
}

function Predictions({ system }) {
  return (
    <div className="coming-soon">
      <BrainCircuit size={42} />
      <h3>HistGradientBoosting Lookahead Horizon</h3>
      <p>Predicted Status: {system?.agent_active_alert ? "🚨 ANOMALY RISK IN STEPS [-10]" : "✅ CLEAR FORECAST"}</p>
    </div>
  );
}

function Anomalies({ system }) {
  return (
    <div className="coming-soon">
      <ShieldAlert size={42} />
      <h3>Isolation Forest Analysis Layer</h3>
      <p>Detected Dynamic Outliers: {system?.agent_active_alert ? "1 Active Outlier Signature" : "0 System Outliers"}</p>
    </div>
  );
}

function AgenticAIView({ system, triggerRefresh }) {
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
