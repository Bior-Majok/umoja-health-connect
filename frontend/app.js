const AUTH_BASE = "/api/auth";
const APPOINTMENTS_BASE = "/api/appointments";
const RECORDS_BASE = "/api/records";
const CONSULTATIONS_BASE = "/api/consultations";

function showMessage(el, text, type) {
  el.textContent = text;
  el.className = `message ${type}`;
}

function getSession() {
  const raw = localStorage.getItem("umoja_session");
  return raw ? JSON.parse(raw) : null;
}

function setSession(token, patient) {
  localStorage.setItem("umoja_session", JSON.stringify({ token, patient }));
}

function clearSession() {
  localStorage.removeItem("umoja_session");
}

function requireSessionOrRedirect() {
  const session = getSession();
  if (!session) {
    window.location.href = "index.html";
    return null;
  }
  return session;
}

function redirectToLoginExpired() {
  clearSession();
  window.location.href = "index.html?expired=1";
}

function showExpiredNoticeIfPresent() {
  const params = new URLSearchParams(window.location.search);
  if (params.get("expired") === "1") {
    const messageEl = document.getElementById("message");
    if (messageEl) {
      showMessage(messageEl, "Your session expired. Please log in again.", "error");
    }
  }
}

// Wraps fetch with the auth token and redirects to login on 401 (expired/invalid token).
async function authFetch(path, options = {}) {
  const session = getSession();
  if (!session) {
    redirectToLoginExpired();
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
    redirectToLoginExpired();
    return null;
  }

  return res;
}

function setButtonLoading(button, loadingText) {
  button.dataset.originalText = button.textContent;
  button.textContent = loadingText;
  button.disabled = true;
}

function resetButtonLoading(button) {
  if (button.dataset.originalText) {
    button.textContent = button.dataset.originalText;
  }
  button.disabled = false;
}

function setFieldError(input, text) {
  const field = input.closest(".field");
  if (!field) return;
  let errorEl = field.querySelector(".field-error");
  if (!errorEl) {
    errorEl = document.createElement("div");
    errorEl.className = "field-error";
    field.appendChild(errorEl);
  }
  errorEl.textContent = text;
  input.classList.toggle("invalid", Boolean(text));
}

function clearFieldError(input) {
  setFieldError(input, "");
}

// Returns true if valid. Displays inline error and returns false otherwise.
function validateField(input) {
  const value = input.value.trim();

  if (input.hasAttribute("required") && !value) {
    setFieldError(input, "This field is required.");
    return false;
  }

  if (input.type === "tel" && value && !/^\+?[0-9]{7,15}$/.test(value)) {
    setFieldError(input, "Enter a valid phone number (7-15 digits).");
    return false;
  }

  if (input.type === "password" && value && input.minLength > 0 && value.length < input.minLength) {
    setFieldError(input, `Password must be at least ${input.minLength} characters.`);
    return false;
  }

  if (input.type === "number" && value) {
    const num = Number(value);
    const min = input.min !== "" ? Number(input.min) : null;
    const max = input.max !== "" ? Number(input.max) : null;
    if ((min !== null && num < min) || (max !== null && num > max)) {
      setFieldError(input, `Enter a value between ${input.min} and ${input.max}.`);
      return false;
    }
  }

  clearFieldError(input);
  return true;
}

function attachLiveValidation(form) {
  const inputs = form.querySelectorAll("input[required], input[type=tel], input[type=password], input[type=number]");
  inputs.forEach((input) => {
    input.addEventListener("blur", () => validateField(input));
    input.addEventListener("input", () => {
      if (input.classList.contains("invalid")) validateField(input);
    });
  });
}

function validateForm(form) {
  const inputs = form.querySelectorAll("input[required], input[type=tel], input[type=password], input[type=number]");
  let allValid = true;
  inputs.forEach((input) => {
    if (!validateField(input)) allValid = false;
  });
  return allValid;
}

async function handleRegister(event) {
  event.preventDefault();
  const form = event.target;
  const messageEl = document.getElementById("message");
  const submitBtn = form.querySelector('button[type="submit"]');

  if (!validateForm(form)) {
    showMessage(messageEl, "Please fix the highlighted fields.", "error");
    return;
  }

  const payload = {
    full_name: form.full_name.value.trim(),
    phone_number: form.phone_number.value.trim(),
    age: Number(form.age.value),
    gender: form.gender.value,
    country: form.country.value.trim(),
    region: form.region.value.trim(),
    family_contact_phone: form.family_contact_phone.value.trim() || undefined,
    password: form.password.value,
  };

  setButtonLoading(submitBtn, "Creating account...");

  try {
    const res = await fetch(`${AUTH_BASE}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      showMessage(messageEl, data.error || "Registration failed", "error");
      return;
    }

    showMessage(messageEl, "Account created! Redirecting to login...", "success");
    setTimeout(() => (window.location.href = "index.html"), 1200);
  } catch (err) {
    showMessage(messageEl, "Could not reach the server. Is the backend running?", "error");
  } finally {
    resetButtonLoading(submitBtn);
  }
}

async function handleLogin(event) {
  event.preventDefault();
  const form = event.target;
  const messageEl = document.getElementById("message");
  const submitBtn = form.querySelector('button[type="submit"]');

  if (!validateForm(form)) {
    showMessage(messageEl, "Please fix the highlighted fields.", "error");
    return;
  }

  const payload = {
    phone_number: form.phone_number.value.trim(),
    password: form.password.value,
  };

  setButtonLoading(submitBtn, "Logging in...");

  try {
    const res = await fetch(`${AUTH_BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      showMessage(messageEl, data.error || "Login failed", "error");
      return;
    }

    setSession(data.access_token, data.patient);
    window.location.href = "dashboard.html";
  } catch (err) {
    showMessage(messageEl, "Could not reach the server. Is the backend running?", "error");
  } finally {
    resetButtonLoading(submitBtn);
  }
}

function renderProfile(patient) {
  document.getElementById("patient-id").textContent = patient.patient_id;
  document.getElementById("full-name").textContent = patient.full_name;
  document.getElementById("phone-number").textContent = patient.phone_number;
  document.getElementById("age").textContent = patient.age;
  document.getElementById("gender").textContent = patient.gender;
  document.getElementById("country").textContent = patient.country;
  document.getElementById("region").textContent = patient.region;
}

function renderWelcome(patient) {
  const welcomeEl = document.getElementById("welcome-name");
  if (welcomeEl) welcomeEl.textContent = patient.full_name.split(" ")[0];
}

async function loadDashboardStats() {
  const [appointmentsRes, consultationsRes, recordsRes] = await Promise.all([
    authFetch(APPOINTMENTS_BASE, { method: "GET" }),
    authFetch(CONSULTATIONS_BASE, { method: "GET" }),
    authFetch(RECORDS_BASE, { method: "GET" }),
  ]);

  if (appointmentsRes && appointmentsRes.ok) {
    const data = await appointmentsRes.json();
    const upcoming = data.appointments.filter((a) => a.status === "upcoming").length;
    document.getElementById("stat-appointments").textContent = upcoming;
  }
  if (consultationsRes && consultationsRes.ok) {
    const data = await consultationsRes.json();
    const active = data.consultations.filter((c) => c.status !== "closed").length;
    document.getElementById("stat-consultations").textContent = active;
  }
  if (recordsRes && recordsRes.ok) {
    const data = await recordsRes.json();
    document.getElementById("stat-records").textContent = data.records.length;
  }
}

async function initDashboard() {
  const session = requireSessionOrRedirect();
  if (!session) return;

  renderProfile(session.patient);
  renderWelcome(session.patient);
  attachLogout();
  loadDashboardStats();

  const dashEmergencyBtn = document.getElementById("dash-emergency-btn");
  if (dashEmergencyBtn) {
    dashEmergencyBtn.addEventListener("click", () => {
      const realBtn = document.getElementById("emergency-btn");
      if (realBtn) realBtn.click();
    });
  }

  // Validate the token against the server and refresh profile data.
  const res = await authFetch(`${AUTH_BASE}/me`, { method: "GET" });
  if (!res) return;
  if (res.ok) {
    const data = await res.json();
    setSession(session.token, data.patient);
    renderProfile(data.patient);
    renderWelcome(data.patient);
  }
}

function initNavSession() {
  const session = getSession();
  const dashboardLink = document.getElementById("nav-dashboard");
  if (dashboardLink) {
    dashboardLink.style.display = session ? "inline" : "none";
  }
  showExpiredNoticeIfPresent();
}

function initLoginPage() {
  initNavSession();
  attachLiveValidation(document.querySelector("form"));
}

function initRegisterPage() {
  initNavSession();
  attachLiveValidation(document.querySelector("form"));
}

function attachLogout() {
  const btn = document.getElementById("logout-btn");
  if (btn) {
    btn.addEventListener("click", () => {
      clearSession();
      window.location.href = "index.html";
    });
  }
}

function renderList(containerId, items, emptyText) {
  const container = document.getElementById(containerId);
  if (!items.length) {
    container.innerHTML = `<div class="empty-state">${emptyText}</div>`;
    return;
  }
  container.innerHTML = items
    .map(
      (item) => `
      <div class="list-item">
        <div>
          <div class="title">${item.title}</div>
          <div class="subtitle">${item.subtitle}</div>
        </div>
        <div class="list-item-meta">
          <span class="status-badge ${item.status}">${item.status}</span>
          ${item.actions || ""}
        </div>
      </div>`
    )
    .join("");
}

function openModal(modalId) {
  document.getElementById(modalId).classList.add("open");
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.remove("open");
}

function formatDateTime(iso) {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

async function loadAppointments() {
  const res = await authFetch(APPOINTMENTS_BASE, { method: "GET" });
  if (!res) return;
  const data = await res.json();
  const items = data.appointments.map((a) => ({
    title: `${a.doctor_name} — ${a.clinic_name}`,
    subtitle: formatDateTime(a.scheduled_at) + (a.notes ? ` · ${a.notes}` : ""),
    status: a.status,
    actions:
      a.status === "upcoming"
        ? `<button type="button" class="secondary cancel-appointment-btn" data-id="${a.id}">Cancel</button>`
        : "",
  }));
  renderList("appointments-list", items, "No appointments yet.");

  document.querySelectorAll(".cancel-appointment-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const res = await authFetch(`${APPOINTMENTS_BASE}/${btn.dataset.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: "cancelled" }),
      });
      if (res && res.ok) loadAppointments();
    });
  });
}

async function loadRecords() {
  const res = await authFetch(RECORDS_BASE, { method: "GET" });
  if (!res) return;
  const data = await res.json();
  const items = data.records.map((r) => ({
    title: r.title,
    subtitle: `Recorded ${formatDateTime(r.recorded_at)}` + (r.details ? ` · ${r.details}` : ""),
    status: r.status,
  }));
  renderList("records-list", items, "No medical records yet.");
}

async function loadProviderOptions() {
  const select = document.getElementById("provider_id");
  if (!select) return;
  try {
    const res = await fetch("/api/providers");
    const data = await res.json();
    if (!data.providers.length) {
      select.innerHTML = '<option value="" disabled selected>No verified providers available</option>';
      return;
    }
    select.innerHTML = data.providers
      .map((p) => `<option value="${p.provider_id}">${p.full_name} — ${p.specialization} (${p.region})</option>`)
      .join("");
  } catch (err) {
    select.innerHTML = '<option value="" disabled selected>Could not load providers</option>';
  }
}

function initAppointments() {
  if (!requireSessionOrRedirect()) return;
  attachLogout();
  loadAppointments();
  loadProviderOptions();

  const newBtn = document.getElementById("new-appointment-btn");
  if (newBtn) {
    newBtn.addEventListener("click", () => openModal("appointment-modal"));
  }

  const cancelBtn = document.getElementById("appointment-modal-cancel");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => closeModal("appointment-modal"));
  }

  const form = document.getElementById("appointment-form");
  if (form) {
    attachLiveValidation(form);
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const messageEl = document.getElementById("appointment-message");
      const submitBtn = form.querySelector('button[type="submit"]');

      if (!validateForm(form)) {
        showMessage(messageEl, "Please fix the highlighted fields.", "error");
        return;
      }

      const payload = {
        provider_id: form.provider_id.value,
        clinic_name: form.clinic_name.value.trim(),
        scheduled_at: form.scheduled_at.value,
        notes: form.notes.value.trim(),
      };

      setButtonLoading(submitBtn, "Booking...");
      try {
        const res = await authFetch(APPOINTMENTS_BASE, {
          method: "POST",
          body: JSON.stringify(payload),
        });
        if (!res) return;
        const data = await res.json();
        if (!res.ok) {
          showMessage(messageEl, data.error || "Could not book appointment", "error");
          return;
        }
        form.reset();
        showMessage(messageEl, "", "");
        closeModal("appointment-modal");
        loadAppointments();
      } catch (err) {
        showMessage(messageEl, "Could not reach the server. Is the backend running?", "error");
      } finally {
        resetButtonLoading(submitBtn);
      }
    });
  }
}

function initRecords() {
  if (!requireSessionOrRedirect()) return;
  attachLogout();
  loadRecords();

  const newBtn = document.getElementById("new-record-btn");
  if (newBtn) {
    newBtn.addEventListener("click", () => openModal("record-modal"));
  }

  const cancelBtn = document.getElementById("record-modal-cancel");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => closeModal("record-modal"));
  }

  const form = document.getElementById("record-form");
  if (form) {
    attachLiveValidation(form);
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const messageEl = document.getElementById("record-message");
      const submitBtn = form.querySelector('button[type="submit"]');

      if (!validateForm(form)) {
        showMessage(messageEl, "Please fix the highlighted fields.", "error");
        return;
      }

      const payload = {
        title: form.title.value.trim(),
        details: form.details.value.trim(),
        recorded_at: form.recorded_at.value || undefined,
        status: form.status.value,
      };

      setButtonLoading(submitBtn, "Saving...");
      try {
        const res = await authFetch(RECORDS_BASE, {
          method: "POST",
          body: JSON.stringify(payload),
        });
        if (!res) return;
        const data = await res.json();
        if (!res.ok) {
          showMessage(messageEl, data.error || "Could not add record", "error");
          return;
        }
        form.reset();
        showMessage(messageEl, "", "");
        closeModal("record-modal");
        loadRecords();
      } catch (err) {
        showMessage(messageEl, "Could not reach the server. Is the backend running?", "error");
      } finally {
        resetButtonLoading(submitBtn);
      }
    });
  }
}

async function loadConsultations() {
  const res = await authFetch(CONSULTATIONS_BASE, { method: "GET" });
  if (!res) return;
  const data = await res.json();
  const items = data.consultations.map((c) => ({
    title: c.symptoms,
    subtitle: `Reported ${formatDateTime(c.created_at)}` + (c.response_notes ? ` · ${c.response_notes}` : ""),
    status: c.status,
  }));
  renderList("consultations-list", items, "No consultations yet.");
}

function initSymptomReport() {
  if (!requireSessionOrRedirect()) return;
  attachLogout();
  loadConsultations();

  const form = document.getElementById("symptom-form");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const messageEl = document.getElementById("message");
    const submitBtn = form.querySelector('button[type="submit"]');

    const checked = Array.from(form.querySelectorAll('#symptom-checklist input:checked')).map((el) => el.value);
    const freeText = form.free_text.value.trim();
    const symptoms = [...checked, freeText].filter(Boolean).join(", ");

    if (!symptoms) {
      showMessage(messageEl, "Select at least one symptom or describe how you feel.", "error");
      return;
    }

    setButtonLoading(submitBtn, "Submitting...");
    try {
      const res = await authFetch(CONSULTATIONS_BASE, {
        method: "POST",
        body: JSON.stringify({ symptoms, language: getLang ? getLang() : "en" }),
      });
      if (!res) return;
      const data = await res.json();
      if (!res.ok) {
        showMessage(messageEl, data.error || "Could not submit report", "error");
        return;
      }
      showMessage(
        messageEl,
        data.consultation.provider_id
          ? "Submitted! A provider has been assigned to your case."
          : "Submitted! No provider is available right now — you'll be assigned one as soon as possible.",
        "success"
      );
      form.reset();
      loadConsultations();
    } catch (err) {
      showMessage(messageEl, "Could not reach the server. Is the backend running?", "error");
    } finally {
      resetButtonLoading(submitBtn);
    }
  });
}

const OFFLINE_ARTICLES_KEY = "umoja_offline_articles";

async function loadArticles() {
  const lang = getLang();
  let articles = [];
  try {
    const res = await fetch(`/api/health-education?lang=${encodeURIComponent(lang)}`);
    if (!res.ok) throw new Error("bad response");
    const data = await res.json();
    articles = data.articles;
  } catch (err) {
    const cached = localStorage.getItem(OFFLINE_ARTICLES_KEY);
    articles = cached ? JSON.parse(cached).filter((a) => a.language === lang) : [];
  }

  const container = document.getElementById("article-list");
  if (!articles.length) {
    container.innerHTML = '<div class="empty-state">No health education articles available yet.</div>';
    return;
  }

  container.innerHTML = articles
    .map(
      (a) => `
      <div class="article-list-item" data-id="${a.id}">
        <div class="title">${a.title}${a.is_verified ? "" : '<span class="badge-unverified">unverified translation</span>'}</div>
        <div class="subtitle">${a.category}</div>
      </div>`
    )
    .join("");

  container.querySelectorAll(".article-list-item").forEach((el) => {
    el.addEventListener("click", () => {
      const article = articles.find((a) => String(a.id) === el.dataset.id);
      document.getElementById("article-title").textContent = article.title;
      document.getElementById("article-body").textContent = article.body;
      openModal("article-modal");
    });
  });

  container.dataset.loaded = JSON.stringify(articles);
}

function initHealthEducation() {
  if (!requireSessionOrRedirect()) return;
  attachLogout();
  loadArticles();

  document.getElementById("article-modal-close").addEventListener("click", () => closeModal("article-modal"));

  document.getElementById("download-offline-btn").addEventListener("click", () => {
    const container = document.getElementById("article-list");
    const articles = container.dataset.loaded ? JSON.parse(container.dataset.loaded) : [];
    const existing = JSON.parse(localStorage.getItem(OFFLINE_ARTICLES_KEY) || "[]");
    const byId = new Map(existing.map((a) => [a.id, a]));
    articles.forEach((a) => byId.set(a.id, a));
    localStorage.setItem(OFFLINE_ARTICLES_KEY, JSON.stringify(Array.from(byId.values())));
    showMessage(document.getElementById("offline-message"), `${articles.length} article(s) saved for offline reading.`, "success");
  });
}

function initEditProfile() {
  const session = requireSessionOrRedirect();
  if (!session) return;
  attachLogout();

  const { patient } = session;
  const form = document.getElementById("edit-profile-form");
  form.full_name.value = patient.full_name;
  form.phone_number.value = patient.phone_number;
  form.age.value = patient.age;
  form.gender.value = patient.gender;
  form.country.value = patient.country;
  form.region.value = patient.region;
  form.family_contact_phone.value = patient.family_contact_phone || "";

  attachLiveValidation(form);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const messageEl = document.getElementById("message");
    const submitBtn = form.querySelector('button[type="submit"]');

    if (!validateForm(form)) {
      showMessage(messageEl, "Please fix the highlighted fields.", "error");
      return;
    }

    const payload = {
      full_name: form.full_name.value.trim(),
      phone_number: form.phone_number.value.trim(),
      age: Number(form.age.value),
      gender: form.gender.value,
      country: form.country.value.trim(),
      region: form.region.value.trim(),
      family_contact_phone: form.family_contact_phone.value.trim() || null,
    };

    setButtonLoading(submitBtn, "Saving...");

    try {
      const res = await authFetch(`${AUTH_BASE}/me`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      if (!res) return;
      const data = await res.json();

      if (!res.ok) {
        showMessage(messageEl, data.error || "Could not update profile", "error");
        return;
      }

      setSession(session.token, data.patient);
      showMessage(messageEl, "Profile updated! Redirecting...", "success");
      setTimeout(() => (window.location.href = "dashboard.html"), 1000);
    } catch (err) {
      showMessage(messageEl, "Could not reach the server. Is the backend running?", "error");
    } finally {
      resetButtonLoading(submitBtn);
    }
  });
}
