const ADMIN_SESSION_KEY = "umoja_admin_session";

function getAdminSession() {
  const raw = localStorage.getItem(ADMIN_SESSION_KEY);
  return raw ? JSON.parse(raw) : null;
}

function setAdminSession(token, admin) {
  localStorage.setItem(ADMIN_SESSION_KEY, JSON.stringify({ token, admin }));
}

function clearAdminSession() {
  localStorage.removeItem(ADMIN_SESSION_KEY);
}

function requireAdminSessionOrRedirect() {
  const session = getAdminSession();
  if (!session) {
    window.location.href = "admin-login.html";
    return null;
  }
  return session;
}

async function adminAuthFetch(path, options = {}) {
  const session = getAdminSession();
  if (!session) {
    window.location.href = "admin-login.html";
    return null;
  }
  const res = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.token}`,
      ...(options.headers || {}),
    },
  });
  if (res.status === 401 || res.status === 422) {
    clearAdminSession();
    window.location.href = "admin-login.html";
    return null;
  }
  return res;
}

function attachAdminLogout() {
  const btn = document.getElementById("logout-btn");
  if (btn) {
    btn.addEventListener("click", () => {
      clearAdminSession();
      window.location.href = "admin-login.html";
    });
  }
}

async function handleAdminLogin(event) {
  event.preventDefault();
  const form = event.target;
  const messageEl = document.getElementById("message");
  const submitBtn = form.querySelector('button[type="submit"]');
  setButtonLoading(submitBtn, "Logging in...");
  try {
    const res = await fetch("/api/auth/admin/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        phone_number: form.phone_number.value.trim(),
        password: form.password.value,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      showMessage(messageEl, data.error || "Login failed", "error");
      return;
    }
    setAdminSession(data.access_token, data.admin);
    window.location.href = "admin-dashboard.html";
  } catch (err) {
    showMessage(messageEl, "Could not reach the server.", "error");
  } finally {
    resetButtonLoading(submitBtn);
  }
}

async function loadProvidersForAdmin() {
  const res = await adminAuthFetch("/api/providers?all=1");
  if (!res) return;
  const data = await res.json();
  const container = document.getElementById("providers-list");
  if (!data.providers.length) {
    container.innerHTML = '<div class="empty-state">No providers registered yet.</div>';
    return;
  }
  container.innerHTML = data.providers
    .map(
      (p) => `
      <div class="list-item">
        <div>
          <div class="title">${p.full_name} — ${p.specialization}</div>
          <div class="subtitle">${p.region}, ${p.country} · ${p.phone_number}</div>
        </div>
        <div class="list-item-meta">
          <span class="status-badge ${p.is_verified ? "completed" : "pending"}">${p.is_verified ? "verified" : "pending"}</span>
          ${
            p.is_verified
              ? `<button type="button" class="secondary suspend-btn" data-id="${p.provider_id}">Suspend</button>`
              : `<button type="button" class="secondary verify-btn" data-id="${p.provider_id}">Verify</button>`
          }
        </div>
      </div>`
    )
    .join("");

  container.querySelectorAll(".verify-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const res = await adminAuthFetch(`/api/providers/${btn.dataset.id}/verify`, { method: "PATCH" });
      if (res && res.ok) loadProvidersForAdmin();
    });
  });
  container.querySelectorAll(".suspend-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const res = await adminAuthFetch(`/api/providers/${btn.dataset.id}/suspend`, { method: "PATCH" });
      if (res && res.ok) loadProvidersForAdmin();
    });
  });
}

async function loadAdminReports() {
  const res = await adminAuthFetch("/api/admin/reports");
  if (!res) return;
  const data = await res.json();
  const container = document.getElementById("reports-summary");
  const countRows = (obj) =>
    Object.entries(obj)
      .map(([k, v]) => `<div class="list-item"><div class="title">${k}</div><span class="status-badge normal">${v}</span></div>`)
      .join("");

  container.innerHTML = `
    <h2 style="font-size:1.05rem; margin-bottom:0.5rem;">Verified providers: ${data.verified_providers} · Pending: ${data.pending_providers}</h2>
    <h3 style="font-size:0.95rem; margin:1rem 0 0.3rem;">Patients by country</h3>
    ${countRows(data.patients_by_country) || '<div class="empty-state">No data yet.</div>'}
    <h3 style="font-size:0.95rem; margin:1rem 0 0.3rem;">Providers by region</h3>
    ${countRows(data.providers_by_region) || '<div class="empty-state">No data yet.</div>'}
    <h3 style="font-size:0.95rem; margin:1rem 0 0.3rem;">Consultations by status</h3>
    ${countRows(data.consultations_by_status) || '<div class="empty-state">No data yet.</div>'}
    <h3 style="font-size:0.95rem; margin:1rem 0 0.3rem;">Emergency alerts by status</h3>
    ${countRows(data.emergency_alerts_by_status) || '<div class="empty-state">No data yet.</div>'}
  `;
}

function initAdminDashboard() {
  if (!requireAdminSessionOrRedirect()) return;
  attachAdminLogout();
  loadProvidersForAdmin();
  loadAdminReports();
}
