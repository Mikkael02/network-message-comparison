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
const transmissionVisualization = document.getElementById("transmission-visualization");
const frameLayerVisualization = document.getElementById("frame-layer-visualization");

const navOverhead = document.getElementById("nav-overhead");
const navExperiments = document.getElementById("nav-experiments");
const navEnvironment = document.getElementById("nav-environment");
const navHistory = document.getElementById("nav-history");

const viewOverhead = document.getElementById("view-overhead");
const viewExperiments = document.getElementById("view-experiments");
const viewEnvironment = document.getElementById("view-environment");
const viewHistory = document.getElementById("view-history");
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
const experimentTabRequestResponse = document.getElementById("experiment-tab-request-response");
const experimentTabRealtime = document.getElementById("experiment-tab-realtime");
const experimentTabValidation = document.getElementById("experiment-tab-validation");
const experimentTabSerialization = document.getElementById("experiment-tab-serialization");

const experimentPanelRequestResponse = document.getElementById("experiment-panel-request-response");
const experimentPanelRealtime = document.getElementById("experiment-panel-realtime");
const experimentPanelValidation = document.getElementById("experiment-panel-validation");
const experimentPanelSerialization = document.getElementById("experiment-panel-serialization");

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
const compareNagleButton = document.getElementById("compare-nagle-button");
const nagleComparisonSummary = document.getElementById("nagle-comparison-summary");
const nagleComparisonTable = document.getElementById("nagle-comparison-table");
const nagleComparisonChart = document.getElementById("nagle-comparison-chart");
const nagleComparisonSummaryPanel = document.getElementById("nagle-comparison-summary-panel");
const nagleComparisonTablePanel = document.getElementById("nagle-comparison-table-panel");
const nagleComparisonChartPanel = document.getElementById("nagle-comparison-chart-panel");
const compareProfilesButton = document.getElementById("compare-profiles-button");
const profileComparisonSummary = document.getElementById("profile-comparison-summary");
const profileComparisonTable = document.getElementById("profile-comparison-table");
const profileComparisonChart = document.getElementById("profile-comparison-chart");
const profileComparisonSummaryPanel = document.getElementById("profile-comparison-summary-panel");
const profileComparisonTablePanel = document.getElementById("profile-comparison-table-panel");
const profileComparisonChartPanel = document.getElementById("profile-comparison-chart-panel");

function setMode(mode) {
  const singleActive = mode === "single";
  singleTab.classList.toggle("active", singleActive);
  sequenceTab.classList.toggle("active", !singleActive);
  singleFormSection.classList.toggle("hidden", !singleActive);
  sequenceFormSection.classList.toggle("hidden", singleActive);

  const hideSequenceComparisons = singleActive;
  [
    nagleComparisonSummaryPanel,
    nagleComparisonTablePanel,
    nagleComparisonChartPanel,
    profileComparisonSummaryPanel,
    profileComparisonTablePanel,
    profileComparisonChartPanel,
  ].forEach((element) => {
    if (element) {
      element.classList.toggle("hidden", hideSequenceComparisons);
    }
  });
}

function setMainView(view) {
  const overheadActive = view === "overhead";
  const experimentsActive = view === "experiments";
  const environmentActive = view === "environment";
  const historyActive = view === "history";

  navOverhead.classList.toggle("active", overheadActive);
  navExperiments.classList.toggle("active", experimentsActive);
  navEnvironment.classList.toggle("active", environmentActive);
  navHistory.classList.toggle("active", historyActive);

  viewOverhead.classList.toggle("hidden", !overheadActive);
  viewExperiments.classList.toggle("hidden", !experimentsActive);
  viewEnvironment.classList.toggle("hidden", !environmentActive);
  viewHistory.classList.toggle("hidden", !historyActive);

  if (overheadActive) {
    pageTitle.textContent = "Model transmisji i narzutu";
    pageDescription.textContent =
      "Analiza narzutu transmisji dla pojedynczej wiadomości i sekwencji wiadomości w modelu Ethernet II + IPv4 + TCP.";
  } else if (experimentsActive) {
    pageTitle.textContent = "Eksperymenty";
    pageDescription.textContent =
      "Uruchamianie eksperymentów request-response, realtime, walidacji i serializacji.";
  } else if (environmentActive) {
    pageTitle.textContent = "Środowisko badawcze";
    pageDescription.textContent =
      "Sprawdzanie dostępności usług HTTP, WebSocket i gRPC oraz przygotowanie środowiska do badań.";
  } else {
    pageTitle.textContent = "Historia uruchomień";
    pageDescription.textContent =
      "Przegląd zapisanych uruchomień eksperymentów i podgląd szczegółów wybranego runu.";
  }
}



function setExperimentTab(tabName) {
  const isRequestResponse = tabName === "request_response";
  const isRealtime = tabName === "realtime";
  const isValidation = tabName === "validation";
  const isSerialization = tabName === "serialization";

  if (experimentTabRequestResponse) {
    experimentTabRequestResponse.classList.toggle("active", isRequestResponse);
  }
  if (experimentTabRealtime) {
    experimentTabRealtime.classList.toggle("active", isRealtime);
  }
  if (experimentTabValidation) {
    experimentTabValidation.classList.toggle("active", isValidation);
  }
  if (experimentTabSerialization) {
    experimentTabSerialization.classList.toggle("active", isSerialization);
  }

  if (experimentPanelRequestResponse) {
    experimentPanelRequestResponse.classList.toggle("hidden", !isRequestResponse);
  }
  if (experimentPanelRealtime) {
    experimentPanelRealtime.classList.toggle("hidden", !isRealtime);
  }
  if (experimentPanelValidation) {
    experimentPanelValidation.classList.toggle("hidden", !isValidation);
  }
  if (experimentPanelSerialization) {
    experimentPanelSerialization.classList.toggle("hidden", !isSerialization);
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
    container.innerHTML = `<div class="summary-card muted">Brak danych.</div>`;
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

function renderSimpleComparisonBars(container, rows) {
  const metrics = [
    {
      key: "total_transmitted_bytes",
      label: "Przesłane bajty",
      formatter: (value) => `${value} B`,
    },
    {
      key: "total_frame_count",
      label: "Liczba ramek",
      formatter: (value) => String(value),
    },
    {
      key: "aggregated_message_count",
      label: "Zagregowane wiadomości",
      formatter: (value) => String(value),
    },
    {
      key: "payload_efficiency_ratio",
      label: "Efektywność payloadu",
      formatter: (value) => Number(value).toFixed(4),
    },
  ];

  const chartSections = metrics.map((metric) => {
    const maxValue = Math.max(...rows.map((row) => row[metric.key])) || 1;

    const bars = rows
      .map((row) => {
        const percent = (row[metric.key] / maxValue) * 100;
        return `
          <div style="margin-bottom: 10px;">
            <div style="display:flex; justify-content:space-between; gap:12px; font-size: 14px;">
              <span>${row.variant_label}</span>
              <span>${metric.formatter(row[metric.key])}</span>
            </div>
            <div style="width:100%; background:#e5e7eb; border-radius:10px; overflow:hidden; height:14px; margin-top:4px;">
              <div style="width:${percent}%; height:14px; background:#9ca3af;"></div>
            </div>
          </div>
        `;
      })
      .join("");

    return `
      <div class="summary-card" style="min-width: 260px;">
        <span class="label">${metric.label}</span>
        <div style="margin-top:10px;">
          ${bars}
        </div>
      </div>
    `;
  });

  container.innerHTML = `
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px;">
      ${chartSections.join("")}
    </div>
  `;
}


function renderLayerStack(title, layers) {
  const total = layers.reduce((sum, layer) => sum + layer.value, 0) || 1;

  const segments = layers
    .map((layer) => {
      const percent = Math.max(6, (layer.value / total) * 100);
      return `
        <div style="margin-bottom:12px;">
          <div style="display:flex; justify-content:space-between; gap:12px; font-size:14px;">
            <span>${layer.label}</span>
            <span>${layer.value} B (${((layer.value / total) * 100).toFixed(1)}%)</span>
          </div>
          <div style="width:100%; background:#0f172a; border-radius:10px; overflow:hidden; height:18px; margin-top:4px;">
            <div style="width:${percent}%; height:18px; background:${layer.color};"></div>
          </div>
        </div>
      `;
    })
    .join("");

  return `
    <div class="summary-card">
      <span class="label">${title}</span>
      <div style="margin-top:10px;">
        ${segments}
      </div>
      <div style="margin-top:10px; font-size:14px;">
        <strong>Łącznie:</strong> ${total} B
      </div>
    </div>
  `;
}


function renderLabeledBlocks(title, values, unit = "B") {
  if (!values || !values.length) {
    return `
      <div class="summary-card">
        <span class="label">${title}</span>
        <div class="muted">Brak danych</div>
      </div>
    `;
  }

  const maxValue = Math.max(...values, 1);

  const blocks = values
    .map((value, index) => {
      const percent = Math.max(8, (value / maxValue) * 100);
      return `
        <div style="margin-bottom:10px;">
          <div style="display:flex; justify-content:space-between; gap:12px; font-size:14px;">
            <span>${title} ${index + 1}</span>
            <span>${value} ${unit}</span>
          </div>
          <div style="width:100%; background:#1e293b; border-radius:10px; overflow:hidden; height:16px; margin-top:4px;">
            <div style="width:${percent}%; height:16px; background:#38bdf8;"></div>
          </div>
        </div>
      `;
    })
    .join("");

  return `
    <div class="summary-card">
      <span class="label">${title}</span>
      <div style="margin-top:10px;">
        ${blocks}
      </div>
    </div>
  `;
}

function renderSingleTransmissionVisualization(data) {
  const serializedPayload =
    data.serialized_payload_size_bytes ??
    data.layer_breakdown?.serialized_payload_size_bytes ??
    data.input_summary?.payload_size_bytes ??
    "-";
  const bytesPerFrame =
    data.frame_analysis?.bytes_per_frame ||
    data.frame_analysis?.frame_sizes_bytes ||
    [];
  const mtu = data.effective_settings?.mtu_bytes ?? "-";
  const payloadInput =
    data.input_summary?.payload_size_bytes ??
    data.payload_size_bytes ??
    "-";

  transmissionVisualization.innerHTML = `
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:16px;">
      <div class="summary-card">
        <span class="label">Poziom aplikacji</span>
        <div style="margin-top:10px;">
          <div><strong>Payload wejściowy:</strong> ${payloadInput} B</div>
          <div><strong>Payload po serializacji:</strong> ${serializedPayload} B</div>
          <div><strong>Narzut aplikacyjny:</strong> ${data.effective_settings?.application_header_overhead_bytes ?? "-"} B</div>
        </div>
      </div>

      <div class="summary-card">
        <span class="label">Segmentacja</span>
        <div style="margin-top:10px;">
          <div><strong>MTU:</strong> ${mtu} B</div>
          <div><strong>Liczba segmentów:</strong> ${data.frame_analysis?.segment_count ?? "-"}</div>
          <div><strong>Liczba ramek:</strong> ${data.frame_analysis?.frame_count ?? "-"}</div>
          <div><strong>Fragmentacja:</strong> ${data.frame_analysis?.fragmentation_occurred ? "tak" : "nie"}</div>
        </div>
      </div>

      ${renderLabeledBlocks("Ramka", bytesPerFrame)}
    </div>
  `;
}

function renderSequenceTransmissionVisualization(data) {
  const payloads = data.input_summary?.payload_sizes_bytes || [];
  const aggregated = data.aggregated_payload_sizes_bytes || [];
  const mtu = data.effective_settings?.mtu_bytes ?? "-";

  transmissionVisualization.innerHTML = `
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:16px;">
      ${renderLabeledBlocks("Payload wejściowy", payloads)}
      ${renderLabeledBlocks("Grupa po agregacji", aggregated)}

      <div class="summary-card">
        <span class="label">Podsumowanie transmisji</span>
        <div style="margin-top:10px;">
          <div><strong>Tryb agregacji:</strong> ${data.effective_aggregation_mode}</div>
          <div><strong>Nagle:</strong> ${data.nagle_enabled ? "włączony" : "wyłączony"}</div>
          <div><strong>MTU:</strong> ${mtu} B</div>
          <div><strong>Liczba ramek:</strong> ${data.total_frame_count}</div>
          <div><strong>Łącznie przesłane:</strong> ${data.total_transmitted_bytes} B</div>
        </div>
      </div>
    </div>
  `;
}


function renderSingleFrameLayerVisualization(data) {
  const settings = data.effective_settings || {};
  const payloadBytes =
    data.serialized_payload_size_bytes ??
    data.layer_breakdown?.serialized_payload_size_bytes ??
    data.input_summary?.payload_size_bytes ??
    0;
  const appHeaderBytes = settings.application_header_overhead_bytes ?? 0;
  const tcpBytes = settings.tcp_header_size_bytes ?? 0;
  const ipv4Bytes = settings.ipv4_header_size_bytes ?? 0;
  const ethernetHeaderBytes = settings.ethernet_header_size_bytes ?? 0;
  const ethernetTrailerBytes = settings.ethernet_trailer_size_bytes ?? 0;

  frameLayerVisualization.innerHTML = `
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:16px;">
      ${renderLayerStack("Budowa wiadomości i ramki", [
        { label: "Payload", value: payloadBytes, color: "#38bdf8" },
        { label: "Nagłówek aplikacyjny", value: appHeaderBytes, color: "#818cf8" },
        { label: "TCP", value: tcpBytes, color: "#22c55e" },
        { label: "IPv4", value: ipv4Bytes, color: "#f59e0b" },
        { label: "Ethernet header", value: ethernetHeaderBytes, color: "#ef4444" },
        { label: "Ethernet trailer", value: ethernetTrailerBytes, color: "#ec4899" },
      ])}

      <div class="summary-card">
        <span class="label">Interpretacja warstw</span>
        <div style="margin-top:10px; font-size:14px; line-height:1.6;">
          <div><strong>Payload po serializacji:</strong> ${payloadBytes} B</div>
          <div><strong>Warstwa aplikacyjna:</strong> ${appHeaderBytes} B</div>
          <div><strong>Warstwa transportowa TCP:</strong> ${tcpBytes} B</div>
          <div><strong>Warstwa sieciowa IPv4:</strong> ${ipv4Bytes} B</div>
          <div><strong>Warstwa łącza Ethernet:</strong> ${ethernetHeaderBytes + ethernetTrailerBytes} B</div>
          <div><strong>Łączny narzut nie-payload:</strong> ${
            appHeaderBytes + tcpBytes + ipv4Bytes + ethernetHeaderBytes + ethernetTrailerBytes
          } B</div>
        </div>
      </div>
    </div>
  `;
}

function renderSequenceFrameLayerVisualization(data) {
  const settings = data.effective_settings || {};
  const representativePayload =
    (data.aggregated_payload_sizes_bytes && data.aggregated_payload_sizes_bytes[0]) || 0;

  const appHeaderBytes = settings.application_header_overhead_bytes ?? 0;
  const tcpBytes = settings.tcp_header_size_bytes ?? 0;
  const ipv4Bytes = settings.ipv4_header_size_bytes ?? 0;
  const ethernetHeaderBytes = settings.ethernet_header_size_bytes ?? 0;
  const ethernetTrailerBytes = settings.ethernet_trailer_size_bytes ?? 0;

  const perGroupTotal =
    representativePayload +
    appHeaderBytes +
    tcpBytes +
    ipv4Bytes +
    ethernetHeaderBytes +
    ethernetTrailerBytes;

  frameLayerVisualization.innerHTML = `
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:16px;">
      ${renderLayerStack("Reprezentatywna grupa po agregacji", [
        { label: "Payload / grupa", value: representativePayload, color: "#38bdf8" },
        { label: "Nagłówek aplikacyjny", value: appHeaderBytes, color: "#818cf8" },
        { label: "TCP", value: tcpBytes, color: "#22c55e" },
        { label: "IPv4", value: ipv4Bytes, color: "#f59e0b" },
        { label: "Ethernet header", value: ethernetHeaderBytes, color: "#ef4444" },
        { label: "Ethernet trailer", value: ethernetTrailerBytes, color: "#ec4899" },
      ])}

      <div class="summary-card">
        <span class="label">Podsumowanie sekwencji</span>
        <div style="margin-top:10px; font-size:14px; line-height:1.6;">
          <div><strong>Tryb agregacji:</strong> ${data.effective_aggregation_mode}</div>
          <div><strong>Nagle:</strong> ${data.nagle_enabled ? "włączony" : "wyłączony"}</div>
          <div><strong>Liczba grup:</strong> ${data.aggregated_message_count}</div>
          <div><strong>Przykładowa grupa:</strong> ${representativePayload} B</div>
          <div><strong>Szacowany rozmiar grupy z narzutem:</strong> ${perGroupTotal} B</div>
          <div><strong>Łącznie przesłane:</strong> ${data.total_transmitted_bytes} B</div>
        </div>
      </div>
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
      apiStatus.textContent = "API gotowe";
      apiStatus.classList.add("ok");
      apiStatus.classList.remove("error");
    } else {
      throw new Error("Unexpected health response");
    }
  } catch (error) {
    apiStatus.textContent = "API niedostępne";
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
          `<li>${key}: MTU ${value.mtu_bytes}B, IPv4 ${value.ipv4_header_size_bytes}B, TCP ${value.tcp_header_size_bytes}B</li>`
      )
      .join("");

    presetsContent.innerHTML = `
      <strong>Warstwy</strong>
      <ul class="preset-list">
        <li>Ethernet: ${data.layer_presets.ethernet.header_size_bytes}B header + ${data.layer_presets.ethernet.trailer_size_bytes}B trailer</li>
        <li>IPv4: ${data.layer_presets.ipv4.header_size_bytes}B header</li>
        <li>TCP: ${data.layer_presets.tcp.header_size_bytes}B header</li>
      </ul>
      <strong>Protokoły</strong>
      <ul class="preset-list">
        <li>HTTP: ${data.protocol_presets.http.default_header_overhead_bytes}B</li>
        <li>WebSocket: ${data.protocol_presets.websocket.default_header_overhead_bytes}B</li>
        <li>gRPC: ${data.protocol_presets.grpc.default_header_overhead_bytes}B</li>
      </ul>
      <strong>Profile transmisji</strong>
      <ul class="preset-list">
        ${profileItems}
      </ul>
    `;
  } catch (error) {
    presetsContent.textContent = "Nie udało się załadować presetów.";
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
    nagle_enabled: formData.get("nagle_enabled") === "on",
    nagle_max_coalesced_messages: Number(formData.get("nagle_max_coalesced_messages")),
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

function getSelectedComparisonProfiles() {
  const profiles = [];

  if (sequenceForm.querySelector('input[name="compare_profile_standard_ethernet"]').checked) {
    profiles.push("standard_ethernet");
  }
  if (sequenceForm.querySelector('input[name="compare_profile_constrained_mtu"]').checked) {
    profiles.push("constrained_mtu");
  }
  if (sequenceForm.querySelector('input[name="compare_profile_tcp_options_heavy"]').checked) {
    profiles.push("tcp_options_heavy");
  }
  if (sequenceForm.querySelector('input[name="compare_profile_jumbo_frame"]').checked) {
    profiles.push("jumbo_frame");
  }

  return profiles;
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
      `<div class="summary-card muted">Brak efektywnych ustawień.</div>`;
    return;
  }

  const settings = data.effective_settings;

  renderCardGroup(effectiveSettingsBox, [
    { label: "Profil", value: settings.transmission_profile },
    { label: "MTU [B]", value: String(settings.mtu_bytes) },
    { label: "Nagłówek Ethernet [B]", value: String(settings.ethernet_header_size_bytes) },
    { label: "Trailer Ethernet [B]", value: String(settings.ethernet_trailer_size_bytes) },
    { label: "Minimalny payload Ethernet [B]", value: String(settings.ethernet_min_payload_bytes) },
    { label: "Nagłówek IPv4 [B]", value: String(settings.ipv4_header_size_bytes) },
    { label: "Nagłówek TCP [B]", value: String(settings.tcp_header_size_bytes) },
    { label: "Narzut nagłówka aplikacyjnego [B]", value: String(settings.application_header_overhead_bytes) },
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



function extractApiErrorDetail(data, fallbackMessage) {
  if (typeof data?.detail === "string" && data.detail.trim()) {
    return data.detail;
  }
  if (typeof data?.message === "string" && data.message.trim()) {
    return data.message;
  }
  return fallbackMessage;
}

function formatTransportName(name) {
  const mapping = {
    http: "HTTP",
    ws: "WebSocket",
    grpc: "gRPC",
  };
  return mapping[name] || name;
}

function formatValidationScenarioName(name) {
  const mapping = {
    baseline_valid_dict: "Scenariusz bazowy",
    structural_validation_valid_set: "Walidacja strukturalna — poprawne dane",
    full_validation_valid_set: "Pełna walidacja — poprawne dane",
    structural_validation_invalid: "Walidacja strukturalna — błędne dane",
    business_validation_invalid: "Walidacja biznesowa — błędne dane",
  };
  return mapping[name] || name;
}

function formatSerializationOperationName(name) {
  const mapping = {
    set_value: "Ustawienie wartości",
    get_value: "Pobranie wartości",
  };
  return mapping[name] || name;
}

function formatRealtimeScenarioName(name) {
  const mapping = {
    non_empty_fetch: "Pobranie z nowymi zdarzeniami",
    empty_fetch: "Pobranie bez nowych zdarzeń",
  };
  return mapping[name] || name;
}

function formatExpectedOutcomeName(name) {
  const mapping = {
    success: "Sukces",
    structural_validation_error: "Błąd walidacji strukturalnej",
    business_validation_error: "Błąd walidacji biznesowej",
  };
  return mapping[name] || name;
}

function formatEncodingName(name) {
  const mapping = {
    json: "JSON",
    protobuf: "Protobuf",
  };
  return mapping[name] || name;
}

function normalizeApiDetail(detail) {
  return String(detail)
    .replaceAll("http:", "HTTP:")
    .replaceAll("ws:", "WebSocket:")
    .replaceAll("grpc:", "gRPC:");
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
    renderSummary([{ label: "Błąd", value: "Żądanie nie powiodło się" }]);
    effectiveSettingsBox.innerHTML =
      `<div class="summary-card muted">Nie udało się wyznaczyć efektywnych ustawień.</div>`;
    transmissionVisualization.innerHTML =
      `<div class="summary-card muted">Nie udało się wygenerować wizualizacji.</div>`;
    frameLayerVisualization.innerHTML =
      `<div class="summary-card muted">Nie udało się wygenerować budowy ramki.</div>`;
    renderResult(data);
    return;
  }

  renderSummary([
    { label: "Łączna liczba przesłanych bajtów", value: String(data.layer_breakdown.total_transmitted_bytes) },
    { label: "Liczba ramek", value: String(data.frame_analysis.frame_count) },
    { label: "Efektywność payloadu", value: data.efficiency.payload_efficiency_ratio.toFixed(4) },
    { label: "Wymagany bitrate [kb/s]", value: data.efficiency.required_bitrate_kbps.toFixed(4) },
  ]);

  renderEffectiveSettings(data);
  renderResult(data);
  renderSingleTransmissionVisualization(data);
  renderSingleFrameLayerVisualization(data);
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
    renderSummary([{ label: "Błąd", value: "Żądanie nie powiodło się" }]);
    effectiveSettingsBox.innerHTML =
      `<div class="summary-card muted">Nie udało się wyznaczyć efektywnych ustawień.</div>`;
    transmissionVisualization.innerHTML =
      `<div class="summary-card muted">Nie udało się wygenerować wizualizacji.</div>`;
    frameLayerVisualization.innerHTML =
      `<div class="summary-card muted">Nie udało się wygenerować budowy ramki.</div>`;
    renderResult(data);
    return;
  }

  renderSummary([
    { label: "Liczba zagregowanych wiadomości", value: String(data.aggregated_message_count) },
    { label: "Łączna liczba przesłanych bajtów", value: String(data.total_transmitted_bytes) },
    { label: "Łączna liczba ramek", value: String(data.total_frame_count) },
    { label: "Efektywność payloadu", value: data.payload_efficiency_ratio.toFixed(4) },
    { label: "Nagle", value: data.nagle_enabled ? "włączony" : "wyłączony" },
    { label: "Efektywny tryb agregacji", value: data.effective_aggregation_mode },
  ]);

  renderEffectiveSettings(data);
  renderResult(data);
  renderSequenceTransmissionVisualization(data);
  renderSequenceFrameLayerVisualization(data);
}

async function compareNagleVariants() {
  nagleComparisonSummaryPanel.classList.remove("hidden");
  nagleComparisonTablePanel.classList.remove("hidden");
  nagleComparisonChartPanel.classList.remove("hidden");

  nagleComparisonSummary.innerHTML =
    `<div class="summary-card muted">Trwa porównanie wariantów Nagle...</div>`;
  nagleComparisonTable.innerHTML = "";
  nagleComparisonChart.innerHTML = "";

  const basePayload = buildSequencePayload(new FormData(sequenceForm));

  const nagleOffPayload = {
    ...basePayload,
    aggregation_mode:
      basePayload.aggregation_mode === "nagle_like"
        ? "per_message"
        : basePayload.aggregation_mode,
    nagle_enabled: false,
  };

  const nagleOnPayload = {
    ...basePayload,
    aggregation_mode:
      basePayload.aggregation_mode === "nagle_like"
        ? "per_message"
        : basePayload.aggregation_mode,
    nagle_enabled: true,
  };

  try {
    const [offResponse, onResponse] = await Promise.all([
      fetch("/analyze/sequence", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(nagleOffPayload),
      }),
      fetch("/analyze/sequence", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(nagleOnPayload),
      }),
    ]);

    const offData = await offResponse.json();
    const onData = await onResponse.json();

    if (!offResponse.ok || !onResponse.ok) {
      nagleComparisonSummary.innerHTML =
        `<div class="summary-card muted">Porównanie Nagle nie powiodło się.</div>`;
      nagleComparisonTable.innerHTML = `
        <div class="summary-card muted">${JSON.stringify(
          { nagle_off: offData, nagle_on: onData },
          null,
          2
        )}</div>
      `;
      nagleComparisonChart.innerHTML =
        `<div class="summary-card muted">Brak wykresu.</div>`;
      return;
    }

    const comparisonRows = [
      {
        variant_label: "Nagle off",
        nagle_enabled: offData.nagle_enabled,
        effective_aggregation_mode: offData.effective_aggregation_mode,
        aggregated_message_count: offData.aggregated_message_count,
        total_transmitted_bytes: offData.total_transmitted_bytes,
        total_frame_count: offData.total_frame_count,
        payload_efficiency_ratio: offData.payload_efficiency_ratio,
        aggregated_payload_sizes_bytes: offData.aggregated_payload_sizes_bytes.join(", "),
      },
      {
        variant_label: "Nagle on",
        nagle_enabled: onData.nagle_enabled,
        effective_aggregation_mode: onData.effective_aggregation_mode,
        aggregated_message_count: onData.aggregated_message_count,
        total_transmitted_bytes: onData.total_transmitted_bytes,
        total_frame_count: onData.total_frame_count,
        payload_efficiency_ratio: onData.payload_efficiency_ratio,
        aggregated_payload_sizes_bytes: onData.aggregated_payload_sizes_bytes.join(", "),
      },
    ];

    const bytesDelta = onData.total_transmitted_bytes - offData.total_transmitted_bytes;
    const framesDelta = onData.total_frame_count - offData.total_frame_count;
    const efficiencyDelta =
      onData.payload_efficiency_ratio - offData.payload_efficiency_ratio;

    renderCardGroup(nagleComparisonSummary, [
      {
        label: "Różnica bajtów (on - off)",
        value: String(bytesDelta),
      },
      {
        label: "Różnica ramek (on - off)",
        value: String(framesDelta),
      },
      {
        label: "Różnica efektywności",
        value: efficiencyDelta.toFixed(4),
      },
      {
        label: "Lepszy wariant wg bajtów",
        value:
          onData.total_transmitted_bytes < offData.total_transmitted_bytes
            ? "Nagle on"
            : onData.total_transmitted_bytes > offData.total_transmitted_bytes
              ? "Nagle off"
              : "remis",
      },
    ]);

    renderTable(
      nagleComparisonTable,
      [
        { key: "variant_label", label: "Wariant" },
        {
          key: "nagle_enabled",
          label: "Nagle",
          render: (row) => (row.nagle_enabled ? "włączony" : "wyłączony"),
        },
        {
          key: "effective_aggregation_mode",
          label: "Efektywny tryb",
        },
        {
          key: "aggregated_message_count",
          label: "Zagregowane wiadomości",
        },
        {
          key: "total_transmitted_bytes",
          label: "Przesłane bajty",
        },
        {
          key: "total_frame_count",
          label: "Ramki",
        },
        {
          key: "payload_efficiency_ratio",
          label: "Efektywność",
          render: (row) => Number(row.payload_efficiency_ratio).toFixed(4),
        },
        {
          key: "aggregated_payload_sizes_bytes",
          label: "Grupy payloadów",
        },
      ],
      comparisonRows
    );

    renderSimpleComparisonBars(nagleComparisonChart, comparisonRows);
  } catch (error) {
    nagleComparisonSummary.innerHTML =
      `<div class="summary-card muted">Porównanie Nagle nie powiodło się.</div>`;
    nagleComparisonTable.innerHTML =
      `<div class="summary-card muted">${error}</div>`;
    nagleComparisonChart.innerHTML =
      `<div class="summary-card muted">Brak wykresu.</div>`;
  }
}

function resetProfileComparisonViews() {
  profileComparisonSummary.innerHTML =
    `<div class="summary-card muted">Uruchom porównanie profili, aby zobaczyć wyniki.</div>`;
  profileComparisonTable.innerHTML =
    `<div class="summary-card muted">Uruchom porównanie profili, aby zobaczyć wyniki.</div>`;
  profileComparisonChart.innerHTML =
    `<div class="summary-card muted">Uruchom porównanie profili, aby zobaczyć wykres.</div>`;
}

async function compareTransmissionProfiles() {
  profileComparisonSummaryPanel.classList.remove("hidden");
  profileComparisonTablePanel.classList.remove("hidden");
  profileComparisonChartPanel.classList.remove("hidden");

  profileComparisonSummary.innerHTML =
    `<div class="summary-card muted">Trwa porównanie profili transmisji...</div>`;
  profileComparisonTable.innerHTML = "";
  profileComparisonChart.innerHTML = "";

  const selectedProfiles = getSelectedComparisonProfiles();

  if (!selectedProfiles.length) {
    profileComparisonSummary.innerHTML =
      `<div class="summary-card muted">Wybierz co najmniej jeden profil transmisji.</div>`;
    profileComparisonTable.innerHTML =
      `<div class="summary-card muted">Brak danych.</div>`;
    profileComparisonChart.innerHTML =
      `<div class="summary-card muted">Brak wykresu.</div>`;
    return;
  }

  const basePayload = buildSequencePayload(new FormData(sequenceForm));

  try {
    const responses = await Promise.all(
      selectedProfiles.map((profile) =>
        fetch("/analyze/sequence", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ...basePayload,
            transmission_profile: profile,
          }),
        }).then(async (response) => ({
          ok: response.ok,
          profile,
          data: await response.json(),
        }))
      )
    );

    const failed = responses.filter((item) => !item.ok);
    if (failed.length) {
      profileComparisonSummary.innerHTML =
        `<div class="summary-card muted">Porównanie profili nie powiodło się.</div>`;
      profileComparisonTable.innerHTML =
        `<div class="summary-card muted"><pre>${JSON.stringify(failed, null, 2)}</pre></div>`;
      profileComparisonChart.innerHTML =
        `<div class="summary-card muted">Brak wykresu.</div>`;
      return;
    }

    const rows = responses.map((item) => ({
      profile: item.profile,
      total_transmitted_bytes: item.data.total_transmitted_bytes,
      total_frame_count: item.data.total_frame_count,
      aggregated_message_count: item.data.aggregated_message_count,
      payload_efficiency_ratio: item.data.payload_efficiency_ratio,
      effective_aggregation_mode: item.data.effective_aggregation_mode,
      aggregated_payload_sizes_bytes: item.data.aggregated_payload_sizes_bytes.join(", "),
    }));

    const bestByBytes = [...rows].sort(
      (a, b) => a.total_transmitted_bytes - b.total_transmitted_bytes
    )[0];

    const worstByBytes = [...rows].sort(
      (a, b) => b.total_transmitted_bytes - a.total_transmitted_bytes
    )[0];

    const bestByEfficiency = [...rows].sort(
      (a, b) => b.payload_efficiency_ratio - a.payload_efficiency_ratio
    )[0];

    renderCardGroup(profileComparisonSummary, [
      {
        label: "Najlepszy profil wg bajtów",
        value: `${bestByBytes.profile} (${bestByBytes.total_transmitted_bytes} B)`,
      },
      {
        label: "Najgorszy profil wg bajtów",
        value: `${worstByBytes.profile} (${worstByBytes.total_transmitted_bytes} B)`,
      },
      {
        label: "Najlepsza efektywność",
        value: `${bestByEfficiency.profile} (${bestByEfficiency.payload_efficiency_ratio.toFixed(4)})`,
      },
      {
        label: "Liczba porównanych profili",
        value: String(rows.length),
      },
    ]);

    renderTable(
      profileComparisonTable,
      [
        { key: "profile", label: "Profil" },
        { key: "total_transmitted_bytes", label: "Przesłane bajty" },
        { key: "total_frame_count", label: "Ramki" },
        { key: "aggregated_message_count", label: "Zagregowane wiadomości" },
        {
          key: "payload_efficiency_ratio",
          label: "Efektywność",
          render: (row) => Number(row.payload_efficiency_ratio).toFixed(4),
        },
        { key: "effective_aggregation_mode", label: "Efektywny tryb" },
        { key: "aggregated_payload_sizes_bytes", label: "Grupy payloadów" },
      ],
      rows
    );

    renderSimpleComparisonBars(
      profileComparisonChart,
      rows.map((row) => ({
        variant_label: row.profile,
        total_transmitted_bytes: row.total_transmitted_bytes,
        total_frame_count: row.total_frame_count,
        aggregated_message_count: row.aggregated_message_count,
        payload_efficiency_ratio: row.payload_efficiency_ratio,
      }))
    );
  } catch (error) {
    profileComparisonSummary.innerHTML =
      `<div class="summary-card muted">Porównanie profili nie powiodło się.</div>`;
    profileComparisonTable.innerHTML =
      `<div class="summary-card muted">${error}</div>`;
    profileComparisonChart.innerHTML =
      `<div class="summary-card muted">Brak wykresu.</div>`;
  }
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
      `<div class="summary-card muted">Nie udało się wczytać domyślnej konfiguracji środowiska.</div>`;
  }
}

async function loadRecentRuns(event = null) {
  if (event) {
    event.preventDefault();
  }

  recentRunsSummary.innerHTML =
    `<div class="summary-card muted">Ładowanie ostatnich uruchomień...</div>`;
  recentRunsTable.innerHTML = "";

  try {
    const formData = new FormData(recentRunsForm);
    const limit = Number(formData.get("limit"));
    const experimentName = formData.get("experiment_name");

    const response = await fetch(buildRecentRunsUrl(limit, experimentName));
    const data = await response.json();

    if (!response.ok) {
      recentRunsSummary.innerHTML =
        `<div class="summary-card muted">Nie udało się załadować ostatnich uruchomień.</div>`;
      recentRunsTable.innerHTML =
        `<div class="summary-card muted">${JSON.stringify(data)}</div>`;
      return;
    }

    renderCardGroup(recentRunsSummary, [
      {
        label: "Łącznie pasujących uruchomień",
        value: String(data.total_count),
      },
      {
        label: "Wyświetlone uruchomienia",
        value: String(data.runs.length),
      },
      {
        label: "Filtr",
        value: experimentName || "wszystkie",
      },
      {
        label: "Limit",
        value: String(limit),
      },
    ]);

    renderTable(
      recentRunsTable,
      [
        { key: "experiment_name", label: "Eksperyment" },
        { key: "run_id", label: "ID uruchomienia" },
        {
          key: "run_label",
          label: "Etykieta uruchomienia",
          render: (row) => row.run_label || "-",
        },
        { key: "saved_at", label: "Zapisano o" },
        { key: "file_path", label: "Ścieżka pliku" },
        {
          key: "actions",
          label: "Akcja",
          render: (row) =>
            `<button class="primary-button secondary-button load-run-detail-button" data-run-id="${row.run_id}">Wczytaj</button>`,
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
      `<div class="summary-card muted">Nie udało się załadować ostatnich uruchomień.</div>`;
    recentRunsTable.innerHTML =
      `<div class="summary-card muted">${error}</div>`;
  }
}

async function loadSavedRunDetailById(runId) {
  if (!runId) {
    savedRunDetailSummary.innerHTML =
      `<div class="summary-card muted">Najpierw podaj ID uruchomienia.</div>`;
    savedRunDetailJson.textContent = "Nie wczytano zapisanego uruchomienia.";
    return;
  }

  savedRunDetailSummary.innerHTML =
    `<div class="summary-card muted">Ładowanie zapisanego uruchomienia...</div>`;
  savedRunDetailJson.textContent = "Ładowanie zapisanego uruchomienia...";

  try {
    const response = await fetch(`/experiment-runs/${encodeURIComponent(runId)}`);
    const data = await response.json();

    if (!response.ok) {
      savedRunDetailSummary.innerHTML =
        `<div class="summary-card muted">Nie udało się wczytać zapisanego uruchomienia.</div>`;
      savedRunDetailJson.textContent = JSON.stringify(data, null, 2);
      return;
    }

    renderCardGroup(savedRunDetailSummary, [
      { label: "Eksperyment", value: data.metadata.experiment_name },
      { label: "ID uruchomienia", value: data.metadata.run_id },
      { label: "Etykieta uruchomienia", value: data.metadata.run_label || "-" },
      { label: "Zapisano o", value: data.metadata.saved_at },
      { label: "Ścieżka pliku", value: data.metadata.file_path },
    ]);

    savedRunDetailJson.textContent = JSON.stringify(data, null, 2);
    savedRunDetailForm.querySelector('input[name="run_id"]').value =
      data.metadata.run_id;
  } catch (error) {
    savedRunDetailSummary.innerHTML =
      `<div class="summary-card muted">Nie udało się wczytać zapisanego uruchomienia.</div>`;
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
    `<div class="summary-card muted">Sprawdzanie środowiska...</div>`;
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
        `<div class="summary-card muted">Sprawdzenie statusu środowiska nie powiodło się.</div>`;
      environmentStatusTable.innerHTML =
        `<div class="summary-card muted">${JSON.stringify(data)}</div>`;
      return;
    }

    const availableCount = data.services.filter((service) => service.available).length;

    renderCardGroup(environmentStatusSummary, [
      {
        label: "Stan ogólny",
        value: data.all_available ? "wszystkie dostępne" : "częściowo niedostępne",
      },
      {
        label: "Dostępne usługi",
        value: `${availableCount}/${data.services.length}`,
      },
      {
        label: "Timeout [s]",
        value: String(data.config.timeout_seconds),
      },
      {
        label: "Sprawdzono o",
        value: data.checked_at,
      },
    ]);

    renderTable(
      environmentStatusTable,
      [
        { key: "service_name", label: "Usługa" },
        {
          key: "available",
          label: "Dostępna",
          render: (row) =>
            row.available
              ? `<span class="report-ok">tak</span>`
              : `<span class="report-missing">nie</span>`,
        },
        {
          key: "response_time_ms",
          label: "Czas odpowiedzi [ms]",
          render: (row) =>
            row.response_time_ms === null
              ? "-"
              : Number(row.response_time_ms).toFixed(3),
        },
        { key: "detail", label: "Szczegóły" },
      ],
      data.services
    );
  } catch (error) {
    environmentStatusSummary.innerHTML =
      `<div class="summary-card muted">Nie udało się odświeżyć statusu środowiska.</div>`;
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
    validationRunJson.textContent = "Nie udało się wczytać domyślnej konfiguracji walidacji.";
  }
}

async function loadSerializationDefaults() {
  try {
    const response = await fetch("/experiments/serialization/default-config");
    const config = await response.json();
    fillSerializationExperimentForm(config);
  } catch (error) {
    serializationRunJson.textContent = "Nie udało się wczytać domyślnej konfiguracji serializacji.";
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
      `<div class="summary-card muted">Wybierz co najmniej jeden transport.</div>`;
    return;
  }

  requestResponseRunSummary.innerHTML = `<div class="summary-card muted">Trwa uruchamianie eksperymentu...</div>`;
  requestResponseRunJson.textContent = "Trwa uruchamianie eksperymentu...";

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
    const detail = normalizeApiDetail(extractApiErrorDetail(
      data,
      "Uruchomienie eksperymentu nie powiodło się."
    ));
    requestResponseRunSummary.innerHTML = `<div class="summary-card muted">${detail}</div>`;
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
    { label: "Iteracje", value: String(data.iterations) },
    { label: "Uruchomione transporty", value: String(data.transports.length) },
    { label: "Najszybsze ustawienie wartości", value: `${formatTransportName(setBest.transport)} (${setBest.avg_ms.toFixed(3)} ms)` },
    { label: "Najszybsze pobranie wartości", value: `${formatTransportName(getBest.transport)} (${getBest.avg_ms.toFixed(3)} ms)` },
  ];

  if (data.saved_result) {
    requestResponseCards.push({
      label: "Zapisany run",
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
      { key: "transport", label: "Transport", render: (row) => formatTransportName(row.transport) },
      { key: "operation", label: "Operacja", render: (row) => formatSerializationOperationName(row.operation) },
      { key: "avg_ms", label: "Średnia [ms]", render: (row) => row.avg_ms.toFixed(3) },
      { key: "median_ms", label: "Mediana [ms]", render: (row) => row.median_ms.toFixed(3) },
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
      `<div class="summary-card muted">Wybierz co najmniej jeden transport.</div>`;
    return;
  }

  realtimeRunSummary.innerHTML = `<div class="summary-card muted">Trwa uruchamianie eksperymentu...</div>`;
  realtimeRunJson.textContent = "Trwa uruchamianie eksperymentu...";

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
    const detail = normalizeApiDetail(extractApiErrorDetail(
      data,
      "Uruchomienie eksperymentu nie powiodło się."
    ));
    realtimeRunSummary.innerHTML = `<div class="summary-card muted">${detail}</div>`;
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
    { label: "Iteracje", value: String(data.iterations) },
    { label: "Uruchomione transporty", value: String(data.transports.length) },
    { label: "Najszybsze pobranie z danymi", value: `${formatTransportName(bestNonEmpty.transport)} (${bestNonEmpty.summary.avg_ms.toFixed(3)} ms)` },
    { label: "Najszybsze pobranie bez danych", value: `${formatTransportName(bestEmpty.transport)} (${bestEmpty.summary.avg_ms.toFixed(3)} ms)` },
  ];

  if (data.saved_result) {
    realtimeCards.push({
      label: "Zapisany run",
      value: data.saved_result.run_id,
    });
  }

  renderCardGroup(realtimeRunSummary, realtimeCards);

  renderTable(
    realtimeRunTable,
    [
      { key: "transport", label: "Transport", render: (row) => formatTransportName(row.transport) },
      { key: "scenario", label: "Scenariusz", render: (row) => formatRealtimeScenarioName(row.scenario) },
      { key: "summary.avg_ms", label: "Średnia [ms]", render: (row) => row.summary.avg_ms.toFixed(3) },
      { key: "summary.median_ms", label: "Mediana [ms]", render: (row) => row.summary.median_ms.toFixed(3) },
      { key: "summary.min_ms", label: "Min [ms]", render: (row) => row.summary.min_ms.toFixed(3) },
      { key: "summary.max_ms", label: "Max [ms]", render: (row) => row.summary.max_ms.toFixed(3) },
      { key: "expected_event_count", label: "Liczba zdarzeń", render: (row) => String(row.expected_event_count) },
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
      `<div class="summary-card muted">Wybierz co najmniej jeden scenariusz.</div>`;
    return;
  }

  validationRunSummary.innerHTML = `<div class="summary-card muted">Trwa uruchamianie eksperymentu...</div>`;
  validationRunJson.textContent = "Trwa uruchamianie eksperymentu...";

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
    const detail = normalizeApiDetail(extractApiErrorDetail(
      data,
      "Uruchomienie eksperymentu nie powiodło się."
    ));
    validationRunSummary.innerHTML = `<div class="summary-card muted">${detail}</div>`;
    validationRunJson.textContent = JSON.stringify(data, null, 2);
    validationRunTable.innerHTML = "";
    return;
  }

  const fastest = bestRowBy(data.measurements, "summary.avg_us");
  const slowest = worstRowBy(data.measurements, "summary.avg_us");

  const validationCards = [
    { label: "Iteracje", value: String(data.iterations) },
    { label: "Uruchomione scenariusze", value: String(data.scenarios.length) },
    { label: "Najszybszy scenariusz", value: `${formatValidationScenarioName(fastest.scenario)} (${fastest.summary.avg_us.toFixed(3)} us)` },
    { label: "Najwolniejszy scenariusz", value: `${formatValidationScenarioName(slowest.scenario)} (${slowest.summary.avg_us.toFixed(3)} us)` },
  ];

  if (data.saved_result) {
    validationCards.push({
      label: "Zapisany run",
      value: data.saved_result.run_id,
    });
  }

  renderCardGroup(validationRunSummary, validationCards);

  renderTable(
    validationRunTable,
    [
      { key: "scenario", label: "Scenariusz", render: (row) => formatValidationScenarioName(row.scenario) },
      { key: "expected_outcome", label: "Oczekiwany wynik", render: (row) => formatExpectedOutcomeName(row.expected_outcome) },
      { key: "summary.avg_us", label: "Średnia [us]", render: (row) => row.summary.avg_us.toFixed(3) },
      { key: "summary.median_us", label: "Mediana [us]", render: (row) => row.summary.median_us.toFixed(3) },
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
      `<div class="summary-card muted">Wybierz co najmniej jeden transport.</div>`;
    return;
  }

  if (!payload.operations.length) {
    serializationRunSummary.innerHTML =
      `<div class="summary-card muted">Wybierz co najmniej jedną operację.</div>`;
    return;
  }

  serializationRunSummary.innerHTML = `<div class="summary-card muted">Trwa uruchamianie eksperymentu...</div>`;
  serializationRunJson.textContent = "Trwa uruchamianie eksperymentu...";

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
    const detail = normalizeApiDetail(extractApiErrorDetail(
      data,
      "Uruchomienie eksperymentu nie powiodło się."
    ));
    serializationRunSummary.innerHTML = `<div class="summary-card muted">${detail}</div>`;
    serializationRunJson.textContent = JSON.stringify(data, null, 2);
    serializationRunTable.innerHTML = "";
    return;
  }

  const smallestRequest = bestRowBy(data.measurements, "request_size_bytes");
  const smallestResponse = bestRowBy(data.measurements, "response_size_bytes");
  const fastestSerialize = bestRowBy(data.measurements, "request_serialize_summary.avg_us");
  const fastestDeserialize = bestRowBy(data.measurements, "response_deserialize_summary.avg_us");

  const serializationCards = [
    { label: "Iteracje", value: String(data.iterations) },
    { label: "Pomiary", value: String(data.measurements.length) },
    { label: "Najmniejsze żądanie", value: `${formatTransportName(smallestRequest.transport)} / ${formatSerializationOperationName(smallestRequest.operation)} (${smallestRequest.request_size_bytes} B)` },
    { label: "Najszybsza serializacja żądania", value: `${formatTransportName(fastestSerialize.transport)} / ${formatSerializationOperationName(fastestSerialize.operation)} (${fastestSerialize.request_serialize_summary.avg_us.toFixed(3)} us)` },
    { label: "Najmniejsza odpowiedź", value: `${formatTransportName(smallestResponse.transport)} / ${formatSerializationOperationName(smallestResponse.operation)} (${smallestResponse.response_size_bytes} B)` },
    { label: "Najszybsza deserializacja odpowiedzi", value: `${formatTransportName(fastestDeserialize.transport)} / ${formatSerializationOperationName(fastestDeserialize.operation)} (${fastestDeserialize.response_deserialize_summary.avg_us.toFixed(3)} us)` },
  ];

  if (data.saved_result) {
    serializationCards.push({
      label: "Zapisany run",
      value: data.saved_result.run_id,
    });
  }

  renderCardGroup(serializationRunSummary, serializationCards);

  renderTable(
    serializationRunTable,
    [
      { key: "transport", label: "Transport", render: (row) => formatTransportName(row.transport) },
      { key: "operation", label: "Operacja", render: (row) => formatSerializationOperationName(row.operation) },
      { key: "encoding", label: "Kodowanie", render: (row) => formatEncodingName(row.encoding) },
      { key: "request_size_bytes", label: "Żądanie [B]" },
      { key: "response_size_bytes", label: "Odpowiedź [B]" },
      { key: "request_serialize_summary.avg_us", label: "Serializacja żądania [us]", render: (row) => row.request_serialize_summary.avg_us.toFixed(3) },
      { key: "request_deserialize_summary.avg_us", label: "Deserializacja żądania [us]", render: (row) => row.request_deserialize_summary.avg_us.toFixed(3) },
      { key: "response_serialize_summary.avg_us", label: "Serializacja odpowiedzi [us]", render: (row) => row.response_serialize_summary.avg_us.toFixed(3) },
      { key: "response_deserialize_summary.avg_us", label: "Deserializacja odpowiedzi [us]", render: (row) => row.response_deserialize_summary.avg_us.toFixed(3) },
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
          ${report.exists ? "dostępny" : "brak"}
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
      { label: "Najlepszy transport dla ustawienia wartości", value: `${formatTransportName(bestSet.transport)} (${bestSet.avg_ms.toFixed(3)} ms)` },
      { label: "Najlepszy transport dla pobrania wartości", value: `${formatTransportName(bestGet.transport)} (${bestGet.avg_ms.toFixed(3)} ms)` },
      { label: "Najlepszy wynik scenariusza realtime", value: `${formatTransportName(bestRealtime.transport)} (${bestRealtime.avg_ms.toFixed(3)} ms)` },
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
      { label: "Załadowane scenariusze", value: String(validation.length) },
      { label: "Najszybszy scenariusz", value: fastestValidation.scenario },
    ]);

    renderTable(
      requestResponseTable,
      [
        { key: "transport", label: "Transport" },
        { key: "operation", label: "Operacja" },
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
        { key: "scenario", label: "Scenariusz" },
        { key: "avg_ms", label: "Avg [ms]", render: (row) => row.avg_ms.toFixed(3) },
        { key: "median_ms", label: "Median [ms]", render: (row) => row.median_ms.toFixed(3) },
        { key: "expected_event_count", label: "Event count" },
      ],
      realtime
    );

    renderTable(
      validationTable,
      [
        { key: "scenario", label: "Scenariusz" },
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
    availableReports.innerHTML = `<div class="summary-card muted">Nie udało się załadować raportów.</div>`;
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
compareNagleButton.addEventListener("click", compareNagleVariants);
compareProfilesButton.addEventListener("click", compareTransmissionProfiles);

navOverhead.addEventListener("click", () => setMainView("overhead"));
navExperiments.addEventListener("click", () => setMainView("experiments"));
navEnvironment.addEventListener("click", () => setMainView("environment"));
navHistory.addEventListener("click", () => setMainView("history"));
if (loadReportButton) {
  loadReportButton.addEventListener("click", loadSelectedReport);
}

if (experimentTabRequestResponse) {
  experimentTabRequestResponse.addEventListener("click", () => setExperimentTab("request_response"));
}
if (experimentTabRealtime) {
  experimentTabRealtime.addEventListener("click", () => setExperimentTab("realtime"));
}
if (experimentTabValidation) {
  experimentTabValidation.addEventListener("click", () => setExperimentTab("validation"));
}
if (experimentTabSerialization) {
  experimentTabSerialization.addEventListener("click", () => setExperimentTab("serialization"));
}

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
loadRecentRuns();
setExperimentTab("request_response");
