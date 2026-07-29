const PROVIDER_SESSION_KEY = "umoja_provider_session";

function getProviderSession() {
  const raw = localStorage.getItem(PROVIDER_SESSION_KEY);
  return raw ? JSON.parse(raw) : null;
}

function setProviderSession(token, provider) {
  localStorage.setItem(PROVIDER_SESSION_KEY, JSON.stringify({ token, provider }));
}

function clearProviderSession() {
  localStorage.removeItem(PROVIDER_SESSION_KEY);
}

function requireProviderSessionOrRedirect() {
  const session = getProviderSession();
  if (!session) {
    window.location.href = "provider-login.html";
    return null;
  }
  return session;
}

async function providerAuthFetch(path, options = {}) {
  const session = getProviderSession();
  if (!session) {
    window.location.href = "provider-login.html";
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
    clearProviderSession();
    window.location.href = "provider-login.html";
    return null;
  }
  return res;
}

function attachProviderLogout() {
  const btn = document.getElementById("logout-btn");
  if (btn) {
    btn.addEventListener("click", () => {
      clearProviderSession();
      window.location.href = "provider-login.html";
    });
  }
}

async function handleProviderRegister(event) {
  event.preventDefault();
  const form = event.target;
  const messageEl = document.getElementById("message");
  const submitBtn = form.querySelector('button[type="submit"]');
  setButtonLoading(submitBtn, "Registering...");
  try {
    const res = await fetch("/api/auth/provider/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: form.full_name.value.trim(),
        phone_number: form.phone_number.value.trim(),
        specialization: form.specialization.value.trim(),
        country: form.country.value.trim(),
        region: form.region.value.trim(),
        password: form.password.value,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      showMessage(messageEl, data.error || "Registration failed", "error");
      return;
    }
    showMessage(messageEl, data.message, "success");
    form.reset();
  } catch (err) {
    showMessage(messageEl, "Could not reach the server.", "error");
  } finally {
    resetButtonLoading(submitBtn);
  }
}

async function handleProviderLogin(event) {
  event.preventDefault();
  const form = event.target;
  const messageEl = document.getElementById("message");
  const submitBtn = form.querySelector('button[type="submit"]');
  setButtonLoading(submitBtn, "Logging in...");
  try {
    const res = await fetch("/api/auth/provider/login", {
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
    setProviderSession(data.access_token, data.provider);
    window.location.href = "provider-dashboard.html";
  } catch (err) {
    showMessage(messageEl, "Could not reach the server.", "error");
  } finally {
    resetButtonLoading(submitBtn);
  }
}

async function loadProviderConsultations() {
  const res = await providerAuthFetch("/api/consultations");
  if (!res) return;
  const data = await res.json();
  const container = document.getElementById("consultations-list");
  if (!data.consultations.length) {
    container.innerHTML = `<div class="empty-state">${t("no_consultations_yet")}</div>`;
    return;
  }
  container.innerHTML = data.consultations
    .map(
      (c) => `
      <div class="list-item">
        <div>
          <div class="title">${c.symptoms}</div>
          <div class="subtitle">${t("patient_label")} ${c.patient_id} · ${formatDateTime(c.created_at)}</div>
        </div>
        <div class="list-item-meta">
          <span class="status-badge ${c.urgency === "critical" ? "critical" : c.status}">${c.urgency === "critical" ? "critical" : c.status}</span>
          <button type="button" class="secondary records-btn" data-patient-id="${c.patient_id}">${t("view_records_btn")}</button>
          ${c.status !== "closed" ? `<button type="button" class="secondary respond-btn" data-id="${c.id}">${t("respond_btn")}</button>` : ""}
        </div>
      </div>`
    )
    .join("");

  container.querySelectorAll(".respond-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.getElementById("respond-consultation-id").value = btn.dataset.id;
      openModal("respond-modal");
    });
  });

  container.querySelectorAll(".records-btn").forEach((btn) => {
    btn.addEventListener("click", () => showPatientRecords(btn.dataset.patientId));
  });
}

async function showPatientRecords(patientId) {
  openModal("patient-records-modal");
  const titleEl = document.getElementById("patient-records-title");
  const listEl = document.getElementById("patient-records-list");
  titleEl.textContent = t("patient_records_title");
  listEl.innerHTML = `<p class="empty-state">${t("loading")}</p>`;
  const res = await providerAuthFetch(`/api/records/patient/${patientId}`);
  if (!res) return;
  const data = await res.json();
  if (!res.ok) {
    listEl.innerHTML = `<p class="empty-state">${data.error || t("could_not_load_records")}</p>`;
    return;
  }
  titleEl.textContent = `${t("records_heading_prefix")} ${data.patient.full_name}`;
  if (!data.records.length) {
    listEl.innerHTML = `<p class="empty-state">${t("no_records_on_file")}</p>`;
    return;
  }
  listEl.innerHTML = data.records
    .map(
      (r) => `
      <div class="list-item">
        <div>
          <div class="title">${r.title}</div>
          <div class="subtitle">${r.details || ""}${r.details ? " · " : ""}${formatDateTime(r.recorded_at)}</div>
        </div>
        <span class="status-badge ${r.status}">${r.status}</span>
      </div>`
    )
    .join("");
}

function initProviderDashboard() {
  if (!requireProviderSessionOrRedirect()) return;
  attachProviderLogout();
  loadProviderConsultations();

  const closeBtn = document.getElementById("respond-modal-cancel");
  if (closeBtn) closeBtn.addEventListener("click", () => closeModal("respond-modal"));

  const recordsCloseBtn = document.getElementById("patient-records-close");
  if (recordsCloseBtn) recordsCloseBtn.addEventListener("click", () => closeModal("patient-records-modal"));

  const form = document.getElementById("respond-form");
  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const messageEl = document.getElementById("respond-message");
      const submitBtn = form.querySelector('button[type="submit"]');
      const consultationId = document.getElementById("respond-consultation-id").value;

      setButtonLoading(submitBtn, "Saving...");
      try {
        const res = await providerAuthFetch(`/api/consultations/${consultationId}/respond`, {
          method: "PATCH",
          body: JSON.stringify({
            response_notes: form.response_notes.value.trim(),
            status: form.close_case.checked ? "closed" : "responded",
            urgency: form.mark_critical.checked ? "critical" : undefined,
          }),
        });
        if (!res) return;
        const data = await res.json();
        if (!res.ok) {
          showMessage(messageEl, data.error || "Could not save response", "error");
          return;
        }
        form.reset();
        closeModal("respond-modal");
        loadProviderConsultations();
      } catch (err) {
        showMessage(messageEl, "Could not reach the server.", "error");
      } finally {
        resetButtonLoading(submitBtn);
      }
    });
  }
}

async function loadProviderAppointments() {
  const res = await providerAuthFetch("/api/appointments/provider");
  if (!res) return;
  const data = await res.json();
  const container = document.getElementById("provider-appointments-list");
  if (!data.appointments.length) {
    container.innerHTML = `<div class="empty-state">${t("no_appointments_yet")}</div>`;
    return;
  }
  container.innerHTML = data.appointments
    .map(
      (a) => `
      <div class="list-item">
        <div>
          <div class="title">${a.clinic_name}</div>
          <div class="subtitle">${formatDateTime(a.scheduled_at)}${a.notes ? " · " + a.notes : ""}</div>
        </div>
        <div class="list-item-meta">
          <span class="status-badge ${a.status}">${a.status}</span>
          ${a.status === "upcoming" ? `<button type="button" class="secondary complete-btn" data-id="${a.id}">${t("mark_completed_btn")}</button>` : ""}
        </div>
      </div>`
    )
    .join("");

  container.querySelectorAll(".complete-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const res = await providerAuthFetch(`/api/appointments/${btn.dataset.id}/complete`, { method: "PATCH" });
      if (res && res.ok) loadProviderAppointments();
    });
  });
}

function initProviderAppointments() {
  if (!requireProviderSessionOrRedirect()) return;
  attachProviderLogout();
  loadProviderAppointments();
}

async function loadProviderAlerts() {
  const res = await providerAuthFetch("/api/emergency-alerts");
  if (!res) return;
  const data = await res.json();
  const container = document.getElementById("alerts-list");
  if (!data.emergency_alerts.length) {
    container.innerHTML = `<div class="empty-state">${t("no_alerts_in_region")}</div>`;
    return;
  }
  container.innerHTML = data.emergency_alerts
    .map(
      (a) => `
      <div class="list-item">
        <div>
          <div class="title">${a.condition}</div>
          <div class="subtitle">${mapsLink(a.location)} · ${formatDateTime(a.created_at)}</div>
        </div>
        <div class="list-item-meta">
          <span class="status-badge ${a.status}">${a.status}</span>
          ${a.status !== "resolved" ? `<button type="button" class="secondary resolve-btn" data-id="${a.id}">${t("resolve_btn")}</button>` : ""}
        </div>
      </div>`
    )
    .join("");

  container.querySelectorAll(".resolve-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const res = await providerAuthFetch(`/api/emergency-alerts/${btn.dataset.id}/resolve`, { method: "PATCH" });
      if (res && res.ok) loadProviderAlerts();
    });
  });
}

function initProviderAlerts() {
  if (!requireProviderSessionOrRedirect()) return;
  attachProviderLogout();
  loadProviderAlerts();
}
