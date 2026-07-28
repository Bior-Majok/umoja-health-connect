const I18N_STORAGE_KEY = "umoja_lang";

function getLang() {
  return localStorage.getItem(I18N_STORAGE_KEY) || "en";
}

function setLang(lang) {
  localStorage.setItem(I18N_STORAGE_KEY, lang);
}

let _labels = {};

async function loadLabels() {
  const lang = getLang();
  try {
    const res = await fetch(`/api/labels?lang=${encodeURIComponent(lang)}`);
    const data = await res.json();
    _labels = data.labels;
    document.documentElement.setAttribute("lang", data.language);
    document.documentElement.setAttribute("dir", data.dir);
  } catch (err) {
    _labels = {};
  }
  applyLabels();
  document.dispatchEvent(new CustomEvent("i18n:changed"));
}

function t(key) {
  return _labels[key] || key;
}

function applyLabels() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.setAttribute("placeholder", t(el.dataset.i18nPlaceholder));
  });
}

function initLanguageSwitcher() {
  const select = document.getElementById("language-select");
  if (!select) return;
  select.value = getLang();
  select.addEventListener("change", () => {
    setLang(select.value);
    loadLabels();
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initLanguageSwitcher();
  loadLabels();
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  });
}
