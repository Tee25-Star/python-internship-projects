const form = document.getElementById("monitor-form");
const urlsInput = document.getElementById("urls");
const checkButton = document.getElementById("check-button");
const clearButton = document.getElementById("clear-button");
const presetButton = document.getElementById("preset-examples");
const lastRunLabel = document.getElementById("last-run");
const resultsEmpty = document.getElementById("results-empty");
const resultsWrapper = document.getElementById("results-table-wrapper");
const resultsBody = document.getElementById("results-body");

function setLoading(isLoading) {
  if (isLoading) {
    checkButton.classList.add("is-loading");
    checkButton.disabled = true;
  } else {
    checkButton.classList.remove("is-loading");
    checkButton.disabled = false;
  }
}

function parseUrls(raw) {
  return raw
    .split(/\r?\n|,/)
    .map((x) => x.trim())
    .filter(Boolean);
}

function formatTimestamp(date) {
  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function renderResults(results) {
  if (!results || results.length === 0) {
    resultsBody.innerHTML = "";
    resultsWrapper.classList.add("hidden");
    resultsEmpty.classList.remove("hidden");
    lastRunLabel.textContent = "No results";
    return;
  }

  const rows = results
    .map((r) => {
      const statusClass = r.status === "up" ? "status-pill--up" : "status-pill--down";
      const dotClass = r.status === "up" ? "status-dot--up" : "status-dot--down";
      const statusLabel = r.status === "up" ? "Up" : r.status === "invalid" ? "Invalid" : "Down";
      const httpLabel = r.http_status ?? "—";
      const httpExtraClass = r.http_status == null ? "http-badge--none" : "";
      const latency =
        r.response_time_ms != null ? `${r.response_time_ms.toFixed ? r.response_time_ms.toFixed(1) : r.response_time_ms} ms` : "—";
      const details = r.error || (r.ok ? "Responding normally" : "No response or error");

      return `
        <tr>
          <td class="url-cell">${r.url || "—"}</td>
          <td>
            <span class="status-pill ${statusClass}">
              <span class="status-dot ${dotClass}"></span>
              ${statusLabel}
            </span>
          </td>
          <td>
            <span class="http-badge ${httpExtraClass}">
              ${httpLabel}
            </span>
          </td>
          <td class="latency">${latency}</td>
          <td class="details">${details}</td>
        </tr>
      `;
    })
    .join("");

  resultsBody.innerHTML = rows;
  resultsEmpty.classList.add("hidden");
  resultsWrapper.classList.remove("hidden");
  lastRunLabel.textContent = `Last run at ${formatTimestamp(new Date())}`;
}

async function runCheck(event) {
  event.preventDefault();
  const raw = urlsInput.value || "";
  const urls = parseUrls(raw);

  if (urls.length === 0) {
    urlsInput.focus();
    return;
  }

  setLoading(true);

  try {
    const response = await fetch("/api/check", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ urls }),
    });

    if (!response.ok) {
      throw new Error(`Request failed with ${response.status}`);
    }

    const data = await response.json();
    renderResults(data.results || []);
  } catch (err) {
    console.error(err);
    renderResults([
      {
        url: "—",
        status: "down",
        http_status: null,
        response_time_ms: null,
        ok: false,
        error: "Unable to perform check. Is the server running?",
      },
    ]);
  } finally {
    setLoading(false);
  }
}

function clearForm() {
  urlsInput.value = "";
  renderResults([]);
}

function loadPresetExamples() {
  const examples = [
    "https://example.com",
    "https://www.github.com",
    "https://www.google.com",
    "https://this-domain-should-not-exist-xyz123.com",
  ];
  urlsInput.value = examples.join("\n");
  urlsInput.focus();
}

form.addEventListener("submit", runCheck);
clearButton.addEventListener("click", clearForm);
presetButton.addEventListener("click", loadPresetExamples);

