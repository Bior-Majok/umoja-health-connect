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
    container.innerHTML = `<div class="empty-state">${t("no_providers_registered")}</div>`;
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
          <span class="status-badge ${p.is_verified ? "completed" : "pending"}">${p.is_verified ? t("verified_status") : t("pending_status")}</span>
          ${
            p.is_verified
              ? `<button type="button" class="secondary suspend-btn" data-id="${p.provider_id}">${t("suspend_btn")}</button>`
              : `<button type="button" class="secondary verify-btn" data-id="${p.provider_id}">${t("verify_btn")}</button>`
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
    <h2 style="font-size:1.05rem; margin-bottom:0.5rem;">${t("verified_providers_report_label")}: ${data.verified_providers} · ${t("pending_report_label")}: ${data.pending_providers}</h2>
    <h3 style="font-size:0.95rem; margin:1rem 0 0.3rem;">${t("patients_by_country_label")}</h3>
    ${countRows(data.patients_by_country) || `<div class="empty-state">${t("no_data_yet")}</div>`}
    <h3 style="font-size:0.95rem; margin:1rem 0 0.3rem;">${t("providers_by_region_label")}</h3>
    ${countRows(data.providers_by_region) || `<div class="empty-state">${t("no_data_yet")}</div>`}
    <h3 style="font-size:0.95rem; margin:1rem 0 0.3rem;">${t("consultations_by_status_label")}</h3>
    ${countRows(data.consultations_by_status) || `<div class="empty-state">${t("no_data_yet")}</div>`}
    <h3 style="font-size:0.95rem; margin:1rem 0 0.3rem;">${t("alerts_by_status_label")}</h3>
    ${countRows(data.emergency_alerts_by_status) || `<div class="empty-state">${t("no_data_yet")}</div>`}
  `;
}

async function loadFacilitiesForAdmin() {
  const res = await adminAuthFetch("/api/facilities");
  if (!res) return;
  const data = await res.json();
  const container = document.getElementById("facilities-list");
  if (!data.facilities.length) {
    container.innerHTML = `<div class="empty-state">${t("no_facilities_yet")}</div>`;
    return;
  }
  container.innerHTML = data.facilities
    .map(
      (f) => `
      <div class="list-item">
        <div>
          <div class="title">${f.name}</div>
          <div class="subtitle">${f.facility_type} · ${f.region}, ${f.country}${f.phone_number ? " · " + f.phone_number : ""}</div>
        </div>
        <button type="button" class="secondary remove-facility-btn" data-id="${f.id}">${t("remove_btn")}</button>
      </div>`
    )
    .join("");

  container.querySelectorAll(".remove-facility-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const res = await adminAuthFetch(`/api/facilities/${btn.dataset.id}`, { method: "DELETE" });
      if (res && res.ok) loadFacilitiesForAdmin();
    });
  });
}

function initFacilityForm() {
  const newBtn = document.getElementById("new-facility-btn");
  if (newBtn) newBtn.addEventListener("click", () => openModal("facility-modal"));

  const cancelBtn = document.getElementById("facility-modal-cancel");
  if (cancelBtn) cancelBtn.addEventListener("click", () => closeModal("facility-modal"));

  const form = document.getElementById("facility-form");
  if (!form) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const messageEl = document.getElementById("facility-message");
    const submitBtn = form.querySelector('button[type="submit"]');
    setButtonLoading(submitBtn, "Saving...");
    try {
      const res = await adminAuthFetch("/api/facilities", {
        method: "POST",
        body: JSON.stringify({
          name: form.name.value.trim(),
          facility_type: form.facility_type.value,
          country: form.country.value.trim(),
          region: form.region.value.trim(),
          phone_number: form.phone_number.value.trim() || undefined,
        }),
      });
      if (!res) return;
      const data = await res.json();
      if (!res.ok) {
        showMessage(messageEl, data.error || "Could not add facility", "error");
        return;
      }
      form.reset();
      closeModal("facility-modal");
      loadFacilitiesForAdmin();
    } catch (err) {
      showMessage(messageEl, "Could not reach the server.", "error");
    } finally {
      resetButtonLoading(submitBtn);
    }
  });
}

function initAdminDashboard() {
  if (!requireAdminSessionOrRedirect()) return;
  attachAdminLogout();
  loadProvidersForAdmin();
  loadAdminReports();
  loadFacilitiesForAdmin();
  initFacilityForm();
}
