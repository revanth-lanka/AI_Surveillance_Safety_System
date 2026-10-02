import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Car,
  Camera,
  CheckCircle2,
  CircleUserRound,
  Gauge,
  RefreshCw,
  ShieldAlert,
  Trash2,
  Users,
  Video,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import { API, clearEvents, getEvents, getSettings, updateSettings } from "./api";

const initialStats = {
  people: 0,
  vehicles: 0,
  objects: 0,
  alerts: 0,
  fps: 0,
  camera: "Camera 1",
  status: "CONNECTING",
  model: "",
};

function StatCard({ icon: Icon, title, value, subtitle }) {
  return (
    <div className="stat-card">
      <div className="stat-icon"><Icon size={21} /></div>
      <div>
        <div className="stat-title">{title}</div>
        <div className="stat-value">{value}</div>
        <div className="stat-subtitle">{subtitle}</div>
      </div>
    </div>
  );
}

function App() {
  const [stats, setStats] = useState(initialStats);
  const [events, setEvents] = useState([]);
  const [settings, setSettings] = useState({
    crowd_threshold: 8,
    confidence: 0.45,
  });
  const [saving, setSaving] = useState(false);
  const [wsStatus, setWsStatus] = useState("Connecting");

  const refreshEvents = async () => {
    try {
      setEvents(await getEvents());
    } catch {
      // backend may not be ready yet
    }
  };

  useEffect(() => {
    getSettings().then((s) => {
      setSettings({
        crowd_threshold: s.crowd_threshold,
        confidence: s.confidence,
      });
    }).catch(() => {});

    refreshEvents();
    const interval = setInterval(refreshEvents, 3000);

    let ws;
    let reconnectTimer;

    const connect = () => {
      ws = new WebSocket("ws://127.0.0.1:8000/ws");
      ws.onopen = () => setWsStatus("Live");
      ws.onmessage = (event) => setStats(JSON.parse(event.data));
      ws.onclose = () => {
        setWsStatus("Reconnecting");
        reconnectTimer = setTimeout(connect, 2000);
      };
      ws.onerror = () => ws.close();
    };

    connect();

    return () => {
      clearInterval(interval);
      clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, []);

  const chartData = useMemo(() => {
    const counts = {};
    [...events].reverse().forEach((e) => {
      const hour = e.timestamp?.slice(11, 13) || "--";
      counts[hour] = (counts[hour] || 0) + 1;
    });
    return Object.entries(counts).slice(-8).map(([hour, count]) => ({
      hour: `${hour}:00`,
      alerts: count,
    }));
  }, [events]);

  const saveSettings = async () => {
    setSaving(true);
    try {
      const result = await updateSettings(settings);
      setSettings(result);
    } finally {
      setSaving(false);
    }
  };

  const removeEvents = async () => {
    await clearEvents();
    await refreshEvents();
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <div className="brand-row">
            <div className="brand-mark"><ShieldAlert size={24} /></div>
            <div>
              <h1>AI Surveillance</h1>
              <p>Real-Time Safety Monitoring System</p>
            </div>
          </div>
        </div>
        <div className="connection">
          <span className={`dot ${wsStatus === "Live" ? "live" : ""}`}></span>
          {wsStatus}
        </div>
      </header>

      <main className="content">
        <section className="stats-grid">
          <StatCard icon={Users} title="People" value={stats.people} subtitle="Currently detected" />
          <StatCard icon={Car} title="Vehicles" value={stats.vehicles} subtitle="Currently detected" />
          <StatCard icon={AlertTriangle} title="Events" value={events.length} subtitle="Recorded events" />
          <StatCard icon={Gauge} title="FPS" value={stats.fps} subtitle="Inference speed" />
        </section>

        <section className="main-grid">
          <div className="panel camera-panel">
            <div className="panel-header">
              <div>
                <h2><Video size={18} /> Live Camera</h2>
                <span>{stats.camera} · {stats.status}</span>
              </div>
              <div className="live-pill"><span className="dot live"></span> LIVE</div>
            </div>
            <div className="camera-frame">
              <img src={`${API}/video_feed`} alt="Live surveillance feed" />
              {stats.status !== "LIVE" && (
                <div className="camera-overlay">
                  <Camera size={38} />
                  <strong>{stats.status}</strong>
                  <span>Start the backend camera service.</span>
                </div>
              )}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h2><Activity size={18} /> System Status</h2>
                <span>Real-time inference</span>
              </div>
              <CheckCircle2 className="ok-icon" size={22} />
            </div>

            <div className="status-list">
              <div><span>Model</span><strong>{stats.model || "Loading..."}</strong></div>
              <div><span>Camera</span><strong>{stats.camera}</strong></div>
              <div><span>System</span><strong>{stats.status}</strong></div>
              <div><span>Detection objects</span><strong>{stats.objects}</strong></div>
            </div>

            <div className="settings">
              <h3>Detection Settings</h3>
              <label>
                Crowd threshold
                <input
                  type="number"
                  min="1"
                  value={settings.crowd_threshold}
                  onChange={(e) => setSettings({
                    ...settings,
                    crowd_threshold: Number(e.target.value),
                  })}
                />
              </label>
              <label>
                Confidence
                <input
                  type="number"
                  min="0.05"
                  max="0.99"
                  step="0.05"
                  value={settings.confidence}
                  onChange={(e) => setSettings({
                    ...settings,
                    confidence: Number(e.target.value),
                  })}
                />
              </label>
              <button onClick={saveSettings} disabled={saving}>
                <RefreshCw size={16} /> {saving ? "Saving..." : "Save Settings"}
              </button>
            </div>
          </div>
        </section>

        <section className="bottom-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h2><AlertTriangle size={18} /> Recent Events</h2>
                <span>Safety and detection activity</span>
              </div>
              <button className="icon-btn" title="Clear events" onClick={removeEvents}>
                <Trash2 size={17} />
              </button>
            </div>

            <div className="events">
              {events.length === 0 ? (
                <div className="empty">No events recorded yet.</div>
              ) : events.slice(0, 8).map((event, i) => (
                <div className="event-row" key={event.id || event._id || i}>
                  <div className="event-icon"><AlertTriangle size={17} /></div>
                  <div className="event-info">
                    <strong>{event.event_type}</strong>
                    <span>{event.message}</span>
                  </div>
                  <time>{event.timestamp?.replace("T", " ").replace("Z", "")}</time>
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h2><Activity size={18} /> Event Analytics</h2>
                <span>Events by hour</span>
              </div>
            </div>
            <div className="chart">
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="alerts" name="Events" radius={[5,5,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <footer>
          <span>AI Surveillance & Safety System</span>
          <span>Computer Vision · YOLO · FastAPI · React</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
