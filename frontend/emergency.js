// Global emergency-alert control (FR3.1). Injected into every patient page's
// header so the alert button is reachable from anywhere, as the SRS requires.
function injectEmergencyControl() {
  const session = getSession();
  if (!session) return;

  const nav = document.querySelector("header nav");
  if (!nav || document.getElementById("emergency-btn")) return;

  const btn = document.createElement("button");
  btn.id = "emergency-btn";
  btn.type = "button";
  btn.className = "emergency-btn";
  btn.textContent = t("emergency");
  btn.addEventListener("click", openEmergencyModal);
  nav.prepend(btn);

  if (!document.getElementById("emergency-modal")) {
    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";
    overlay.id = "emergency-modal";
    overlay.innerHTML = `
      <div class="modal">
        <h1>Trigger emergency alert</h1>
        <div id="emergency-message" class="message"></div>
        <form id="emergency-form">
          <div class="field">
            <label for="emergency-condition">What's happening?</label>
            <input type="text" id="emergency-condition" name="condition" required />
          </div>
          <div class="field">
            <label for="emergency-location">Location</label>
            <input type="text" id="emergency-location" name="location" required />
            <button type="button" class="secondary" id="use-my-location-btn" style="margin-top:0.5rem">Use my location</button>
          </div>
          <div class="modal-actions">
            <button type="button" class="secondary" id="emergency-modal-cancel">Cancel</button>
            <button type="submit" class="primary emergency-submit">Send emergency alert</button>
          </div>
        </form>
      </div>`;
    document.body.appendChild(overlay);

    document.getElementById("emergency-modal-cancel").addEventListener("click", () => closeModal("emergency-modal"));

    document.getElementById("use-my-location-btn").addEventListener("click", () => {
      if (!navigator.geolocation) return;
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          document.getElementById("emergency-location").value =
            `${pos.coords.latitude.toFixed(5)}, ${pos.coords.longitude.toFixed(5)}`;
        },
        () => {},
      );
    });

    document.getElementById("emergency-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = event.target;
      const messageEl = document.getElementById("emergency-message");
      const submitBtn = form.querySelector('button[type="submit"]');

      setButtonLoading(submitBtn, "Sending...");
      try {
        const res = await authFetch("/api/emergency-alerts", {
          method: "POST",
          body: JSON.stringify({
            condition: form.condition.value.trim(),
            location: form.location.value.trim(),
          }),
        });
        if (!res) return;
        const data = await res.json();
        if (!res.ok) {
          showMessage(messageEl, data.error || "Could not send alert", "error");
          return;
        }
        showMessage(messageEl, `Alert sent. ${data.providers_notified} provider(s) notified.`, "success");
        form.reset();
        setTimeout(() => closeModal("emergency-modal"), 1500);
      } catch (err) {
        showMessage(messageEl, "Could not reach the server.", "error");
      } finally {
        resetButtonLoading(submitBtn);
      }
    });
  }
}

function openEmergencyModal() {
  openModal("emergency-modal");
}

document.addEventListener("DOMContentLoaded", injectEmergencyControl);
