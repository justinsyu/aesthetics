const ALL_ROLES = "All";
const ALL_TRACKS = "All conference tracks";
const PAGE_SIZE = 100;

const state = {
  data: null,
  selectedAbstract: null,
  activeRole: ALL_ROLES,
  activeTrack: ALL_TRACKS,
  search: "",
  renderedCount: PAGE_SIZE,
  dataMode: "Fallback data",
};

let syncNavigationState = () => {};

const fallbackData = {
  generatedAtUtc: "2026-05-27T00:00:00Z",
  dataset: {
    name: "ASCO 2026 abstracts",
    records: 7295,
    sourcePage: "https://www.asco.org/annual-meeting/search?filters=%7B%22mediaTypes%22:%5B%22Abstracts%22%5D%7D&userInput=&sortBy=Relevancy&contentKey=ANNUAL_MEETING&contentKeyYear=2026",
    downloadedAtUtc: "2026-05-27T17:08:46Z",
  },
  metrics: [
    { label: "Abstract records", value: 7295, tone: "lime" },
    { label: "With HTML tables", value: 1709, tone: "blue" },
    { label: "Late-breaking", value: 60, tone: "orange" },
    { label: "Role classifications", value: 5, tone: "pink" },
  ],
  sessionTypes: [],
  tracks: [],
  prioritySignals: [],
  abstracts: [],
  audienceWorkspaces: [],
  workflow: [],
  sources: [],
};

function formatNumber(value) {
  if (typeof value === "number") return value.toLocaleString("en-US");
  const numeric = Number(String(value ?? "").replaceAll(",", ""));
  return Number.isFinite(numeric) ? numeric.toLocaleString("en-US") : String(value ?? "");
}

function shortDate(value) {
  if (!value) return "Not recorded";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function toneClass(tone) {
  return ["lime", "blue", "orange", "pink"].includes(tone) ? tone : "gray";
}

function normalizeDisplayText(value) {
  return String(value ?? "")
    .replace(/<\/?(em|i|strong|b|sup|sub)\b[^>]*>/gi, "")
    .replace(/<\/?[a-z][a-z0-9-]*(?:\s[^>]*)?>/gi, "")
    .replace(/\u2014/g, ": ")
    .replace(/[\u2013\u2011]/g, "-")
    .replace(/\s+/g, " ")
    .trim();
}

function normalizeTitle(value) {
  return normalizeDisplayText(value).replace(/\.$/, "");
}

function buildRecordSearchText(record) {
  return [
    record.title,
    record.abstractNumber,
    record.contentId,
    record.track,
    record.sessionType,
    record.speaker,
    record.primaryRole,
    ...(record.roles || []),
    ...(record.tags || []),
    record.summary,
    ...Object.values(record.sections || {}),
  ]
    .map(normalizeDisplayText)
    .join(" ")
    .toLowerCase();
}

function normalizeAbstract(record, index) {
  const roles = (record.roles || record.recommendedRoles || record.audience || [])
    .map(normalizeDisplayText)
    .filter(Boolean);
  const normalized = {
    uid: normalizeDisplayText(record.uid || record.id || record.contentId || `abstract-${index}`),
    contentId: normalizeDisplayText(record.contentId),
    abstractNumber: normalizeDisplayText(record.abstractNumber),
    title: normalizeTitle(record.title || "Untitled abstract"),
    speaker: normalizeDisplayText(record.speaker || record.primaryPerson || ""),
    track: normalizeDisplayText(record.track || "Publication only"),
    sessionType: normalizeDisplayText(record.sessionType || "Session not listed"),
    url: record.url || record.sourceUrl || "",
    score: record.score || record.priorityScore || 0,
    primaryRole: normalizeDisplayText(record.primaryRole || roles[0] || "Unclassified"),
    roles,
    roleScores: record.roleScores || record.roleRelevance || {},
    tags: (record.tags || record.evidenceTags || [record.risk, record.confidence].filter(Boolean))
      .map(normalizeDisplayText)
      .filter(Boolean),
    summary: normalizeDisplayText(record.summary || ""),
    sections: Object.fromEntries(
      Object.entries(record.sections || {})
        .map(([key, value]) => [key, normalizeDisplayText(value)])
        .filter(([, value]) => value),
    ),
    tableCount: record.tableCount || 0,
  };
  return {
    ...normalized,
    searchText: buildRecordSearchText(normalized),
  };
}

function deriveTracks(abstracts) {
  const counts = new Map();
  abstracts.forEach((abstract) => {
    const track = abstract.track || "Publication only";
    counts.set(track, (counts.get(track) || 0) + 1);
  });
  return [...counts.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
}

function normalizeWorkspace(workspace, abstracts) {
  const name = normalizeDisplayText(workspace.name);
  const roleMatches = abstracts.filter((abstract) => abstract.roles.includes(name) || abstract.primaryRole === name);
  const topSignals = (workspace.topSignals && workspace.topSignals.length ? workspace.topSignals : roleMatches.slice(0, 6))
    .map(normalizeAbstract);

  return {
    name,
    count: roleMatches.length,
    sampleCount: workspace.sampleCount || workspace.sample_count || topSignals.length,
    countLabel: normalizeDisplayText(workspace.countLabel || workspace.count_label || "matching abstracts"),
    description: normalizeDisplayText(workspace.description || workspace.objective || ""),
    topSignals,
  };
}

async function loadData() {
  if (window.ASCO_DASHBOARD_DATA) {
    state.dataMode = "Generated data";
    return normalizeData(window.ASCO_DASHBOARD_DATA);
  }

  const sources = [
    { url: "generated_data/dashboard_data.json", mode: "Generated data" },
    { url: "data/dashboard-data.json", mode: "Seed data" },
  ];

  for (const source of sources) {
    try {
      const response = await fetch(source.url, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      state.dataMode = source.mode;
      return normalizeData(await response.json());
    } catch (error) {
      console.warn(`Unable to load ${source.url}`, error);
    }
  }

  state.dataMode = "Fallback data";
  return normalizeData(fallbackData);
}

function normalizeData(data) {
  const sourceAbstracts = data.abstracts && data.abstracts.length ? data.abstracts : data.prioritySignals || [];
  const abstracts = sourceAbstracts.map(normalizeAbstract);
  const tracks = deriveTracks(abstracts);

  return {
    ...fallbackData,
    ...data,
    dataset: { ...fallbackData.dataset, ...data.dataset },
    metrics: (data.metrics || fallbackData.metrics).map((metric) => ({
      label: normalizeDisplayText(metric.label),
      value: metric.value,
      tone: metric.tone || "gray",
    })),
    sessionTypes: (data.sessionTypes || []).map((row) => ({
      name: normalizeDisplayText(row.name || row.label),
      count: row.count || row.value || 0,
    })),
    tracks,
    prioritySignals: (data.prioritySignals || []).map(normalizeAbstract),
    abstracts,
    audienceWorkspaces: (data.audienceWorkspaces || []).map((workspace) => normalizeWorkspace(workspace, abstracts)),
    workflow: (data.workflow || []).map((step) => ({
      ...step,
      name: normalizeDisplayText(step.name || step.title),
      status: normalizeDisplayText(step.status || "planned"),
      description: normalizeDisplayText(step.description || step.body || ""),
    })),
    sources: (data.sources || []).map((source) => ({
      ...source,
      name: normalizeDisplayText(source.name || source.label),
      type: normalizeDisplayText(source.type || "Source"),
      url: source.url || data.dataset?.sourcePage || "",
      status: normalizeDisplayText(source.status),
    })),
  };
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderMetrics(data) {
  const metrics = document.querySelector("#hero-metrics");
  metrics.innerHTML = data.metrics
    .map(
      (metric) => `
        <div class="metric-card" data-tone="${toneClass(metric.tone)}">
          <strong>${formatNumber(metric.value)}</strong>
          <span>${escapeHtml(metric.label)}</span>
        </div>
      `,
    )
    .join("");
  const railRecordCount = document.querySelector("#rail-record-count");
  const railSourceStatus = document.querySelector("#rail-source-status");
  if (railRecordCount) railRecordCount.textContent = formatNumber(data.dataset.records);
  if (railSourceStatus) railSourceStatus.textContent = "ASCO source records";
  document.querySelector("#data-updated").textContent = `Updated ${shortDate(data.generatedAtUtc)}`;
}

function renderBars(selector, rows, nameKey = "name") {
  const node = document.querySelector(selector);
  const max = Math.max(...rows.map((row) => row.count), 1);
  node.innerHTML = rows
    .map(
      (row) => `
        <div class="bar-row">
          <b>${escapeHtml(row[nameKey])}</b>
          <span class="bar-track"><span class="bar-fill" style="width:${(row.count / max) * 100}%"></span></span>
          <span>${formatNumber(row.count)}</span>
        </div>
      `,
    )
    .join("");
}

function renderTracks(data) {
  const node = document.querySelector("#track-list");
  const rows = [{ name: ALL_TRACKS, count: data.abstracts.length }, ...data.tracks];
  node.innerHTML = rows
    .map(
      (track) => `
        <button class="track-item ${state.activeTrack === track.name ? "is-active" : ""}" type="button" data-track="${escapeHtml(track.name)}">
          <b>${escapeHtml(track.name || "Publication only")}</b>
          <span>${formatNumber(track.count)}</span>
        </button>
      `,
    )
    .join("");

  node.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeTrack = button.dataset.track;
      resetReviewWindow();
      renderTracks(state.data);
      renderReview(state.data);
      document.querySelector("#abstracts")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
}

function roles(data) {
  return [ALL_ROLES, ...data.audienceWorkspaces.map((workspace) => workspace.name)];
}

function renderRoleFilters(data) {
  const node = document.querySelector("#audience-filters");
  node.innerHTML = roles(data)
    .map(
      (role) => `
        <button class="role-filter ${state.activeRole === role ? "is-active" : ""}" type="button" data-role="${escapeHtml(role)}">
          ${escapeHtml(role)}
        </button>
      `,
    )
    .join("");
  node.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeRole = button.dataset.role;
      resetReviewWindow();
      renderRoleFilters(state.data);
      renderReview(state.data);
    });
  });
}

function resetReviewWindow() {
  state.renderedCount = PAGE_SIZE;
  state.selectedAbstract = null;
}

function filteredAbstracts(data) {
  const query = state.search.trim().toLowerCase();
  return data.abstracts.filter((abstract) => {
    const roleMatch =
      state.activeRole === ALL_ROLES ||
      abstract.roles.includes(state.activeRole) ||
      abstract.primaryRole === state.activeRole;
    const trackMatch = state.activeTrack === ALL_TRACKS || abstract.track === state.activeTrack;
    const searchMatch = !query || abstract.searchText.includes(query);
    return roleMatch && trackMatch && searchMatch;
  });
}

function renderReview(data, options = {}) {
  const matches = filteredAbstracts(data);
  const shown = matches.slice(0, state.renderedCount);
  const list = document.querySelector("#signal-list");
  const resultCount = document.querySelector("#signal-result-count");
  const previousScrollTop = list.scrollTop;

  resultCount.textContent = `${formatNumber(shown.length)} of ${formatNumber(matches.length)} matching abstracts shown`;

  if (matches.length === 0) {
    state.selectedAbstract = null;
    list.innerHTML = `
      <div class="empty-state">
        <strong>No matching abstracts</strong>
        <span>Clear the search field or choose different role and conference track filters.</span>
      </div>
    `;
    renderDetail();
    return;
  }

  if (!state.selectedAbstract || !matches.some((abstract) => abstract.uid === state.selectedAbstract.uid)) {
    state.selectedAbstract = matches[0];
  }

  list.innerHTML = shown
    .map(
      (abstract) => `
        <button class="signal-item ${state.selectedAbstract?.uid === abstract.uid ? "is-selected" : ""}" type="button" data-uid="${escapeHtml(abstract.uid)}">
          <span class="signal-title">${escapeHtml(abstract.title)}</span>
          <span class="signal-meta">
            <span class="score-chip">${escapeHtml(abstract.score)}</span>
            <span>${escapeHtml(abstract.abstractNumber || "No ID")}</span>
            <span>${escapeHtml(abstract.sessionType)}</span>
            <span>${escapeHtml(abstract.primaryRole)}</span>
            <span>${escapeHtml(abstract.track)}</span>
          </span>
        </button>
      `,
    )
    .join("");

  list.querySelectorAll(".signal-item").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedAbstract = data.abstracts.find((abstract) => abstract.uid === button.dataset.uid);
      renderReview(data, { preserveScroll: true });
      revealDetailOnSmallScreen();
    });
  });

  if (options.preserveScroll) list.scrollTop = previousScrollTop;
  renderDetail();
  syncNavigationState();
}

function appendMoreRecords() {
  if (!state.data) return;
  const matches = filteredAbstracts(state.data);
  if (state.renderedCount >= matches.length) return;
  state.renderedCount = Math.min(state.renderedCount + PAGE_SIZE, matches.length);
  renderReview(state.data, { preserveScroll: true });
}

function revealDetailOnSmallScreen() {
  if (!window.matchMedia("(max-width: 1120px)").matches) return;
  document.querySelector(".detail-panel")?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
}

function renderDetail() {
  const node = document.querySelector("#signal-detail");
  const abstract = state.selectedAbstract;
  if (!abstract) {
    node.innerHTML = "<p>No matching abstracts.</p>";
    return;
  }
  const sectionLabels = {
    background: "Background",
    methods: "Methods",
    results: "Results",
    conclusions: "Conclusions",
  };
  const sectionEntries = Object.entries(sectionLabels)
    .map(([key, label]) => ({ label, text: abstract.sections?.[key] || "" }))
    .filter((section) => section.text);
  const abstractBody = sectionEntries.length
    ? sectionEntries
        .map(
          (section) => `
            <section class="abstract-section-block">
              <h4>${escapeHtml(section.label)}</h4>
              <p>${escapeHtml(section.text)}</p>
            </section>
          `,
        )
        .join("")
    : `<p class="signal-summary">${escapeHtml(abstract.summary || "No abstract body available; open the ASCO source for the full abstract text.")}</p>`;

  node.innerHTML = `
    <p class="section-label">Selected ASCO abstract</p>
    <h3>${escapeHtml(abstract.title)}</h3>
    <div class="abstract-body">${abstractBody}</div>
    <div class="tag-row">
      <span class="tag-chip">${escapeHtml(abstract.abstractNumber || "No ID")}</span>
      <span class="tag-chip">Content ${escapeHtml(abstract.contentId || "not listed")}</span>
      <span class="tag-chip">${escapeHtml(abstract.sessionType)}</span>
      <span class="tag-chip">${formatNumber(abstract.tableCount)} tables</span>
      ${(abstract.roles || []).slice(0, 4).map((role) => `<span class="tag-chip">${escapeHtml(role)}</span>`).join("")}
      ${(abstract.tags || []).slice(0, 4).map((tag) => `<span class="tag-chip">${escapeHtml(tag)}</span>`).join("")}
    </div>
    <p class="signal-meta"><b>Track:</b> ${escapeHtml(abstract.track || "Publication only")}</p>
    <p class="signal-meta"><b>Speaker:</b> ${escapeHtml(abstract.speaker || "Not listed")}</p>
    <a class="detail-link" href="${escapeHtml(abstract.url || "#")}" target="_blank" rel="noreferrer">View on ASCO</a>
  `;
}

function renderWorkflow(data) {
  const node = document.querySelector("#workflow-steps");
  node.innerHTML = data.workflow
    .map(
      (step) => `
        <article class="workflow-item">
          <span class="workflow-status" data-status="${escapeHtml(step.status)}">${escapeHtml(step.status)}</span>
          <h3>${escapeHtml(step.name)}</h3>
          <p>${escapeHtml(step.description)}</p>
        </article>
      `,
    )
    .join("");
}

function bindControls() {
  document.querySelector("#signal-search").addEventListener("input", (event) => {
    state.search = event.target.value;
    resetReviewWindow();
    renderReview(state.data);
  });

  document.querySelector("#signal-list").addEventListener("scroll", (event) => {
    const list = event.currentTarget;
    if (list.scrollTop + list.clientHeight >= list.scrollHeight - 180) {
      appendMoreRecords();
    }
  }, { passive: true });

}

function bindNavigation() {
  const navItems = [...document.querySelectorAll('.nav-item[href^="#"]')];
  if (!navItems.length) return;
  const sections = navItems
    .map((item) => document.querySelector(item.getAttribute("href")))
    .filter(Boolean);
  let scrollFrame = null;

  function setActiveNav(sectionId) {
    navItems.forEach((item) => {
      item.classList.toggle("is-active", item.getAttribute("href") === `#${sectionId}`);
    });
  }

  function activeSectionFromScroll() {
    const anchorOffset = 140;
    const hashId = decodeURIComponent(window.location.hash.replace("#", ""));
    const hashedSection = sections.find((section) => section.id === hashId);
    if (hashedSection) {
      const hashedRect = hashedSection.getBoundingClientRect();
      if (hashedRect.top >= -24 && hashedRect.top < window.innerHeight * 0.92) {
        return hashedSection.id;
      }
    }

    let current = sections[0]?.id;
    let nearestDistance = Number.POSITIVE_INFINITY;

    sections.forEach((section) => {
      const rect = section.getBoundingClientRect();
      if (rect.top <= anchorOffset && rect.bottom > anchorOffset) {
        current = section.id;
        nearestDistance = 0;
        return;
      }

      const distance = Math.abs(rect.top - anchorOffset);
      if (distance < nearestDistance && rect.bottom > 0) {
        nearestDistance = distance;
        current = section.id;
      }
    });

    return current;
  }

  function syncActiveNav() {
    const hashId = window.location.hash.replace("#", "");
    const hashedSection = sections.find((section) => section.id === hashId);
    setActiveNav(hashedSection?.id || activeSectionFromScroll());
  }

  function syncActiveNavOnScroll() {
    if (scrollFrame) return;
    scrollFrame = window.requestAnimationFrame(() => {
      scrollFrame = null;
      setActiveNav(activeSectionFromScroll());
    });
  }

  navItems.forEach((item) => {
    item.addEventListener("click", () => {
      const section = document.querySelector(item.getAttribute("href"));
      if (section) setActiveNav(section.id);
    });
  });

  window.addEventListener("hashchange", syncActiveNav);
  window.addEventListener("scroll", syncActiveNavOnScroll, { passive: true });
  window.addEventListener("resize", syncActiveNavOnScroll);
  syncNavigationState = syncActiveNav;
  syncActiveNav();
}

function renderAll() {
  renderMetrics(state.data);
  renderBars("#session-stack", state.data.sessionTypes);
  renderTracks(state.data);
  renderRoleFilters(state.data);
  renderReview(state.data);
  renderWorkflow(state.data);
}

async function init() {
  bindControls();
  bindNavigation();
  state.data = await loadData();
  renderAll();
}

init();
