const state = {
  data: null,
  assets: [],
  filtered: [],
  selectedId: null,
  sortKey: null,
  sortDirection: "asc"
};

const windows = ["0-12 months", "12-24 months", "24-36 months", "36+ months"];
const diffLevels = ["Low", "Modest", "Meaningful", "High"];
const budgetLevels = ["Low", "Medium", "High"];

const el = {
  lastUpdated: document.querySelector("#lastUpdated"),
  areaFilter: document.querySelector("#areaFilter"),
  phaseFilter: document.querySelector("#phaseFilter"),
  horizonFilter: document.querySelector("#horizonFilter"),
  riskFilter: document.querySelector("#riskFilter"),
  searchInput: document.querySelector("#searchInput"),
  clearFilters: document.querySelector("#clearFilters"),
  saveView: document.querySelector("#saveView"),
  cadenceSelect: document.querySelector("#cadenceSelect"),
  metricAssets: document.querySelector("#metricAssets"),
  metricScope: document.querySelector("#metricScope"),
  metricHigh: document.querySelector("#metricHigh"),
  metricNear: document.querySelector("#metricNear"),
  timelineChart: document.querySelector("#timelineChart"),
  heatmap: document.querySelector("#heatmap"),
  tableTitle: document.querySelector("#tableTitle"),
  assetRows: document.querySelector("#assetRows"),
  assetDetail: document.querySelector("#assetDetail"),
  closeDetail: document.querySelector("#closeDetail"),
  backToTop: document.querySelector("#backToTop"),
  tableHeaders: document.querySelectorAll("th[data-sort]")
};

init();

async function init() {
  const response = await fetch("data/pipeline-assets.json", { cache: "no-store" });
  state.data = await response.json();
  state.assets = state.data.assets || [];
  state.selectedId = state.assets[0]?.asset_id || null;

  hydrateFilters();
  bindEvents();
  applyFilters();
}

function hydrateFilters() {
  addOptions(el.areaFilter, ["All", ...unique(state.assets.map((asset) => asset.therapeutic_area))]);
  addOptions(el.phaseFilter, ["All", ...unique(state.assets.map((asset) => asset.phase))]);
  addOptions(el.horizonFilter, ["All", ...windows]);
  addOptions(el.riskFilter, ["All", "High", "Medium", "Low"]);
}

function bindEvents() {
  [el.areaFilter, el.phaseFilter, el.horizonFilter, el.riskFilter, el.searchInput].forEach((node) => {
    node.addEventListener("input", applyFilters);
  });

  el.tableHeaders.forEach((header) => {
    header.addEventListener("click", () => {
      setHeaderSort(header.dataset.sort);
    });
    header.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        setHeaderSort(header.dataset.sort);
      }
    });
  });

  el.clearFilters.addEventListener("click", () => {
    el.areaFilter.value = "All";
    el.phaseFilter.value = "All";
    el.horizonFilter.value = "All";
    el.riskFilter.value = "All";
    state.sortKey = null;
    state.sortDirection = "asc";
    el.searchInput.value = "";
    applyFilters();
  });

  el.saveView.addEventListener("click", () => {
    const saved = {
      area: el.areaFilter.value,
      phase: el.phaseFilter.value,
      horizon: el.horizonFilter.value,
      risk: el.riskFilter.value,
      sortKey: state.sortKey,
      sortDirection: state.sortDirection,
      search: el.searchInput.value,
      cadence: el.cadenceSelect.value
    };
    localStorage.setItem("pipeline-intelligence-view", JSON.stringify(saved));
    el.saveView.textContent = "View saved";
    setTimeout(() => {
      el.saveView.textContent = "Save current view";
    }, 1400);
  });

  el.closeDetail.addEventListener("click", () => {
    state.selectedId = null;
    renderDetail();
    renderTable();
  });

  el.backToTop.addEventListener("click", (event) => {
    event.preventDefault();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  el.assetDetail.addEventListener("click", (event) => {
    toggleBasisPanel(event.target.closest(".basis-toggle"));
  });

  el.assetDetail.addEventListener("keydown", (event) => {
    const toggle = event.target.closest(".basis-toggle");
    if (!toggle || (event.key !== "Enter" && event.key !== " ")) return;
    event.preventDefault();
    toggleBasisPanel(toggle);
  });
}

function toggleBasisPanel(toggle) {
  if (!toggle) return;
  const panel = toggle.closest(".basis-panel");
  const willOpen = !panel.classList.contains("is-open");
  el.assetDetail.querySelectorAll(".basis-panel.is-open").forEach((openPanel) => {
    if (openPanel === panel) return;
    openPanel.classList.remove("is-open");
    openPanel.querySelector(".basis-toggle")?.setAttribute("aria-expanded", "false");
  });
  panel.classList.toggle("is-open", willOpen);
  const isOpen = panel.classList.contains("is-open");
  toggle.setAttribute("aria-expanded", String(isOpen));
  if (isOpen) {
    positionBasisPanel(panel);
  }
}

function positionBasisPanel(panel) {
  const toggle = panel.querySelector(".basis-toggle");
  const popup = panel.querySelector(".basis");
  if (!toggle || !popup) return;

  popup.style.left = "";
  popup.style.top = "";
  const toggleRect = toggle.getBoundingClientRect();
  const popupRect = popup.getBoundingClientRect();
  const margin = 8;
  const left = Math.min(
    Math.max(margin, toggleRect.right - popupRect.width),
    window.innerWidth - popupRect.width - margin
  );
  const belowTop = toggleRect.bottom + 6;
  const aboveTop = toggleRect.top - popupRect.height - 6;
  const top = belowTop + popupRect.height + margin <= window.innerHeight
    ? belowTop
    : Math.max(margin, aboveTop);

  popup.style.left = `${left}px`;
  popup.style.top = `${top}px`;
}

function setHeaderSort(sortKey) {
  if (state.sortKey === sortKey) {
    state.sortDirection = state.sortDirection === "asc" ? "desc" : "asc";
  } else {
    state.sortKey = sortKey;
    state.sortDirection = "asc";
  }
  applyFilters();
}

function applyFilters() {
  const query = el.searchInput.value.trim().toLowerCase();
  state.filtered = state.assets.filter((asset) => {
    const matchesArea = el.areaFilter.value === "All" || asset.therapeutic_area === el.areaFilter.value;
    const matchesPhase = el.phaseFilter.value === "All" || asset.phase === el.phaseFilter.value;
    const matchesHorizon = el.horizonFilter.value === "All" || launchBucket(asset) === el.horizonFilter.value;
    const matchesRisk = el.riskFilter.value === "All" || asset.disruption_risk === el.riskFilter.value;
    const haystack = [asset.asset_name, asset.manufacturer, asset.indication, asset.mechanism].join(" ").toLowerCase();
    return matchesArea && matchesPhase && matchesHorizon && matchesRisk && (!query || haystack.includes(query));
  });

  if (state.sortKey) {
    sortFilteredAssets();
  }

  if (!state.filtered.some((asset) => asset.asset_id === state.selectedId)) {
    state.selectedId = state.filtered[0]?.asset_id || null;
  }

  renderAll();
}

function renderAll() {
  const generatedAt = new Date(state.data.metadata.generated_at);
  el.lastUpdated.textContent = `Last updated ${generatedAt.toLocaleString()}`;
  el.metricAssets.textContent = state.filtered.length;
  el.metricScope.textContent = `${state.data.metadata.scope || state.data.metadata.condition || "Configured"} scope`;
  el.metricHigh.textContent = state.filtered.filter((asset) => asset.disruption_risk === "High").length;
  el.metricNear.textContent = state.filtered.filter((asset) => ["0-12 months", "12-24 months"].includes(launchBucket(asset))).length;
  el.tableTitle.textContent = `PIPELINE ASSETS (${state.filtered.length || 0})`;

  renderTimeline();
  renderHeatmap();
  renderTable();
  renderDetail();
  updateSortHeaders();
}

function sortFilteredAssets() {
  const direction = state.sortDirection === "desc" ? -1 : 1;
  const collator = new Intl.Collator(undefined, { numeric: true, sensitivity: "base" });
  state.filtered.sort((a, b) => {
    const primary = collator.compare(sortValue(a, state.sortKey), sortValue(b, state.sortKey));
    if (primary !== 0) return primary * direction;
    return collator.compare(a.asset_name || "", b.asset_name || "");
  });
}

function sortValue(asset, key) {
  const values = {
    asset: asset.asset_name,
    ctgov: (asset.clinical_trial_links || asset.sources || [])
      .map((source) => source.url?.match(/NCT\d{8}/i)?.[0] || source.title?.match(/NCT\d{8}/i)?.[0])
      .filter(Boolean)
      .join(", "),
    manufacturer: asset.manufacturer,
    indication: asset.indication,
    phase: asset.phase,
    launch: launchDisplay(asset),
    clinical: asset.clinical_differentiation,
    cost: `${formatMoney(asset.estimated_annual_cost_low)} - ${formatMoney(asset.estimated_annual_cost_high)}`,
    risk: asset.disruption_risk,
    action: asset.recommended_action
  };
  return String(values[key] || "");
}

function updateSortHeaders() {
  el.tableHeaders.forEach((header) => {
    const isActive = header.dataset.sort === state.sortKey;
    header.classList.toggle("active-sort", isActive);
    header.dataset.direction = isActive ? state.sortDirection : "";
    header.setAttribute("aria-sort", isActive ? (state.sortDirection === "asc" ? "ascending" : "descending") : "none");
  });
}

function renderTimeline() {
  const max = Math.max(1, ...windows.map((window) => state.filtered.filter((asset) => launchBucket(asset) === window).length));
  el.timelineChart.innerHTML = windows.map((window) => {
    const windowAssets = state.filtered.filter((asset) => launchBucket(asset) === window);
    const groups = groupCount(windowAssets, "therapeutic_area");
    const total = windowAssets.length;
    const totalHeight = total ? Math.max(6, (total / max) * 178) : 0;
    const segments = Object.entries(groups).map(([area, count]) => {
      const height = total ? Math.max(6, (count / max) * 178) : 0;
      return `<div class="bar-segment" title="${escapeHtml(area)}: ${count}" style="height:${height}px;background:${areaColor(area)}"></div>`;
    }).join("");

    return `
      <div class="bar-column">
        <div class="bar-plot">
          <div class="bar-total" style="bottom:${totalHeight + 8}px">${total}</div>
          <div class="bar-stack">${segments}</div>
        </div>
        <div class="bar-label">${window}</div>
      </div>
    `;
  }).join("");
}

function renderHeatmap() {
  el.heatmap.innerHTML = "";
  for (const budget of budgetLevels.slice().reverse()) {
    for (const diff of diffLevels) {
      const count = state.filtered.filter((asset) => asset.budget_impact_level === budget && asset.clinical_differentiation === diff).length;
      const color = heatColor(count, budget);
      const cell = document.createElement("div");
      cell.className = "heat-cell";
      cell.style.background = color;
      cell.innerHTML = `${count}<small>${budget} / ${diff}</small>`;
      el.heatmap.appendChild(cell);
    }
  }
}

function renderTable() {
  el.assetRows.innerHTML = state.filtered.map((asset) => `
    <tr class="${asset.asset_id === state.selectedId ? "selected" : ""}" data-id="${escapeHtml(asset.asset_id)}">
      <td><span class="asset-link">${escapeHtml(asset.asset_name)}</span></td>
      <td>${renderCtgovLinks(asset)}</td>
      <td>${escapeHtml(asset.manufacturer)}</td>
      <td>${escapeHtml(asset.indication)}</td>
      <td>${escapeHtml(asset.phase)}</td>
      <td title="${escapeAttribute(launchRationale(asset)?.explanation || "")}">${escapeHtml(launchDisplay(asset))}${basisBadge(launchRationale(asset))}</td>
      <td title="${escapeAttribute(asset.rationale?.clinical_differentiation?.explanation || "")}">${escapeHtml(asset.clinical_differentiation)}${basisBadge(asset.rationale?.clinical_differentiation)}</td>
      <td class="cost-cell" title="${escapeAttribute(asset.rationale?.annual_cost_range?.explanation || "")}"><span class="cost-value">${formatMoney(asset.estimated_annual_cost_low)} - ${formatMoney(asset.estimated_annual_cost_high)}</span>${basisBadge(asset.rationale?.annual_cost_range)}</td>
      <td title="${escapeAttribute(asset.rationale?.disruption_risk?.explanation || "")}"><span class="pill ${asset.disruption_risk.toLowerCase()}">${escapeHtml(asset.disruption_risk)}</span></td>
      <td>${escapeHtml(asset.recommended_action)}${basisBadge(asset.rationale?.recommended_action)}</td>
    </tr>
  `).join("");

  el.assetRows.querySelectorAll("tr").forEach((row) => {
    row.addEventListener("click", () => {
      state.selectedId = row.dataset.id;
      renderTable();
      renderDetail();
    });
  });
}

function renderDetail() {
  const asset = state.filtered.find((item) => item.asset_id === state.selectedId);
  if (!asset) {
    el.assetDetail.innerHTML = "<p>No asset selected.</p>";
    return;
  }

  el.assetDetail.innerHTML = `
    <h1>${escapeHtml(asset.asset_name)}</h1>
    <div class="detail-meta">
      <div><span>Manufacturer</span><strong>${escapeHtml(asset.manufacturer)}</strong></div>
      <div><span>Indication</span><strong>${escapeHtml(asset.indication)}</strong></div>
      <div><span>CT.gov studies</span><div class="nct-list">${renderCtgovLinks(asset)}</div></div>
      <div><span>Research status</span><strong>${escapeHtml(researchStatusLabel(asset))}</strong></div>
      <div><span>Mechanism</span><strong>${escapeHtml(asset.mechanism)}</strong></div>
      ${detailField("Expected launch", launchDisplay(asset), launchRationale(asset), asset)}
      ${detailField("Risk", asset.disruption_risk, asset.rationale?.disruption_risk, asset)}
      ${detailField("Recommended action", asset.recommended_action, asset.rationale?.recommended_action, asset)}
    </div>

    <section class="detail-section">
      ${sectionHeading("Clinical profile", asset.rationale?.clinical_differentiation, asset)}
      <p>${escapeHtml(asset.clinical_summary)}</p>
    </section>

    <section class="detail-section">
      ${sectionHeading("Estimated annual cost", asset.rationale?.annual_cost_range, asset)}
      <p>${formatMoney(asset.estimated_annual_cost_low)} - ${formatMoney(asset.estimated_annual_cost_high)}</p>
    </section>

    <section class="detail-section">
      ${sectionHeading("Budget impact level", asset.rationale?.budget_impact, asset)}
      <p>${escapeHtml(asset.budget_impact_level)}</p>
    </section>

    <section class="detail-section">
      <h3>Evidence gaps</h3>
      <ul>${(asset.evidence_gaps || []).map((gap) => `<li>${escapeHtml(gap)}</li>`).join("")}</ul>
    </section>

    <section class="detail-section">
      <h3>Management tools</h3>
      <p>${escapeHtml((asset.management_tools || []).join(", "))}</p>
    </section>

    <section class="detail-section">
      <h3>Source log</h3>
      <div class="source-list">
        ${renderSourceLog(asset)}
      </div>
    </section>

    <section class="detail-section">
      <h3>Research assignment</h3>
      <p>${escapeHtml(researchAssignmentText(asset))}</p>
    </section>

    <section class="detail-section">
      <h3>Traceability summary</h3>
      <ul class="trace-list">
        ${traceItem("Sponsor screen", asset.rationale?.sponsor_filter, asset)}
        ${traceItem("Therapeutic area", asset.rationale?.therapeutic_area, asset)}
        ${traceItem("Launch timeline", launchRationale(asset), asset)}
        ${traceItem("Annual cost", asset.rationale?.annual_cost_range, asset)}
        ${traceItem("Risk", asset.rationale?.disruption_risk, asset)}
        ${traceItem("Action", asset.rationale?.recommended_action, asset)}
      </ul>
    </section>
  `;
}

function renderCtgovLinks(asset) {
  const links = (asset.clinical_trial_links || asset.sources || []).filter((source) => /clinicaltrials\.gov\/study\/NCT|NCT\d{8}/i.test(`${source.url || ""} ${source.title || ""}`));
  if (!links.length) return "<span class=\"muted-link\">Not linked</span>";
  return links.map((source) => {
    const label = source.url?.match(/NCT\d{8}/i)?.[0] || source.title?.match(/NCT\d{8}/i)?.[0] || "CT.gov";
    return `<a class="nct-link" href="${escapeAttribute(source.url)}" target="_blank" rel="noreferrer">${escapeHtml(label)}</a>`;
  }).join(" ");
}

function detailField(label, value, rationale, asset) {
  return `<div>
    ${fieldHeading(label, rationale, asset)}
    <strong>${escapeHtml(value)}</strong>
  </div>`;
}

function fieldHeading(label, rationale, asset) {
  if (!rationale) return `<span class="field-label">${escapeHtml(label)}</span>`;
  return `<span class="field-label">${escapeHtml(label)}${basis(rationale, asset)}</span>`;
}

function sectionHeading(label, rationale, asset) {
  if (!rationale) return `<h3>${escapeHtml(label)}</h3>`;
  return `<h3>${escapeHtml(label)}${basis(rationale, asset)}</h3>`;
}

function sourceLabel(source) {
  const nct = source.url?.match(/NCT\d{8}/i)?.[0] || source.title?.match(/NCT\d{8}/i)?.[0];
  return nct ? `${nct} - ${source.title}` : source.title;
}

function renderSourceLog(asset) {
  return (asset.sources || []).map((source, index) => `
    <a href="${escapeAttribute(source.url)}" target="_blank" rel="noreferrer">
      <sup class="source-num">${index + 1}</sup>
      ${escapeHtml(sourceLabel(source))} (${escapeHtml(source.type)}; ${escapeHtml(source.date || "date not listed")})
    </a>
  `).join("");
}

function basis(rationale, asset) {
  if (!rationale) return "";
  return `<span class="basis-panel">
    <button class="basis-toggle" type="button" aria-expanded="false">Basis</button>
    <span class="basis">${escapeHtml(rationale.explanation || rationale.method || "")}${sourceCitationLinks(rationale, asset)}</span>
  </span>`;
}

function basisBadge(rationale) {
  if (!rationale?.basis_type) return "";
  return `<small class="basis-badge">${escapeHtml(basisTypeLabel(rationale))}</small>`;
}

function basisTypeLabel(rationale) {
  const labels = {
    source_direct: "Source-backed",
    source_derived: "Derived from sources",
    heuristic: "Heuristic estimate",
    seed_placeholder: "Seed placeholder"
  };
  return labels[rationale?.basis_type] || "Basis";
}

function sourceCitationLinks(rationale, asset) {
  const citations = citationsForRationale(rationale, asset);
  if (!citations.length) return rationale?.basis_type === "heuristic" ? " <span class=\"citations\">No direct source claim.</span>" : "";
  return ` <span class="citations">${citations.map((citation, index) => {
    const comma = index < citations.length - 1 ? "<sup>,</sup>" : "";
    const link = citation.url
      ? `<a href="${escapeAttribute(citation.url)}" target="_blank" rel="noreferrer" title="${escapeAttribute(citation.title)}"><sup>${citation.number}</sup></a>`
      : `<span title="${escapeAttribute(citation.title)}"><sup>${escapeHtml(citation.label)}</sup></span>`;
    return `${link}${comma}`;
  }).join("")}</span>`;
}

function researchStatusLabel(asset) {
  if (asset.research_status === "source_backed") {
    return asset.research_agent ? `Source-backed by subagent ${asset.research_agent}` : "Source-backed";
  }
  return "Pending asset-level subagent research";
}

function researchAssignmentText(asset) {
  if (asset.research_status === "source_backed") {
    return `Completed ${asset.research_checked_at || ""}. Detail estimates cite source references in the rationales above.`;
  }
  return "A research assignment has been generated for this asset. Until a subagent packet is added, planning estimates are labeled as heuristic and should not be treated as sourced facts.";
}

function traceItem(label, rationale, asset) {
  if (!rationale) return "";
  return `<li><strong>${escapeHtml(label)}:</strong> ${escapeHtml(basisTypeLabel(rationale))}. ${escapeHtml(rationale.method || "Method not documented")} - ${escapeHtml(rationale.explanation || "")}${sourceCitationLinks(rationale, asset)}</li>`;
}

function citationsForRationale(rationale, asset) {
  const refs = [
    ...(rationale?.source_refs || []),
    ...(rationale?.source_fields?.ctgov_urls || [])
  ];
  const seen = new Set();
  const citations = [];
  for (const ref of refs) {
    const key = String(ref || "").trim();
    if (!key || seen.has(key)) continue;
    seen.add(key);
    const match = findSourceForRef(key, asset);
    if (match) {
      citations.push({
        number: match.index + 1,
        title: sourceLabel(match.source),
        url: match.source.url
      });
    } else if (/^https?:\/\//i.test(key)) {
      citations.push({
        number: citations.length + 1,
        title: key,
        url: key
      });
    } else {
      citations.push({
        label: compactRefLabel(key),
        title: key
      });
    }
  }
  return citations;
}

function findSourceForRef(ref, asset) {
  const sources = asset?.sources || [];
  const normalizedRef = normalizeRef(ref);
  const nct = String(ref).match(/NCT\d{8}/i)?.[0]?.toUpperCase();
  return sources.map((source, index) => ({ source, index })).find(({ source }) => {
    const sourceId = normalizeRef(source.source_id || "");
    const sourceUrl = normalizeRef(source.url || "");
    const sourceTitle = normalizeRef(source.title || "");
    const sourceNct = `${source.url || ""} ${source.title || ""}`.match(/NCT\d{8}/i)?.[0]?.toUpperCase();
    return sourceId === normalizedRef || sourceUrl === normalizedRef || sourceTitle === normalizedRef || (nct && sourceNct === nct);
  });
}

function normalizeRef(value) {
  return String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, "");
}

function compactRefLabel(value) {
  const nct = String(value).match(/NCT\d{8}/i)?.[0];
  if (nct) return nct.toUpperCase();
  return String(value).replace(/^(ctgov|company|openfda|cost|label|payer|news|publication):/i, "").slice(0, 18);
}

function addOptions(select, options) {
  select.innerHTML = options.map((option) => `<option>${escapeHtml(option)}</option>`).join("");
}

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort();
}

function groupCount(rows, field) {
  return rows.reduce((acc, row) => {
    acc[row[field]] = (acc[row[field]] || 0) + 1;
    return acc;
  }, {});
}

function launchBucket(asset) {
  return asset.launch_timeline_bucket || bucketFromLaunchText(asset.expected_launch_window);
}

function launchDisplay(asset) {
  return asset.launch_timeline_display || asset.expected_launch_window || launchBucket(asset);
}

function launchRationale(asset) {
  return asset.rationale?.launch_timeline || asset.rationale?.expected_launch_window;
}

function bucketFromLaunchText(value) {
  const text = String(value || "");
  if (/^0-12 months$/i.test(text)) return "0-12 months";
  if (/^12-24 months$/i.test(text)) return "12-24 months";
  if (/^24-36 months$/i.test(text)) return "24-36 months";
  if (/^36\+ months$/i.test(text)) return "36+ months";
  const year = Number(text.match(/\b(20\d{2})\b/)?.[1]);
  if (!year) return "36+ months";
  const currentYear = new Date(state.data?.metadata?.generated_at || Date.now()).getFullYear();
  const months = (year - currentYear) * 12;
  if (months <= 12) return "0-12 months";
  if (months <= 24) return "12-24 months";
  if (months <= 36) return "24-36 months";
  return "36+ months";
}

function areaColor(area) {
  const colors = {
    Oncology: "var(--red)",
    Immunology: "var(--orange)",
    Cardiometabolic: "var(--blue)",
    Neurology: "var(--pink)",
    Hematology: "var(--lime)",
    Ophthalmology: "var(--gray)",
    Other: "#c8bca8"
  };
  return colors[area] || colors.Other;
}

function heatColor(count, budget) {
  if (!count) return "rgba(214, 208, 194, 0.62)";
  if (budget === "High") return count > 2 ? "var(--red)" : "rgba(255, 138, 118, 0.72)";
  if (budget === "Medium") return count > 2 ? "var(--orange)" : "rgba(255, 184, 107, 0.68)";
  return count > 2 ? "var(--blue)" : "rgba(184, 216, 255, 0.72)";
}

function formatMoney(value) {
  const number = Number(value || 0);
  if (number >= 1_000_000) return `$${(number / 1_000_000).toFixed(1)}M`;
  if (number >= 1_000) return `$${Math.round(number / 1_000)}K`;
  return `$${number.toLocaleString()}`;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[char]);
}

function escapeAttribute(value) {
  return escapeHtml(value).replace(/"/g, "&quot;");
}
