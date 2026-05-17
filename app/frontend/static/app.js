const apiStatus = document.getElementById("api-status");
const presetsContent = document.getElementById("presets-content");
const singleTab = document.getElementById("single-tab");
const sequenceTab = document.getElementById("sequence-tab");
const singleFormSection = document.getElementById("single-form-section");
const sequenceFormSection = document.getElementById("sequence-form-section");
const singleForm = document.getElementById("single-form");
const sequenceForm = document.getElementById("sequence-form");
const summaryCards = document.getElementById("summary-cards");
const resultJson = document.getElementById("result-json");

const navOverhead = document.getElementById("nav-overhead");
const navTransport = document.getElementById("nav-transport");
const viewOverhead = document.getElementById("view-overhead");
const viewTransport = document.getElementById("view-transport");
const pageTitle = document.getElementById("page-title");
const pageDescription = document.getElementById("page-description");

const availableReports = document.getElementById("available-reports");
const insightsCards = document.getElementById("insights-cards");
const transportSummaryCards = document.getElementById("transport-summary-cards");
const realtimeSummaryCards = document.getElementById("realtime-summary-cards");
const validationSummaryCards = document.getElementById("validation-summary-cards");
const requestResponseTable = document.getElementById("request-response-table");
const realtimeTable = document.getElementById("realtime-table");
const validationTable = document.getElementById("validation-table");
const reportSelect = document.getElementById("report-select");
const loadReportButton = document.getElementById("load-report-button");
const reportViewer = document.getElementById("report-viewer");

function setMode(mode) {
  const singleActive = mode === "single";

  singleTab.classList.toggle("active", singleActive);
  sequenceTab.classList.toggle("active", !singleActive);

  singleFormSection.classList.toggle("hidden", !singleActive);
  sequenceFormSection.classList.toggle("hidden", singleActive);
}

function setMainView(view) {
  const overheadActive = view === "overhead";

  navOverhead.classList.toggle("active", overheadActive);
  navTransport.classList.toggle("active", !overheadActive);

  viewOverhead.classList.toggle("hidden", !overheadActive);
  viewTransport.classList.toggle("hidden", overheadActive);

  if (overheadActive) {
    pageTitle.textContent = "Transmission Overhead Calculator";
    pageDescription.textContent =
      "Analiza narzutu transmisji dla pojedynczej wiadomości i sekwencji wiadomości w modelu Ethernet II + IPv4 + TCP.";
  } else {
    pageTitle.textContent = "Transport Comparison Dashboard";
    pageDescription.textContent =
      "Przegląd wcześniej wygenerowanych wyników dla request-response, realtime, walidacji i raportów zbiorczych.";
    loadReportsDashboard();
  }
}

function renderSummary(cards) {
  summaryCards.innerHTML = "";

  for (const card of cards) {
    const div = document.createElement("div");
    div.className = "summary-card";
    div.innerHTML = `
      <span class="label">${card.label}</span>
      <span class="value">${card.value}</span>
    `;
    summaryCards.appendChild(div);
  }
}

function renderCardGroup(container, cards) {
  container.innerHTML = "";

  for (const card of cards) {
    const div = document.createElement("div");
    div.className = "summary-card";
    div.innerHTML = `
      <span class="label">${card.label}</span>
      <span class="value">${card.value}</span>
    `;
    container.appendChild(div);
  }
}

function renderResult(data) {
  resultJson.textContent = JSON.stringify(data, null, 2);
}

function renderTable(container, columns, rows) {
  if (!rows.length) {
    container.innerHTML = `<div class="summary-card muted">No data available.</div>`;
    return;
  }

  const headerHtml = columns.map((column) => `<th>${column.label}</th>`).join("");
  const bodyHtml = rows
    .map((row) => {
      const cells = columns
        .map((column) => `<td>${column.render ? column.render(row) : row[column.key]}</td>`)
        .join("");
      return `<tr>${cells}</tr>`;
    })
    .join("");

  container.innerHTML = `
    <div class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>${headerHtml}</tr>
        </thead>
        <tbody>
          ${bodyHtml}
        </tbody>
      </table>
    </div>
  `;
}

async function checkHealth() {
  try {
    const response = await fetch("/health");
    const data = await response.json();

    if (data.status === "ok") {
      apiStatus.textContent = "API ready";
      apiStatus.classList.add("ok");
      apiStatus.classList.remove("error");
    } else {
      throw new Error("Unexpected health response");
    }
  } catch (error) {
    apiStatus.textContent = "API unavailable";
    apiStatus.classList.add("error");
    apiStatus.classList.remove("ok");
  }
}

async function loadPresets() {
  try {
    const response = await fetch("/presets");
    const data = await response.json();

    presetsContent.innerHTML = `
      <strong>Layers</strong>
      <ul class="preset-list">
        <li>Ethernet: ${data.layer_presets.ethernet.header_size_bytes}B header + ${data.layer_presets.ethernet.trailer_size_bytes}B trailer</li>
        <li>IPv4: ${data.layer_presets.ipv4.header_size_bytes}B header</li>
        <li>TCP: ${data.layer_presets.tcp.header_size_bytes}B header</li>
      </ul>
      <strong>Protocols</strong>
      <ul class="preset-list">
        <li>HTTP: ${data.protocol_presets.http.default_header_overhead_bytes}B</li>
        <li>WebSocket: ${data.protocol_presets.websocket.default_header_overhead_bytes}B</li>
        <li>gRPC: ${data.protocol_presets.grpc.default_header_overhead_bytes}B</li>
      </ul>
    `;
  } catch (error) {
    presetsContent.textContent = "Could not load presets.";
  }
}

function buildSinglePayload(formData) {
  return {
    application_protocol: formData.get("application_protocol"),
    payload_encoding: formData.get("payload_encoding"),
    payload_size_bytes: Number(formData.get("payload_size_bytes")),
    message_count: Number(formData.get("message_count")),
    message_frequency_hz: Number(formData.get("message_frequency_hz")),
    mtu_bytes: Number(formData.get("mtu_bytes")),
  };
}

function buildSequencePayload(formData) {
  const payloadSizes = formData
    .get("payload_sizes_bytes")
    .split(",")
    .map((item) => Number(item.trim()))
    .filter((item) => !Number.isNaN(item));

  return {
    application_protocol: formData.get("application_protocol"),
    payload_encoding: formData.get("payload_encoding"),
    payload_sizes_bytes: payloadSizes,
    aggregation_mode: formData.get("aggregation_mode"),
    batch_size: Number(formData.get("batch_size")),
    message_frequency_hz: Number(formData.get("message_frequency_hz")),
    mtu_bytes: Number(formData.get("mtu_bytes")),
  };
}

async function analyzeSingle(event) {
  event.preventDefault();

  const payload = buildSinglePayload(new FormData(singleForm));

  const response = await fetch("/analyze/single", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    renderSummary([{ label: "Error", value: "Request failed" }]);
    renderResult(data);
    return;
  }

  renderSummary([
    {
      label: "Total transmitted bytes",
      value: String(data.layer_breakdown.total_transmitted_bytes),
    },
    {
      label: "Frame count",
      value: String(data.frame_analysis.frame_count),
    },
    {
      label: "Payload efficiency",
      value: data.efficiency.payload_efficiency_ratio.toFixed(4),
    },
    {
      label: "Required bitrate [kbps]",
      value: data.efficiency.required_bitrate_kbps.toFixed(4),
    },
  ]);

  renderResult(data);
}

async function analyzeSequence(event) {
  event.preventDefault();

  const payload = buildSequencePayload(new FormData(sequenceForm));

  const response = await fetch("/analyze/sequence", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    renderSummary([{ label: "Error", value: "Request failed" }]);
    renderResult(data);
    return;
  }

  renderSummary([
    {
      label: "Aggregated message count",
      value: String(data.aggregated_message_count),
    },
    {
      label: "Total transmitted bytes",
      value: String(data.total_transmitted_bytes),
    },
    {
      label: "Total frame count",
      value: String(data.total_frame_count),
    },
    {
      label: "Payload efficiency",
      value: data.payload_efficiency_ratio.toFixed(4),
    },
  ]);

  renderResult(data);
}

async function fetchReport(key) {
  const response = await fetch(`/reports/${key}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch report: ${key}`);
  }
  return await response.json();
}

function bestRowBy(rows, field, predicate = null) {
  const filtered = predicate ? rows.filter(predicate) : rows;
  return [...filtered].sort((a, b) => a[field] - b[field])[0];
}

function worstRowBy(rows, field) {
  return [...rows].sort((a, b) => b[field] - a[field])[0];
}

async function loadReportsDashboard() {
  try {
    const available = await fetchReport("available");
    availableReports.innerHTML = "";

    available.reports.forEach((report) => {
      const div = document.createElement("div");
      div.className = "summary-card";
      div.innerHTML = `
        <span class="label">${report.key}</span>
        <span class="value ${report.exists ? "report-ok" : "report-missing"}">
          ${report.exists ? "available" : "missing"}
        </span>
      `;
      availableReports.appendChild(div);
    });

    const requestResponse = await fetchReport("request-response");
    const realtime = await fetchReport("realtime-fetch");
    const validation = await fetchReport("validation-cost");
    const interpretation = await fetchReport("interpretation");
    const messageSize = await fetchReport("message-size");

    const bestSet = bestRowBy(requestResponse, "avg_ms", (row) => row.operation === "set_value");
    const bestGet = bestRowBy(requestResponse, "avg_ms", (row) => row.operation === "get_value");
    const bestRealtime = bestRowBy(realtime, "avg_ms");
    const smallestPayload = [...messageSize].sort((a, b) => a.request_size_bytes - b.request_size_bytes)[0];
    const fastestValidation = bestRowBy(validation, "avg_us");
    const slowestValidation = worstRowBy(validation, "avg_us");

    renderCardGroup(insightsCards, [
      {
        label: "Best set_value transport",
        value: `${bestSet.transport} (${bestSet.avg_ms.toFixed(3)} ms)`,
      },
      {
        label: "Best get_value transport",
        value: `${bestGet.transport} (${bestGet.avg_ms.toFixed(3)} ms)`,
      },
      {
        label: "Best realtime scenario result",
        value: `${bestRealtime.transport} (${bestRealtime.avg_ms.toFixed(3)} ms)`,
      },
      {
        label: "Smallest request payload",
        value: `${smallestPayload.transport}/${smallestPayload.operation}`,
      },
    ]);

    renderCardGroup(transportSummaryCards, [
      {
        label: "set_value best avg [ms]",
        value: Math.min(...requestResponse.filter((r) => r.operation === "set_value").map((r) => r.avg_ms)).toFixed(3),
      },
      {
        label: "get_value best avg [ms]",
        value: Math.min(...requestResponse.filter((r) => r.operation === "get_value").map((r) => r.avg_ms)).toFixed(3),
      },
      {
        label: "Rows loaded",
        value: String(requestResponse.length),
      },
      {
        label: "Transports",
        value: Array.from(new Set(requestResponse.map((r) => r.transport))).join(", "),
      },
    ]);

    renderCardGroup(realtimeSummaryCards, [
      {
        label: "non_empty_fetch best avg [ms]",
        value: Math.min(...realtime.filter((r) => r.scenario === "non_empty_fetch").map((r) => r.avg_ms)).toFixed(3),
      },
      {
        label: "empty_fetch best avg [ms]",
        value: Math.min(...realtime.filter((r) => r.scenario === "empty_fetch").map((r) => r.avg_ms)).toFixed(3),
      },
      {
        label: "Rows loaded",
        value: String(realtime.length),
      },
      {
        label: "Expected event counts",
        value: Array.from(new Set(realtime.map((r) => r.expected_event_count))).join(", "),
      },
    ]);

    renderCardGroup(validationSummaryCards, [
      {
        label: "Fastest validation avg [us]",
        value: fastestValidation.avg_us.toFixed(3),
      },
      {
        label: "Slowest validation avg [us]",
        value: slowestValidation.avg_us.toFixed(3),
      },
      {
        label: "Scenarios loaded",
        value: String(validation.length),
      },
      {
        label: "Fastest scenario",
        value: fastestValidation.scenario,
      },
    ]);

    renderTable(
      requestResponseTable,
      [
        { key: "transport", label: "Transport" },
        { key: "operation", label: "Operation" },
        { key: "avg_ms", label: "Avg [ms]", render: (row) => row.avg_ms.toFixed(3) },
        { key: "median_ms", label: "Median [ms]", render: (row) => row.median_ms.toFixed(3) },
        { key: "min_ms", label: "Min [ms]", render: (row) => row.min_ms.toFixed(3) },
        { key: "max_ms", label: "Max [ms]", render: (row) => row.max_ms.toFixed(3) },
      ],
      requestResponse
    );

    renderTable(
      realtimeTable,
      [
        { key: "transport", label: "Transport" },
        { key: "scenario", label: "Scenario" },
        { key: "avg_ms", label: "Avg [ms]", render: (row) => row.avg_ms.toFixed(3) },
        { key: "median_ms", label: "Median [ms]", render: (row) => row.median_ms.toFixed(3) },
        { key: "expected_event_count", label: "Event count" },
      ],
      realtime
    );

    renderTable(
      validationTable,
      [
        { key: "scenario", label: "Scenario" },
        { key: "expected_outcome", label: "Expected outcome" },
        { key: "avg_us", label: "Avg [us]", render: (row) => row.avg_us.toFixed(3) },
        { key: "median_us", label: "Median [us]", render: (row) => row.median_us.toFixed(3) },
        { key: "min_us", label: "Min [us]", render: (row) => row.min_us.toFixed(3) },
        { key: "max_us", label: "Max [us]", render: (row) => row.max_us.toFixed(3) },
      ],
      validation
    );

    reportViewer.textContent = interpretation.content;
  } catch (error) {
    availableReports.innerHTML = `<div class="summary-card muted">Could not load reports.</div>`;
    insightsCards.innerHTML = `<div class="summary-card muted">Could not load insights.</div>`;
    transportSummaryCards.innerHTML = `<div class="summary-card muted">Could not load request-response data.</div>`;
    realtimeSummaryCards.innerHTML = `<div class="summary-card muted">Could not load realtime data.</div>`;
    validationSummaryCards.innerHTML = `<div class="summary-card muted">Could not load validation data.</div>`;
    requestResponseTable.innerHTML = "";
    realtimeTable.innerHTML = "";
    validationTable.innerHTML = "";
    reportViewer.textContent = "Could not load report content.";
  }
}

async function loadSelectedReport() {
  try {
    const key = reportSelect.value;
    const report = await fetchReport(key);

    if (typeof report === "object" && report.content) {
      reportViewer.textContent = report.content;
    } else {
      reportViewer.textContent = JSON.stringify(report, null, 2);
    }
  } catch (error) {
    reportViewer.textContent = "Could not load selected report.";
  }
}

singleTab.addEventListener("click", () => setMode("single"));
sequenceTab.addEventListener("click", () => setMode("sequence"));
singleForm.addEventListener("submit", analyzeSingle);
sequenceForm.addEventListener("submit", analyzeSequence);

navOverhead.addEventListener("click", () => setMainView("overhead"));
navTransport.addEventListener("click", () => setMainView("transport"));
loadReportButton.addEventListener("click", loadSelectedReport);

setMode("single");
setMainView("overhead");
checkHealth();
loadPresets();