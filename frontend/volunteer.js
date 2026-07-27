const VOLUNTEER_SESSION_KEY = "umoja_volunteer_session";

function getVolunteerSession() {
  const raw = localStorage.getItem(VOLUNTEER_SESSION_KEY);
  return raw ? JSON.parse(raw) : null;
}

function setVolunteerSession(token, volunteer) {
  localStorage.setItem(VOLUNTEER_SESSION_KEY, JSON.stringify({ token, volunteer }));
}

function clearVolunteerSession() {
  localStorage.removeItem(VOLUNTEER_SESSION_KEY);
}

function requireVolunteerSessionOrRedirect() {
  const session = getVolunteerSession();
  if (!session) {
    window.location.href = "volunteer-login.html";
    return null;
  }
  return session;
}

async function volunteerAuthFetch(path, options = {}) {
  const session = getVolunteerSession();
  if (!session) {
    window.location.href = "volunteer-login.html";
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
    clearVolunteerSession();
    window.location.href = "volunteer-login.html";
    return null;
  }
  return res;
}

function attachVolunteerLogout() {
  const btn = document.getElementById("logout-btn");
  if (btn) {
    btn.addEventListener("click", () => {
      clearVolunteerSession();
      window.location.href = "volunteer-login.html";
    });
  }
}

async function handleVolunteerRegister(event) {
  event.preventDefault();
  const form = event.target;
  const messageEl = document.getElementById("message");
  const submitBtn = form.querySelector('button[type="submit"]');
  setButtonLoading(submitBtn, "Registering...");
  try {
    const res = await fetch("/api/auth/volunteer/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: form.full_name.value.trim(),
        phone_number: form.phone_number.value.trim(),
        assigned_region: form.assigned_region.value.trim(),
        password: form.password.value,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      showMessage(messageEl, data.error || "Registration failed", "error");
      return;
    }
    showMessage(messageEl, "Account created! Redirecting to login...", "success");
    setTimeout(() => (window.location.href = "volunteer-login.html"), 1200);
  } catch (err) {
    showMessage(messageEl, "Could not reach the server.", "error");
  } finally {
    resetButtonLoading(submitBtn);
  }
}

async function handleVolunteerLogin(event) {
  event.preventDefault();
  const form = event.target;
  const messageEl = document.getElementById("message");
  const submitBtn = form.querySelector('button[type="submit"]');
  setButtonLoading(submitBtn, "Logging in...");
  try {
    const res = await fetch("/api/auth/volunteer/login", {
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
    setVolunteerSession(data.access_token, data.volunteer);
    window.location.href = "volunteer-dashboard.html";
  } catch (err) {
    showMessage(messageEl, "Could not reach the server.", "error");
  } finally {
    resetButtonLoading(submitBtn);
  }
}

async function loadVolunteerActivity() {
  const [consultRes, alertRes] = await Promise.all([
    volunteerAuthFetch("/api/consultations"),
    volunteerAuthFetch("/api/emergency-alerts"),
  ]);

  if (consultRes) {
    const data = await consultRes.json();
    const container = document.getElementById("volunteer-consultations-list");
    container.innerHTML = data.consultations.length
      ? data.consultations
          .map(
            (c) => `
        <div class="list-item">
          <div>
            <div class="title">${c.symptoms}</div>
            <div class="subtitle">Patient ${c.patient_id} · ${formatDateTime(c.created_at)}</div>
          </div>
          <span class="status-badge ${c.status}">${c.status}</span>
        </div>`
          )
          .join("")
      : '<div class="empty-state">No consultations submitted yet.</div>';
  }

  if (alertRes) {
    const data = await alertRes.json();
    const container = document.getElementById("volunteer-alerts-list");
    container.innerHTML = data.emergency_alerts.length
      ? data.emergency_alerts
          .map(
            (a) => `
        <div class="list-item">
          <div>
            <div class="title">${a.condition}</div>
            <div class="subtitle">${mapsLink(a.location)} · ${formatDateTime(a.created_at)}</div>
          </div>
          <span class="status-badge ${a.status}">${a.status}</span>
        </div>`
          )
          .join("")
      : '<div class="empty-state">No emergency alerts triggered yet.</div>';
  }
}

function initVolunteerDashboard() {
  if (!requireVolunteerSessionOrRedirect()) return;
  attachVolunteerLogout();
  loadVolunteerActivity();

  const consultForm = document.getElementById("volunteer-consultation-form");
  consultForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const messageEl = document.getElementById("consultation-message");
    const submitBtn = consultForm.querySelector('button[type="submit"]');
    setButtonLoading(submitBtn, "Submitting...");
    try {
      const res = await volunteerAuthFetch("/api/consultations", {
        method: "POST",
        body: JSON.stringify({
          patient_phone_number: consultForm.patient_phone_number.value.trim(),
          symptoms: consultForm.symptoms.value.trim(),
        }),
      });
      if (!res) return;
      const data = await res.json();
      if (!res.ok) {
        showMessage(messageEl, data.error || "Could not submit consultation", "error");
        return;
      }
      showMessage(messageEl, "Consultation submitted.", "success");
      consultForm.reset();
      loadVolunteerActivity();
    } catch (err) {
      showMessage(messageEl, "Could not reach the server.", "error");
    } finally {
      resetButtonLoading(submitBtn);
    }
  });

  const alertForm = document.getElementById("volunteer-alert-form");
  alertForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const messageEl = document.getElementById("alert-message");
    const submitBtn = alertForm.querySelector('button[type="submit"]');
    setButtonLoading(submitBtn, "Sending...");
    try {
      const res = await volunteerAuthFetch("/api/emergency-alerts", {
        method: "POST",
        body: JSON.stringify({
          patient_phone_number: alertForm.patient_phone_number.value.trim(),
          location: alertForm.location.value.trim(),
          condition: alertForm.condition.value.trim(),
        }),
      });
      if (!res) return;
      const data = await res.json();
      if (!res.ok) {
        showMessage(messageEl, data.error || "Could not trigger alert", "error");
        return;
      }
      showMessage(messageEl, `Alert sent. ${data.providers_notified} provider(s) notified.`, "success");
      alertForm.reset();
      loadVolunteerActivity();
    } catch (err) {
      showMessage(messageEl, "Could not reach the server.", "error");
    } finally {
      resetButtonLoading(submitBtn);
    }
  });
}
