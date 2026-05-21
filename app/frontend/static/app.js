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

const requestResponseExperimentForm = document.getElementById("request-response-experiment-form");
const loadRequestResponseDefaultsButton = document.getElementById("load-request-response-defaults");
const requestResponseRunSummary = document.getElementById("request-response-run-summary");
const requestResponseRunTable = document.getElementById("request-response-run-table");
const requestResponseRunJson = document.getElementById("request-response-run-json");

const realtimeExperimentForm = document.getElementById("realtime-experiment-form");
const loadRealtimeDefaultsButton = document.getElementById("load-realtime-defaults");
const realtimeRunSummary = document.getElementById("realtime-run-summary");
const realtimeRunTable = document.getElementById("realtime-run-table");
const realtimeRunJson = document.getElementById("realtime-run-json");

const validationExperimentForm = document.getElementById("validation-experiment-form");
const loadValidationDefaultsButton = document.getElementById("load-validation-defaults");
const validationRunSummary = document.getElementById("validation-run-summary");
const validationRunTable = document.getElementById("validation-run-table");
const validationRunJson = document.getElementById("validation-run-json");

const serializationExperimentForm = document.getElementById("serialization-experiment-form");
const loadSerializationDefaultsButton = document.getElementById("load-serialization-defaults");
const serializationRunSummary = document.getElementById("serialization-run-summary");
const serializationRunTable = document.getElementById("serialization-run-table");
const serializationRunJson = document.getElementById("serialization-run-json");

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
const effectiveSettingsBox = document.getElementById("effective-settings-box");
const environmentStatusForm = document.getElementById("environment-status-form");
const loadEnvironmentDefaultsButton = document.getElementById("load-environment-defaults");
const environmentStatusSummary = document.getElementById("environment-status-summary");
const environmentStatusTable = document.getElementById("environment-status-table");
const recentRunsForm = document.getElementById("recent-runs-form");
const recentRunsSummary = document.getElementById("recent-runs-summary");
const recentRunsTable = document.getElementById("recent-runs-table");
const savedRunDetailForm = document.getElementById("saved-run-detail-form");
const savedRunDetailSummary = document.getElementById("saved-run-detail-summary");
const savedRunDetailJson = document.getElementById("saved-run-detail-json");

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
      "Przegląd wcześniej wygenerowanych wyników dla request-response, realtime, walidacji i raportów zbiorczych oraz uruchamianie eksperymentów request-response, realtime, validation i serialization.";
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

function buildEnvironmentStatusPayload(formData) {
  return {
    http_health_url: formData.get("http_health_url"),
    ws_health_url: formData.get("ws_health_url"),
    grpc_address: formData.get("grpc_address"),
    timeout_seconds: Number(formData.get("timeout_seconds")),
  };
}

function getPersistenceOptions(form, checkboxName, runLabelName) {
  const saveResult = form.querySelector(`input[name="${checkboxName}"]`).checked;
  const runLabel = form.querySelector(`input[name="${runLabelName}"]`).value.trim();

  return {
    saveResult,
    runLabel,
  };
}

function buildExperimentRunUrl(basePath, saveResult, runLabel) {
  const params = new URLSearchParams();

  if (saveResult) {
    params.set("save_result", "true");
  }

  if (runLabel) {
    params.set("run_label", runLabel);
  }

  const query = params.toString();
  return query ? `${basePath}?${query}` : basePath;
}

function buildRecentRunsUrl(limit, experimentName) {
  const params = new URLSearchParams();
  params.set("limit", String(limit));

  if (experimentName) {
    params.set("experiment_name", experimentName);
  }

  return `/experiment-runs/recent?${params.toString()}`;
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

function getNestedValue(obj, path) {
  return path.split(".").reduce((acc, part) => acc[part], obj);
}

function bestRowBy(rows, field, predicate = null) {
  const filtered = predicate ? rows.filter(predicate) : rows;
  return [...filtered].sort((a, b) => getNestedValue(a, field) - getNestedValue(b, field))[0];
}

function worstRowBy(rows, field) {
  return [...rows].sort((a, b) => getNestedValue(b, field) - getNestedValue(a, field))[0];
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

    const profileItems = Object.entries(data.transmission_profiles)
      .map(
        ([key, value]) =>
          `<li>${key}: MTU ${value.mtu_bytes}, IPv4 ${value.ipv4_header_size_bytes}B, TCP ${value.tcp_header_size_bytes}B</li>`
      )
      .join("");

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
      <strong>Transmission profiles</strong>
      <ul class="preset-list">
        ${profileItems}
      </ul>
    `;
  } catch (error) {
    presetsContent.textContent = "Could not load presets.";
  }
}

function buildSinglePayload(formData) {
  const payload = {
    application_protocol: formData.get("application_protocol"),
    payload_encoding: formData.get("payload_encoding"),
    transmission_profile: formData.get("transmission_profile"),
    payload_size_bytes: Number(formData.get("payload_size_bytes")),
    message_count: Number(formData.get("message_count")),
    message_frequency_hz: Number(formData.get("message_frequency_hz")),
  };

  appendOptionalNumber(payload, "mtu_bytes", formData.get("mtu_bytes"));
  appendOptionalNumber(
    payload,
    "application_header_overhead_bytes",
    formData.get("application_header_overhead_bytes")
  );
  appendOptionalNumber(
    payload,
    "ethernet_header_size_bytes",
    formData.get("ethernet_header_size_bytes")
  );
  appendOptionalNumber(
    payload,
    "ethernet_trailer_size_bytes",
    formData.get("ethernet_trailer_size_bytes")
  );
  appendOptionalNumber(
    payload,
    "ethernet_min_payload_bytes",
    formData.get("ethernet_min_payload_bytes")
  );
  appendOptionalNumber(
    payload,
    "ipv4_header_size_bytes",
    formData.get("ipv4_header_size_bytes")
  );
  appendOptionalNumber(
    payload,
    "tcp_header_size_bytes",
    formData.get("tcp_header_size_bytes")
  );

  return payload;
}

function buildSequencePayload(formData) {
  const payloadSizes = formData
    .get("payload_sizes_bytes")
    .split(",")
    .map((item) => Number(item.trim()))
    .filter((item) => !Number.isNaN(item));

  const payload = {
    application_protocol: formData.get("application_protocol"),
    payload_encoding: formData.get("payload_encoding"),
    transmission_profile: formData.get("transmission_profile"),
    payload_sizes_bytes: payloadSizes,
    aggregation_mode: formData.get("aggregation_mode"),
    batch_size: Number(formData.get("batch_size")),
    message_frequency_hz: Number(formData.get("message_frequency_hz")),
  };

  appendOptionalNumber(payload, "mtu_bytes", formData.get("mtu_bytes"));
  appendOptionalNumber(
    payload,
    "application_header_overhead_bytes",
    formData.get("application_header_overhead_bytes")
  );
  appendOptionalNumber(
    payload,
    "ethernet_header_size_bytes",
    formData.get("ethernet_header_size_bytes")
  );
  appendOptionalNumber(
    payload,
    "ethernet_trailer_size_bytes",
    formData.get("ethernet_trailer_size_bytes")
  );
  appendOptionalNumber(
    payload,
    "ethernet_min_payload_bytes",
    formData.get("ethernet_min_payload_bytes")
  );
  appendOptionalNumber(
    payload,
    "ipv4_header_size_bytes",
    formData.get("ipv4_header_size_bytes")
  );
  appendOptionalNumber(
    payload,
    "tcp_header_size_bytes",
    formData.get("tcp_header_size_bytes")
  );

  return payload;
}

function parseOptionalNumber(value) {
  if (value === null || value === undefined) {
    return undefined;
  }

  const normalized = String(value).trim();
  if (normalized === "") {
    return undefined;
  }

  const parsed = Number(normalized);
  return Number.isNaN(parsed) ? undefined : parsed;
}

function appendOptionalNumber(target, key, value) {
  const parsed = parseOptionalNumber(value);
  if (parsed !== undefined) {
    target[key] = parsed;
  }
}

function renderEffectiveSettings(data) {
  if (!data.effective_settings) {
    effectiveSettingsBox.innerHTML =
      `<div class="summary-card muted">No effective settings available.</div>`;
    return;
  }

  const settings = data.effective_settings;

  renderCardGroup(effectiveSettingsBox, [
    { label: "Profile", value: settings.transmission_profile },
    { label: "MTU [B]", value: String(settings.mtu_bytes) },
    { label: "Ethernet header [B]", value: String(settings.ethernet_header_size_bytes) },
    { label: "Ethernet trailer [B]", value: String(settings.ethernet_trailer_size_bytes) },
    { label: "Ethernet minimum payload [B]", value: String(settings.ethernet_min_payload_bytes) },
    { label: "IPv4 header [B]", value: String(settings.ipv4_header_size_bytes) },
    { label: "TCP header [B]", value: String(settings.tcp_header_size_bytes) },
    { label: "App header overhead [B]", value: String(settings.application_header_overhead_bytes) },
  ]);
}

function getSelectedRequestResponseTransports() {
  const transports = [];
  if (requestResponseExperimentForm.querySelector('input[name="transport_http"]').checked) transports.push("http");
  if (requestResponseExperimentForm.querySelector('input[name="transport_ws"]').checked) transports.push("ws");
  if (requestResponseExperimentForm.querySelector('input[name="transport_grpc"]').checked) transports.push("grpc");
  return transports;
}

function getSelectedRealtimeTransports() {
  const transports = [];
  if (realtimeExperimentForm.querySelector('input[name="realtime_transport_http"]').checked) transports.push("http");
  if (realtimeExperimentForm.querySelector('input[name="realtime_transport_ws"]').checked) transports.push("ws");
  if (realtimeExperimentForm.querySelector('input[name="realtime_transport_grpc"]').checked) transports.push("grpc");
  return transports;
}

function getSelectedValidationScenarios() {
  const scenarios = [];
  if (validationExperimentForm.querySelector('input[name="scenario_baseline_valid_dict"]').checked) scenarios.push("baseline_valid_dict");
  if (validationExperimentForm.querySelector('input[name="scenario_structural_validation_valid_set"]').checked) scenarios.push("structural_validation_valid_set");
  if (validationExperimentForm.querySelector('input[name="scenario_full_validation_valid_set"]').checked) scenarios.push("full_validation_valid_set");
  if (validationExperimentForm.querySelector('input[name="scenario_structural_validation_invalid"]').checked) scenarios.push("structural_validation_invalid");
  if (validationExperimentForm.querySelector('input[name="scenario_business_validation_invalid"]').checked) scenarios.push("business_validation_invalid");
  return scenarios;
}

function getSelectedSerializationTransports() {
  const transports = [];
  if (serializationExperimentForm.querySelector('input[name="serialization_transport_http"]').checked) transports.push("http");
  if (serializationExperimentForm.querySelector('input[name="serialization_transport_ws"]').checked) transports.push("ws");
  if (serializationExperimentForm.querySelector('input[name="serialization_transport_grpc"]').checked) transports.push("grpc");
  return transports;
}

function getSelectedSerializationOperations() {
  const operations = [];
  if (serializationExperimentForm.querySelector('input[name="serialization_operation_set_value"]').checked) operations.push("set_value");
  if (serializationExperimentForm.querySelector('input[name="serialization_operation_get_value"]').checked) operations.push("get_value");
  return operations;
}

function buildRequestResponseExperimentPayload(formData) {
  return {
    transports: getSelectedRequestResponseTransports(),
    iterations: Number(formData.get("iterations")),
    http_base_url: formData.get("http_base_url"),
    ws_url: formData.get("ws_url"),
    grpc_address: formData.get("grpc_address"),
    source: formData.get("source"),
    set_value: Number(formData.get("set_value")),
    get_seed_value: Number(formData.get("get_seed_value")),
    set_resource_prefix: formData.get("set_resource_prefix"),
    get_resource_prefix: formData.get("get_resource_prefix"),
  };
}

function buildRealtimeExperimentPayload(formData) {
  return {
    transports: getSelectedRealtimeTransports(),
    iterations: Number(formData.get("iterations")),
    http_base_url: formData.get("http_base_url"),
    ws_changes_url: formData.get("ws_changes_url"),
    ws_process_url: formData.get("ws_process_url"),
    grpc_address: formData.get("grpc_address"),
    resource_prefix: formData.get("resource_prefix"),
    first_value: Number(formData.get("first_value")),
    second_value: Number(formData.get("second_value")),
    third_value: Number(formData.get("third_value")),
  };
}

function buildValidationExperimentPayload(formData) {
  return {
    scenarios: getSelectedValidationScenarios(),
    iterations: Number(formData.get("iterations")),
    source: formData.get("source"),
    valid_resource_id: formData.get("valid_resource_id"),
    readonly_resource_id: formData.get("readonly_resource_id"),
    valid_value: Number(formData.get("valid_value")),
  };
}

function buildSerializationExperimentPayload(formData) {
  return {
    transports: getSelectedSerializationTransports(),
    operations: getSelectedSerializationOperations(),
    iterations: Number(formData.get("iterations")),
    http_base_url: formData.get("http_base_url"),
    ws_url: formData.get("ws_url"),
    grpc_address: formData.get("grpc_address"),
    source: formData.get("source"),
    set_value: Number(formData.get("set_value")),
    get_seed_value: Number(formData.get("get_seed_value")),
    set_resource_prefix: formData.get("set_resource_prefix"),
    get_resource_prefix: formData.get("get_resource_prefix"),
  };
}

async function analyzeSingle(event) {
  event.preventDefault();
  const payload = buildSinglePayload(new FormData(singleForm));

  const response = await fetch("/analyze/single", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    renderSummary([{ label: "Error", value: "Request failed" }]);
    effectiveSettingsBox.innerHTML =
      `<div class="summary-card muted">Could not resolve effective settings.</div>`;
    renderResult(data);
    return;
  }

  renderSummary([
    { label: "Total transmitted bytes", value: String(data.layer_breakdown.total_transmitted_bytes) },
    { label: "Frame count", value: String(data.frame_analysis.frame_count) },
    { label: "Payload efficiency", value: data.efficiency.payload_efficiency_ratio.toFixed(4) },
    { label: "Required bitrate [kbps]", value: data.efficiency.required_bitrate_kbps.toFixed(4) },
  ]);

  renderEffectiveSettings(data);
  renderResult(data);
}

async function analyzeSequence(event) {
  event.preventDefault();
  const payload = buildSequencePayload(new FormData(sequenceForm));

  const response = await fetch("/analyze/sequence", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    renderSummary([{ label: "Error", value: "Request failed" }]);
    effectiveSettingsBox.innerHTML =
      `<div class="summary-card muted">Could not resolve effective settings.</div>`;
    renderResult(data);
    return;
  }

  renderSummary([
    { label: "Aggregated message count", value: String(data.aggregated_message_count) },
    { label: "Total transmitted bytes", value: String(data.total_transmitted_bytes) },
    { label: "Total frame count", value: String(data.total_frame_count) },
    { label: "Payload efficiency", value: data.payload_efficiency_ratio.toFixed(4) },
  ]);

  renderEffectiveSettings(data);
  renderResult(data);
}

async function fetchReport(key) {
  const response = await fetch(`/reports/${key}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch report: ${key}`);
  }
  return await response.json();
}

function fillEnvironmentStatusForm(config) {
  environmentStatusForm.querySelector('input[name="http_health_url"]').value =
    config.http_health_url;
  environmentStatusForm.querySelector('input[name="ws_health_url"]').value =
    config.ws_health_url;
  environmentStatusForm.querySelector('input[name="grpc_address"]').value =
    config.grpc_address;
  environmentStatusForm.querySelector('input[name="timeout_seconds"]').value =
    config.timeout_seconds;
}

function fillRequestResponseExperimentForm(config) {
  requestResponseExperimentForm.querySelector('input[name="iterations"]').value = config.iterations;
  requestResponseExperimentForm.querySelector('input[name="source"]').value = config.source;
  requestResponseExperimentForm.querySelector('input[name="set_value"]').value = config.set_value;
  requestResponseExperimentForm.querySelector('input[name="get_seed_value"]').value = config.get_seed_value;
  requestResponseExperimentForm.querySelector('input[name="http_base_url"]').value = config.http_base_url;
  requestResponseExperimentForm.querySelector('input[name="ws_url"]').value = config.ws_url;
  requestResponseExperimentForm.querySelector('input[name="grpc_address"]').value = config.grpc_address;
  requestResponseExperimentForm.querySelector('input[name="set_resource_prefix"]').value = config.set_resource_prefix;
  requestResponseExperimentForm.querySelector('input[name="get_resource_prefix"]').value = config.get_resource_prefix;

  const transports = new Set(config.transports);
  requestResponseExperimentForm.querySelector('input[name="transport_http"]').checked = transports.has("http");
  requestResponseExperimentForm.querySelector('input[name="transport_ws"]').checked = transports.has("ws");
  requestResponseExperimentForm.querySelector('input[name="transport_grpc"]').checked = transports.has("grpc");
}

function fillRealtimeExperimentForm(config) {
  realtimeExperimentForm.querySelector('input[name="iterations"]').value = config.iterations;
  realtimeExperimentForm.querySelector('input[name="resource_prefix"]').value = config.resource_prefix;
  realtimeExperimentForm.querySelector('input[name="first_value"]').value = config.first_value;
  realtimeExperimentForm.querySelector('input[name="second_value"]').value = config.second_value;
  realtimeExperimentForm.querySelector('input[name="third_value"]').value = config.third_value;
  realtimeExperimentForm.querySelector('input[name="http_base_url"]').value = config.http_base_url;
  realtimeExperimentForm.querySelector('input[name="ws_changes_url"]').value = config.ws_changes_url;
  realtimeExperimentForm.querySelector('input[name="ws_process_url"]').value = config.ws_process_url;
  realtimeExperimentForm.querySelector('input[name="grpc_address"]').value = config.grpc_address;

  const transports = new Set(config.transports);
  realtimeExperimentForm.querySelector('input[name="realtime_transport_http"]').checked = transports.has("http");
  realtimeExperimentForm.querySelector('input[name="realtime_transport_ws"]').checked = transports.has("ws");
  realtimeExperimentForm.querySelector('input[name="realtime_transport_grpc"]').checked = transports.has("grpc");
}

function fillValidationExperimentForm(config) {
  validationExperimentForm.querySelector('input[name="iterations"]').value = config.iterations;
  validationExperimentForm.querySelector('input[name="source"]').value = config.source;
  validationExperimentForm.querySelector('input[name="valid_resource_id"]').value = config.valid_resource_id;
  validationExperimentForm.querySelector('input[name="readonly_resource_id"]').value = config.readonly_resource_id;
  validationExperimentForm.querySelector('input[name="valid_value"]').value = config.valid_value;

  const scenarios = new Set(config.scenarios);
  validationExperimentForm.querySelector('input[name="scenario_baseline_valid_dict"]').checked = scenarios.has("baseline_valid_dict");
  validationExperimentForm.querySelector('input[name="scenario_structural_validation_valid_set"]').checked = scenarios.has("structural_validation_valid_set");
  validationExperimentForm.querySelector('input[name="scenario_full_validation_valid_set"]').checked = scenarios.has("full_validation_valid_set");
  validationExperimentForm.querySelector('input[name="scenario_structural_validation_invalid"]').checked = scenarios.has("structural_validation_invalid");
  validationExperimentForm.querySelector('input[name="scenario_business_validation_invalid"]').checked = scenarios.has("business_validation_invalid");
}

function fillSerializationExperimentForm(config) {
  serializationExperimentForm.querySelector('input[name="iterations"]').value = config.iterations;
  serializationExperimentForm.querySelector('input[name="source"]').value = config.source;
  serializationExperimentForm.querySelector('input[name="set_value"]').value = config.set_value;
  serializationExperimentForm.querySelector('input[name="get_seed_value"]').value = config.get_seed_value;
  serializationExperimentForm.querySelector('input[name="http_base_url"]').value = config.http_base_url;
  serializationExperimentForm.querySelector('input[name="ws_url"]').value = config.ws_url;
  serializationExperimentForm.querySelector('input[name="grpc_address"]').value = config.grpc_address;
  serializationExperimentForm.querySelector('input[name="set_resource_prefix"]').value = config.set_resource_prefix;
  serializationExperimentForm.querySelector('input[name="get_resource_prefix"]').value = config.get_resource_prefix;

  const transports = new Set(config.transports);
  serializationExperimentForm.querySelector('input[name="serialization_transport_http"]').checked = transports.has("http");
  serializationExperimentForm.querySelector('input[name="serialization_transport_ws"]').checked = transports.has("ws");
  serializationExperimentForm.querySelector('input[name="serialization_transport_grpc"]').checked = transports.has("grpc");

  const operations = new Set(config.operations);
  serializationExperimentForm.querySelector('input[name="serialization_operation_set_value"]').checked = operations.has("set_value");
  serializationExperimentForm.querySelector('input[name="serialization_operation_get_value"]').checked = operations.has("get_value");
}

async function loadRequestResponseDefaults() {
  try {
    const response = await fetch("/experiments/request-response/default-config");
    const config = await response.json();
    fillRequestResponseExperimentForm(config);
  } catch (error) {
    requestResponseRunJson.textContent = "Could not load default request-response config.";
  }
}

async function loadRealtimeDefaults() {
  try {
    const response = await fetch("/experiments/realtime/default-config");
    const config = await response.json();
    fillRealtimeExperimentForm(config);
  } catch (error) {
    realtimeRunJson.textContent = "Could not load default realtime config.";
  }
}

async function loadEnvironmentDefaults() {
  try {
    const response = await fetch("/environment/services/default-config");
    const config = await response.json();
    fillEnvironmentStatusForm(config);
  } catch (error) {
    environmentStatusSummary.innerHTML =
      `<div class="summary-card muted">Could not load environment defaults.</div>`;
  }
}

async function loadRecentRuns(event = null) {
  if (event) {
    event.preventDefault();
  }

  recentRunsSummary.innerHTML =
    `<div class="summary-card muted">Loading recent runs...</div>`;
  recentRunsTable.innerHTML = "";

  try {
    const formData = new FormData(recentRunsForm);
    const limit = Number(formData.get("limit"));
    const experimentName = formData.get("experiment_name");

    const response = await fetch(buildRecentRunsUrl(limit, experimentName));
    const data = await response.json();

    if (!response.ok) {
      recentRunsSummary.innerHTML =
        `<div class="summary-card muted">Could not load recent runs.</div>`;
      recentRunsTable.innerHTML =
        `<div class="summary-card muted">${JSON.stringify(data)}</div>`;
      return;
    }

    renderCardGroup(recentRunsSummary, [
      {
        label: "Total matching runs",
        value: String(data.total_count),
      },
      {
        label: "Displayed runs",
        value: String(data.runs.length),
      },
      {
        label: "Filter",
        value: experimentName || "all",
      },
      {
        label: "Limit",
        value: String(limit),
      },
    ]);

    renderTable(
      recentRunsTable,
      [
        { key: "experiment_name", label: "Experiment" },
        { key: "run_id", label: "Run ID" },
        {
          key: "run_label",
          label: "Run label",
          render: (row) => row.run_label || "-",
        },
        { key: "saved_at", label: "Saved at" },
        { key: "file_path", label: "File path" },
        {
          key: "actions",
          label: "Action",
          render: (row) =>
            `<button class="primary-button secondary-button load-run-detail-button" data-run-id="${row.run_id}">Load</button>`,
        },
      ],
      data.runs
    );

    const loadButtons = recentRunsTable.querySelectorAll(".load-run-detail-button");
    loadButtons.forEach((button) => {
      button.addEventListener("click", async () => {
        const runId = button.getAttribute("data-run-id");
        await loadSavedRunDetailById(runId);
      });
    });
  } catch (error) {
    recentRunsSummary.innerHTML =
      `<div class="summary-card muted">Could not load recent runs.</div>`;
    recentRunsTable.innerHTML =
      `<div class="summary-card muted">${error}</div>`;
  }
}

async function loadSavedRunDetailById(runId) {
  if (!runId) {
    savedRunDetailSummary.innerHTML =
      `<div class="summary-card muted">Provide a run ID first.</div>`;
    savedRunDetailJson.textContent = "No saved run loaded.";
    return;
  }

  savedRunDetailSummary.innerHTML =
    `<div class="summary-card muted">Loading saved run...</div>`;
  savedRunDetailJson.textContent = "Loading saved run...";

  try {
    const response = await fetch(`/experiment-runs/${encodeURIComponent(runId)}`);
    const data = await response.json();

    if (!response.ok) {
      savedRunDetailSummary.innerHTML =
        `<div class="summary-card muted">Could not load saved run.</div>`;
      savedRunDetailJson.textContent = JSON.stringify(data, null, 2);
      return;
    }

    renderCardGroup(savedRunDetailSummary, [
      { label: "Experiment", value: data.metadata.experiment_name },
      { label: "Run ID", value: data.metadata.run_id },
      { label: "Run label", value: data.metadata.run_label || "-" },
      { label: "Saved at", value: data.metadata.saved_at },
      { label: "File path", value: data.metadata.file_path },
    ]);

    savedRunDetailJson.textContent = JSON.stringify(data, null, 2);
    savedRunDetailForm.querySelector('input[name="run_id"]').value =
      data.metadata.run_id;
  } catch (error) {
    savedRunDetailSummary.innerHTML =
      `<div class="summary-card muted">Could not load saved run.</div>`;
    savedRunDetailJson.textContent = String(error);
  }
}

async function loadSavedRunDetail(event) {
  event.preventDefault();

  const runId = savedRunDetailForm
    .querySelector('input[name="run_id"]')
    .value.trim();

  await loadSavedRunDetailById(runId);
}

async function refreshEnvironmentStatus(event = null) {
  if (event) {
    event.preventDefault();
  }

  environmentStatusSummary.innerHTML =
    `<div class="summary-card muted">Checking environment...</div>`;
  environmentStatusTable.innerHTML = "";

  const payload = buildEnvironmentStatusPayload(
    new FormData(environmentStatusForm)
  );

  try {
    const response = await fetch("/environment/services/status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      environmentStatusSummary.innerHTML =
        `<div class="summary-card muted">Environment status check failed.</div>`;
      environmentStatusTable.innerHTML =
        `<div class="summary-card muted">${JSON.stringify(data)}</div>`;
      return;
    }

    const availableCount = data.services.filter((service) => service.available).length;

    renderCardGroup(environmentStatusSummary, [
      {
        label: "Overall status",
        value: data.all_available ? "all available" : "degraded",
      },
      {
        label: "Available services",
        value: `${availableCount}/${data.services.length}`,
      },
      {
        label: "Timeout [s]",
        value: String(data.config.timeout_seconds),
      },
      {
        label: "Checked at",
        value: data.checked_at,
      },
    ]);

    renderTable(
      environmentStatusTable,
      [
        { key: "service_name", label: "Service" },
        {
          key: "available",
          label: "Available",
          render: (row) =>
            row.available
              ? `<span class="report-ok">yes</span>`
              : `<span class="report-missing">no</span>`,
        },
        {
          key: "response_time_ms",
          label: "Response time [ms]",
          render: (row) =>
            row.response_time_ms === null
              ? "-"
              : Number(row.response_time_ms).toFixed(3),
        },
        { key: "detail", label: "Detail" },
      ],
      data.services
    );
  } catch (error) {
    environmentStatusSummary.innerHTML =
      `<div class="summary-card muted">Could not refresh environment status.</div>`;
    environmentStatusTable.innerHTML =
      `<div class="summary-card muted">${error}</div>`;
  }
}

async function loadValidationDefaults() {
  try {
    const response = await fetch("/experiments/validation/default-config");
    const config = await response.json();
    fillValidationExperimentForm(config);
  } catch (error) {
    validationRunJson.textContent = "Could not load default validation config.";
  }
}

async function loadSerializationDefaults() {
  try {
    const response = await fetch("/experiments/serialization/default-config");
    const config = await response.json();
    fillSerializationExperimentForm(config);
  } catch (error) {
    serializationRunJson.textContent = "Could not load default serialization config.";
  }
}

async function runRequestResponseExperiment(event) {
  event.preventDefault();

  const formData = new FormData(requestResponseExperimentForm);
  const payload = buildRequestResponseExperimentPayload(formData);
  const persistence = getPersistenceOptions(
    requestResponseExperimentForm,
    "request_response_save_result",
    "request_response_run_label"
  );

  if (!payload.transports.length) {
    requestResponseRunSummary.innerHTML =
      `<div class="summary-card muted">Select at least one transport.</div>`;
    return;
  }

  requestResponseRunSummary.innerHTML = `<div class="summary-card muted">Running experiment...</div>`;
  requestResponseRunJson.textContent = "Running experiment...";

  const response = await fetch(
    buildExperimentRunUrl(
      "/experiments/request-response/run",
      persistence.saveResult,
      persistence.runLabel
    ),
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    requestResponseRunSummary.innerHTML = `<div class="summary-card muted">Experiment failed.</div>`;
    requestResponseRunJson.textContent = JSON.stringify(data, null, 2);
    requestResponseRunTable.innerHTML = "";
    return;
  }

  const setBest = bestRowBy(
    data.measurements.map((m) => ({ transport: m.transport, avg_ms: m.set_value.summary.avg_ms })),
    "avg_ms"
  );

  const getBest = bestRowBy(
    data.measurements.map((m) => ({ transport: m.transport, avg_ms: m.get_value.summary.avg_ms })),
    "avg_ms"
  );

  const requestResponseCards = [
    { label: "Iterations", value: String(data.iterations) },
    { label: "Transports run", value: String(data.transports.length) },
    { label: "Best set_value", value: `${setBest.transport} (${setBest.avg_ms.toFixed(3)} ms)` },
    { label: "Best get_value", value: `${getBest.transport} (${getBest.avg_ms.toFixed(3)} ms)` },
  ];

  if (data.saved_result) {
    requestResponseCards.push({
      label: "Saved run",
      value: data.saved_result.run_id,
    });
  }

  renderCardGroup(requestResponseRunSummary, requestResponseCards);

  const experimentRows = data.measurements.flatMap((measurement) => [
    {
      transport: measurement.transport,
      operation: "set_value",
      avg_ms: measurement.set_value.summary.avg_ms,
      median_ms: measurement.set_value.summary.median_ms,
      min_ms: measurement.set_value.summary.min_ms,
      max_ms: measurement.set_value.summary.max_ms,
    },
    {
      transport: measurement.transport,
      operation: "get_value",
      avg_ms: measurement.get_value.summary.avg_ms,
      median_ms: measurement.get_value.summary.median_ms,
      min_ms: measurement.get_value.summary.min_ms,
      max_ms: measurement.get_value.summary.max_ms,
    },
  ]);

  renderTable(
    requestResponseRunTable,
    [
      { key: "transport", label: "Transport" },
      { key: "operation", label: "Operation" },
      { key: "avg_ms", label: "Avg [ms]", render: (row) => row.avg_ms.toFixed(3) },
      { key: "median_ms", label: "Median [ms]", render: (row) => row.median_ms.toFixed(3) },
      { key: "min_ms", label: "Min [ms]", render: (row) => row.min_ms.toFixed(3) },
      { key: "max_ms", label: "Max [ms]", render: (row) => row.max_ms.toFixed(3) },
    ],
    experimentRows
  );

  requestResponseRunJson.textContent = JSON.stringify(data, null, 2);

  if (data.saved_result) {
    await loadRecentRuns();
    await loadSavedRunDetailById(data.saved_result.run_id);
  }
}

async function runRealtimeExperiment(event) {
  event.preventDefault();

  const formData = new FormData(realtimeExperimentForm);
  const payload = buildRealtimeExperimentPayload(formData);
  const persistence = getPersistenceOptions(
    realtimeExperimentForm,
    "realtime_save_result",
    "realtime_run_label"
  );

  if (!payload.transports.length) {
    realtimeRunSummary.innerHTML =
      `<div class="summary-card muted">Select at least one transport.</div>`;
    return;
  }

  realtimeRunSummary.innerHTML = `<div class="summary-card muted">Running experiment...</div>`;
  realtimeRunJson.textContent = "Running experiment...";

  const response = await fetch(
    buildExperimentRunUrl(
      "/experiments/realtime/run",
      persistence.saveResult,
      persistence.runLabel
    ),
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    realtimeRunSummary.innerHTML = `<div class="summary-card muted">Experiment failed.</div>`;
    realtimeRunJson.textContent = JSON.stringify(data, null, 2);
    realtimeRunTable.innerHTML = "";
    return;
  }

  const bestNonEmpty = bestRowBy(
    data.measurements.filter((m) => m.scenario === "non_empty_fetch"),
    "summary.avg_ms"
  );

  const bestEmpty = bestRowBy(
    data.measurements.filter((m) => m.scenario === "empty_fetch"),
    "summary.avg_ms"
  );

  const realtimeCards = [
    { label: "Iterations", value: String(data.iterations) },
    { label: "Transports run", value: String(data.transports.length) },
    { label: "Best non_empty_fetch", value: `${bestNonEmpty.transport} (${bestNonEmpty.summary.avg_ms.toFixed(3)} ms)` },
    { label: "Best empty_fetch", value: `${bestEmpty.transport} (${bestEmpty.summary.avg_ms.toFixed(3)} ms)` },
  ];

  if (data.saved_result) {
    realtimeCards.push({
      label: "Saved run",
      value: data.saved_result.run_id,
    });
  }

  renderCardGroup(realtimeRunSummary, realtimeCards);

  renderTable(
    realtimeRunTable,
    [
      { key: "transport", label: "Transport" },
      { key: "scenario", label: "Scenario" },
      { key: "summary.avg_ms", label: "Avg [ms]", render: (row) => row.summary.avg_ms.toFixed(3) },
      { key: "summary.median_ms", label: "Median [ms]", render: (row) => row.summary.median_ms.toFixed(3) },
      { key: "summary.min_ms", label: "Min [ms]", render: (row) => row.summary.min_ms.toFixed(3) },
      { key: "summary.max_ms", label: "Max [ms]", render: (row) => row.summary.max_ms.toFixed(3) },
      { key: "expected_event_count", label: "Event count", render: (row) => String(row.expected_event_count) },
    ],
    data.measurements
  );

  realtimeRunJson.textContent = JSON.stringify(data, null, 2);

  if (data.saved_result) {
    await loadRecentRuns();
    await loadSavedRunDetailById(data.saved_result.run_id);
  }
}

async function runValidationExperiment(event) {
  event.preventDefault();

  const formData = new FormData(validationExperimentForm);
  const payload = buildValidationExperimentPayload(formData);
  const persistence = getPersistenceOptions(
    validationExperimentForm,
    "validation_save_result",
    "validation_run_label"
  );

  if (!payload.scenarios.length) {
    validationRunSummary.innerHTML =
      `<div class="summary-card muted">Select at least one scenario.</div>`;
    return;
  }

  validationRunSummary.innerHTML = `<div class="summary-card muted">Running experiment...</div>`;
  validationRunJson.textContent = "Running experiment...";

  const response = await fetch(
    buildExperimentRunUrl(
      "/experiments/validation/run",
      persistence.saveResult,
      persistence.runLabel
    ),
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    validationRunSummary.innerHTML = `<div class="summary-card muted">Experiment failed.</div>`;
    validationRunJson.textContent = JSON.stringify(data, null, 2);
    validationRunTable.innerHTML = "";
    return;
  }

  const fastest = bestRowBy(data.measurements, "summary.avg_us");
  const slowest = worstRowBy(data.measurements, "summary.avg_us");

  const validationCards = [
    { label: "Iterations", value: String(data.iterations) },
    { label: "Scenarios run", value: String(data.scenarios.length) },
    { label: "Fastest scenario", value: `${fastest.scenario} (${fastest.summary.avg_us.toFixed(3)} us)` },
    { label: "Slowest scenario", value: `${slowest.scenario} (${slowest.summary.avg_us.toFixed(3)} us)` },
  ];

  if (data.saved_result) {
    validationCards.push({
      label: "Saved run",
      value: data.saved_result.run_id,
    });
  }

  renderCardGroup(validationRunSummary, validationCards);

  renderTable(
    validationRunTable,
    [
      { key: "scenario", label: "Scenario" },
      { key: "expected_outcome", label: "Expected outcome" },
      { key: "summary.avg_us", label: "Avg [us]", render: (row) => row.summary.avg_us.toFixed(3) },
      { key: "summary.median_us", label: "Median [us]", render: (row) => row.summary.median_us.toFixed(3) },
      { key: "summary.min_us", label: "Min [us]", render: (row) => row.summary.min_us.toFixed(3) },
      { key: "summary.max_us", label: "Max [us]", render: (row) => row.summary.max_us.toFixed(3) },
    ],
    data.measurements
  );

  validationRunJson.textContent = JSON.stringify(data, null, 2);

  if (data.saved_result) {
    await loadRecentRuns();
    await loadSavedRunDetailById(data.saved_result.run_id);
  }
}

async function runSerializationExperiment(event) {
  event.preventDefault();

  const formData = new FormData(serializationExperimentForm);
  const payload = buildSerializationExperimentPayload(formData);
  const persistence = getPersistenceOptions(
    serializationExperimentForm,
    "serialization_save_result",
    "serialization_run_label"
  );

  if (!payload.transports.length) {
    serializationRunSummary.innerHTML =
      `<div class="summary-card muted">Select at least one transport.</div>`;
    return;
  }

  if (!payload.operations.length) {
    serializationRunSummary.innerHTML =
      `<div class="summary-card muted">Select at least one operation.</div>`;
    return;
  }

  serializationRunSummary.innerHTML = `<div class="summary-card muted">Running experiment...</div>`;
  serializationRunJson.textContent = "Running experiment...";

  const response = await fetch(
    buildExperimentRunUrl(
      "/experiments/serialization/run",
      persistence.saveResult,
      persistence.runLabel
    ),
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    serializationRunSummary.innerHTML = `<div class="summary-card muted">Experiment failed.</div>`;
    serializationRunJson.textContent = JSON.stringify(data, null, 2);
    serializationRunTable.innerHTML = "";
    return;
  }

  const smallestRequest = bestRowBy(data.measurements, "request_size_bytes");
  const smallestResponse = bestRowBy(data.measurements, "response_size_bytes");
  const fastestSerialize = bestRowBy(data.measurements, "request_serialize_summary.avg_us");
  const fastestDeserialize = bestRowBy(data.measurements, "response_deserialize_summary.avg_us");

  const serializationCards = [
    { label: "Iterations", value: String(data.iterations) },
    { label: "Measurements", value: String(data.measurements.length) },
    { label: "Smallest request", value: `${smallestRequest.transport}/${smallestRequest.operation} (${smallestRequest.request_size_bytes} B)` },
    { label: "Fastest request serialize", value: `${fastestSerialize.transport}/${fastestSerialize.operation} (${fastestSerialize.request_serialize_summary.avg_us.toFixed(3)} us)` },
    { label: "Smallest response", value: `${smallestResponse.transport}/${smallestResponse.operation} (${smallestResponse.response_size_bytes} B)` },
    { label: "Fastest response deserialize", value: `${fastestDeserialize.transport}/${fastestDeserialize.operation} (${fastestDeserialize.response_deserialize_summary.avg_us.toFixed(3)} us)` },
  ];

  if (data.saved_result) {
    serializationCards.push({
      label: "Saved run",
      value: data.saved_result.run_id,
    });
  }

  renderCardGroup(serializationRunSummary, serializationCards);

  renderTable(
    serializationRunTable,
    [
      { key: "transport", label: "Transport" },
      { key: "operation", label: "Operation" },
      { key: "encoding", label: "Encoding" },
      { key: "request_size_bytes", label: "Request [B]" },
      { key: "response_size_bytes", label: "Response [B]" },
      { key: "request_serialize_summary.avg_us", label: "Req serialize [us]", render: (row) => row.request_serialize_summary.avg_us.toFixed(3) },
      { key: "request_deserialize_summary.avg_us", label: "Req deserialize [us]", render: (row) => row.request_deserialize_summary.avg_us.toFixed(3) },
      { key: "response_serialize_summary.avg_us", label: "Resp serialize [us]", render: (row) => row.response_serialize_summary.avg_us.toFixed(3) },
      { key: "response_deserialize_summary.avg_us", label: "Resp deserialize [us]", render: (row) => row.response_deserialize_summary.avg_us.toFixed(3) },
    ],
    data.measurements
  );

  serializationRunJson.textContent = JSON.stringify(data, null, 2);

  if (data.saved_result) {
    await loadRecentRuns();
    await loadSavedRunDetailById(data.saved_result.run_id);
  }
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
      { label: "Best set_value transport", value: `${bestSet.transport} (${bestSet.avg_ms.toFixed(3)} ms)` },
      { label: "Best get_value transport", value: `${bestGet.transport} (${bestGet.avg_ms.toFixed(3)} ms)` },
      { label: "Best realtime scenario result", value: `${bestRealtime.transport} (${bestRealtime.avg_ms.toFixed(3)} ms)` },
      { label: "Smallest request payload", value: `${smallestPayload.transport}/${smallestPayload.operation}` },
    ]);

    renderCardGroup(transportSummaryCards, [
      { label: "set_value best avg [ms]", value: Math.min(...requestResponse.filter((r) => r.operation === "set_value").map((r) => r.avg_ms)).toFixed(3) },
      { label: "get_value best avg [ms]", value: Math.min(...requestResponse.filter((r) => r.operation === "get_value").map((r) => r.avg_ms)).toFixed(3) },
      { label: "Rows loaded", value: String(requestResponse.length) },
      { label: "Transports", value: Array.from(new Set(requestResponse.map((r) => r.transport))).join(", ") },
    ]);

    renderCardGroup(realtimeSummaryCards, [
      { label: "non_empty_fetch best avg [ms]", value: Math.min(...realtime.filter((r) => r.scenario === "non_empty_fetch").map((r) => r.avg_ms)).toFixed(3) },
      { label: "empty_fetch best avg [ms]", value: Math.min(...realtime.filter((r) => r.scenario === "empty_fetch").map((r) => r.avg_ms)).toFixed(3) },
      { label: "Rows loaded", value: String(realtime.length) },
      { label: "Expected event counts", value: Array.from(new Set(realtime.map((r) => r.expected_event_count))).join(", ") },
    ]);

    renderCardGroup(validationSummaryCards, [
      { label: "Fastest validation avg [us]", value: fastestValidation.avg_us.toFixed(3) },
      { label: "Slowest validation avg [us]", value: slowestValidation.avg_us.toFixed(3) },
      { label: "Scenarios loaded", value: String(validation.length) },
      { label: "Fastest scenario", value: fastestValidation.scenario },
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

requestResponseExperimentForm.addEventListener("submit", runRequestResponseExperiment);
loadRequestResponseDefaultsButton.addEventListener("click", loadRequestResponseDefaults);

environmentStatusForm.addEventListener("submit", refreshEnvironmentStatus);
loadEnvironmentDefaultsButton.addEventListener("click", loadEnvironmentDefaults);

recentRunsForm.addEventListener("submit", loadRecentRuns);
savedRunDetailForm.addEventListener("submit", loadSavedRunDetail);

realtimeExperimentForm.addEventListener("submit", runRealtimeExperiment);
loadRealtimeDefaultsButton.addEventListener("click", loadRealtimeDefaults);

validationExperimentForm.addEventListener("submit", runValidationExperiment);
loadValidationDefaultsButton.addEventListener("click", loadValidationDefaults);

serializationExperimentForm.addEventListener("submit", runSerializationExperiment);
loadSerializationDefaultsButton.addEventListener("click", loadSerializationDefaults);

setMode("single");
setMainView("overhead");
checkHealth();
loadPresets();
loadRequestResponseDefaults();
loadRealtimeDefaults();
loadValidationDefaults();
loadSerializationDefaults();
loadEnvironmentDefaults();