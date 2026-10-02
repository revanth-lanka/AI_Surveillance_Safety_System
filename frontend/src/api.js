export const API = "http://127.0.0.1:8000";

export async function getEvents() {
  const res = await fetch(`${API}/api/events?limit=50`);
  return res.json();
}

export async function getSettings() {
  const res = await fetch(`${API}/api/settings`);
  return res.json();
}

export async function updateSettings(payload) {
  const res = await fetch(`${API}/api/settings`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function clearEvents() {
  await fetch(`${API}/api/events`, { method: "DELETE" });
}
