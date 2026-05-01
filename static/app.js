// ── Theme toggle (persistent) ──
const themeBtn = document.getElementById("themeBtn");

function toggleTheme() {
  document.body.classList.toggle("dark");
  localStorage.setItem("theme", document.body.classList.contains("dark") ? "dark" : "light");
}

(function initTheme() {
  const saved = localStorage.getItem("theme");
  if (saved === "dark") document.body.classList.add("dark");
})();


// ── Comorbidity toggle ──
function toggleComorbidity() {
  const select = document.getElementById("comorbidity_select");
  const box = document.getElementById("comorbidity_textbox");

  box.classList.toggle("hidden", select.value !== "1");
}


// ── Symptom toggles ──
document.querySelectorAll(".sym-check").forEach(cb => {
  cb.addEventListener("change", () => {
    const hiddenInput = cb.parentElement.querySelector("input[type='hidden']");
    const badge = cb.parentElement.querySelector(".sym-badge");

    hiddenInput.value = cb.checked ? 1 : 0;
    badge.textContent = cb.checked ? "Yes" : "No";
  });
});


// ── Tooltip system ──
const hintBox = document.getElementById("hintBox");

document.querySelectorAll("[data-hint]").forEach(el => {
  el.addEventListener("mouseenter", e => {
    hintBox.textContent = el.dataset.hint;
    hintBox.classList.remove("hidden");
  });

  el.addEventListener("mousemove", e => {
    hintBox.style.top = e.clientY + 15 + "px";
    hintBox.style.left = e.clientX + 15 + "px";
  });

  el.addEventListener("mouseleave", () => {
    hintBox.classList.add("hidden");
  });
});


// ── Form submission (AJAX) ──
const form = document.getElementById("predForm");
const btn = document.getElementById("submitBtn");
const btnText = document.getElementById("btnText");
const spinner = document.getElementById("btnSpinner");
const arrow = document.getElementById("btnArrow");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  // UI loading state
  btn.disabled = true;
  spinner.classList.remove("hidden");
  arrow.style.display = "none";
  btnText.textContent = "Analysing...";

  const formData = new FormData(form);

  try {
    const res = await fetch("/predict", {
      method: "POST",
      body: formData
    });

    const data = await res.json();

    if (data.error) throw new Error(data.error);

    showResult(data);

  } catch (err) {
    showError(err.message);
  }

  // Reset button
  btn.disabled = false;
  spinner.classList.add("hidden");
  arrow.style.display = "block";
  btnText.textContent = "Analyse Severity";
});


// ── Result display ──
function showResult(data) {
  const panel = document.getElementById("resultPanel");
  const badge = document.getElementById("resultBadge");
  const severity = document.getElementById("resultSeverity");
  const advice = document.getElementById("resultAdvice");
  const confBars = document.getElementById("confBars");

  panel.classList.remove("hidden");

  badge.className = `result-badge badge-${data.color}`;
  badge.textContent = data.label;

  severity.className = `result-severity sev-${data.color}`;
  severity.textContent = data.label;

  advice.textContent = data.advice;

  // Confidence bars
  confBars.innerHTML = "";
  for (let key in data.confidence) {
    const val = data.confidence[key];

    const row = document.createElement("div");
    row.className = "conf-item";

    row.innerHTML = `
      <div class="conf-label">${key}</div>
      <div class="conf-track">
        <div class="conf-bar" style="width:${val}%"></div>
      </div>
      <div class="conf-pct">${val}%</div>
    `;

    confBars.appendChild(row);
  }

  panel.scrollIntoView({ behavior: "smooth" });
}

function closeResult() {
  document.getElementById("resultPanel").classList.add("hidden");
}


// ── Error toast ──
function showError(msg) {
  const toast = document.getElementById("errorToast");
  toast.textContent = msg;
  toast.classList.remove("hidden");

  setTimeout(() => toast.classList.add("hidden"), 3000);
}