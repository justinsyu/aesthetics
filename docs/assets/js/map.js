const PRODUCTS = [
  {
    key: "botox",
    name: "BOTOX Cosmetic",
    company: "AbbVie / Allergan Aesthetics",
    file: "assets/data/botox_cosmetic_alle_providers.csv",
    color: "#1b60e9"
  },
  {
    key: "dysport",
    name: "Dysport",
    company: "Ipsen / Galderma",
    file: "assets/data/dysport_usa_providers.csv",
    color: "#6a97f1"
  },
  {
    key: "xeomin",
    name: "Xeomin",
    company: "Merz Aesthetics",
    file: "assets/data/xeomin_aesthetic_providers.csv",
    color: "#007247"
  }
];

const PRODUCT_BY_KEY = Object.fromEntries(PRODUCTS.map((product) => [product.key, product]));
const DEFAULT_BOUNDS = [[24.4, -124.9], [49.4, -66.9]];
const PAYMENT_OVERLAY_FILE = "assets/data/open_payments/provider_open_payments_overlay.json";

const state = {
  records: [],
  paymentOverlay: null,
  paymentLocations: {},
  showPayments: false,
  activeProducts: new Set(PRODUCTS.map((product) => product.key)),
  query: "",
  map: null,
  cluster: null,
  renderToken: 0
};

const statusEl = document.querySelector("[data-map-status]");
const countsEl = document.querySelector("[data-map-counts]");
const searchEl = document.querySelector("[data-map-search]");
const filterEl = document.querySelector("[data-product-filter]");
const paymentViewEl = document.querySelector("[data-payment-view]");
const resetEl = document.querySelector("[data-reset-map]");
const loadingEl = document.querySelector("[data-map-loading]");
let searchTimer;

init();

async function init() {
  renderProductFilters();
  initializeMap();
  setControlsDisabled(true);

  try {
    const [batches, paymentOverlay] = await Promise.all([
      Promise.all(PRODUCTS.map(loadProductRecords)),
      loadPaymentOverlay()
    ]);
    state.records = batches.flat();
    state.paymentOverlay = paymentOverlay;
    state.paymentLocations = paymentOverlay?.locations || {};
    applyFilters();
  } catch (error) {
    statusEl.textContent = "Unavailable";
    setControlsDisabled(false);
    setMapLoading(false);
    console.error(error);
  }

  const updateSearch = () => {
    state.query = searchEl.value.trim().toLowerCase();
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => applyFilters({ fit: true }), 180);
  };

  searchEl.addEventListener("input", updateSearch);
  searchEl.addEventListener("change", updateSearch);
  searchEl.addEventListener("search", updateSearch);

  filterEl.addEventListener("change", (event) => {
    const checkbox = event.target.closest("input[type='checkbox']");
    if (!checkbox) return;
    if (checkbox.checked) {
      state.activeProducts.add(checkbox.value);
    } else {
      state.activeProducts.delete(checkbox.value);
    }
    applyFilters({ fit: true });
  });

  paymentViewEl.addEventListener("change", () => {
    state.showPayments = paymentViewEl.checked;
    applyFilters();
  });

  resetEl.addEventListener("click", () => {
    const visible = getVisibleRecords();
    fitToRecords(visible);
  });
}

function initializeMap() {
  state.map = L.map("provider-map", {
    preferCanvas: true,
    minZoom: 3,
    maxZoom: 18,
    attributionControl: false
  }).fitBounds(DEFAULT_BOUNDS);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19
  }).addTo(state.map);

  state.cluster = createClusterLayer();

  state.map.addLayer(state.cluster);
}

function createClusterLayer() {
  return L.markerClusterGroup({
    chunkedLoading: true,
    maxClusterRadius: 48,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false
  });
}

function setControlsDisabled(disabled) {
  searchEl.disabled = disabled;
  resetEl.disabled = disabled;
  paymentViewEl.disabled = disabled;
  filterEl.querySelectorAll("input").forEach((input) => {
    input.disabled = disabled;
  });
}

async function loadPaymentOverlay() {
  const response = await fetch(PAYMENT_OVERLAY_FILE);
  if (!response.ok) {
    throw new Error(`Unable to load Open Payments overlay: ${response.status}`);
  }
  return response.json();
}

function setMapLoading(isLoading, message = "Loading map data") {
  if (!loadingEl) return;
  const textEl = loadingEl.querySelector("[data-map-loading-text]");
  if (textEl) textEl.textContent = message;
  loadingEl.classList.toggle("is-hidden", !isLoading);
}

function renderProductFilters() {
  filterEl.innerHTML = `<legend>Products</legend><div class="product-options">${PRODUCTS.map((product) => `
    <label>
      <input type="checkbox" value="${product.key}" checked>
      ${product.name}
    </label>
  `).join("")}</div>`;
}

function loadProductRecords(product) {
  statusEl.textContent = "Loading";

  return new Promise((resolve, reject) => {
    Papa.parse(product.file, {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const records = results.data
          .map((row, index) => normalizeRecord(product, row, index))
          .filter(Boolean);
        resolve(records);
      },
      error: reject
    });
  });
}

function normalizeRecord(product, row, index) {
  const latitude = Number(row.latitude);
  const longitude = Number(row.longitude);
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return null;

  const common = {
    id: `${product.key}-${row.id || row.account_id || row.provider_organization_id || index}`,
    productKey: product.key,
    productName: product.name,
    company: product.company,
    color: product.color,
    latitude,
    longitude,
    city: clean(row.city),
    state: clean(row.state),
    zip: clean(row.zip),
    phone: clean(row.phone),
    sourceUrl: clean(row.source_locator_url)
  };

  if (product.key === "botox") {
    return finishRecord(common, {
      name: clean(row.display_name),
      address1: clean(row.address1),
      address2: clean(row.address2),
      profileUrl: clean(row.profile_url),
      website: clean(row.profile_url),
      details: [
        row.practice_type && `Practice type: ${clean(row.practice_type).replaceAll("_", " ")}`,
        row.indicators && `Indicators: ${clean(row.indicators)}`,
        row.google_reviews_rating && `Google rating: ${clean(row.google_reviews_rating)}`
      ]
    });
  }

  if (product.key === "dysport") {
    return finishRecord(common, {
      name: clean(row.practice_name) || clean(row.specialists),
      clinician: clean(row.specialists) || [clean(row.first_name), clean(row.last_name)].filter(Boolean).join(" "),
      address1: clean(row.address),
      address2: clean(row.address_optional),
      website: clean(row.practice_url),
      details: [
        row.specialty && `Specialty: ${clean(row.specialty)}`,
        row.specialty_description && clean(row.specialty_description)
      ]
    });
  }

  return finishRecord(common, {
    name: clean(row.name) || clean(row.legal_account_name),
    clinician: providerNames(row.providers_json),
    address1: clean(row.street) || clean(row.address_text),
    address2: "",
    website: clean(row.website),
    details: [
      row.available_procedures && `Procedures: ${clean(row.available_procedures)}`,
      row.brands_listed_for && `Brands listed: ${clean(row.brands_listed_for)}`
    ]
  });
}

function finishRecord(common, productFields) {
  const address = [
    productFields.address1,
    productFields.address2,
    [common.city, common.state].filter(Boolean).join(", "),
    common.zip
  ].filter(Boolean).join(" ");

  const searchText = [
    common.productName,
    common.company,
    productFields.name,
    productFields.clinician,
    address,
    common.phone,
    common.zip
  ].filter(Boolean).join(" ").toLowerCase();

  return {
    ...common,
    ...productFields,
    address,
    searchText
  };
}

function applyFilters(options = {}) {
  const visible = getVisibleRecords();
  const renderToken = state.renderToken + 1;
  state.renderToken = renderToken;
  let progressSeen = false;
  let renderFinished = false;

  setControlsDisabled(true);
  setMapLoading(true, state.records.length ? "Rendering map data" : "Loading map data");
  state.cluster.clearLayers();

  const markers = visible.map((record) => {
    const payment = getPaymentLocation(record);
    const marker = L.marker([record.latitude, record.longitude], {
      icon: L.divIcon({
        className: "provider-dot-icon",
        html: renderMarkerDot(record, payment),
        iconSize: state.showPayments ? [paymentMarkerSize(payment), paymentMarkerSize(payment)] : [18, 18],
        iconAnchor: state.showPayments ? [paymentMarkerSize(payment) / 2, paymentMarkerSize(payment) / 2] : [9, 9]
      }),
      title: record.name
    });
    marker.bindPopup(renderPopup(record), { maxWidth: 340 });
    return marker;
  });

  const finishRender = () => {
    if (renderToken !== state.renderToken || renderFinished) return;
    renderFinished = true;
    updateCounts(visible);
    setControlsDisabled(false);
    setMapLoading(false);
  };

  if (!markers.length) {
    if (options.fit) {
      fitToRecords(visible);
    }
    countsEl.innerHTML = "";
    finishRender();
    return;
  }

  countsEl.innerHTML = "";
  statusEl.textContent = "Rendering";
  state.cluster.options.chunkProgress = (processed, total) => {
    if (renderToken !== state.renderToken) return;
    progressSeen = true;

    if (processed < total) {
      statusEl.textContent = "Rendering";
      return;
    }

    finishRender();
  };

  if (markers.length < 1000) {
    window.setTimeout(() => {
      if (!progressSeen) finishRender();
    }, 0);
  }

  if (options.fit) {
    fitToRecords(visible);
  }

  state.cluster.addLayers(markers);
}

function getVisibleRecords() {
  return state.records.filter((record) => {
    if (!state.activeProducts.has(record.productKey)) return false;
    if (!state.query) return true;
    return record.searchText.includes(state.query) || paymentSearchText(record).includes(state.query);
  });
}

function updateCounts(records) {
  const total = records.length.toLocaleString();
  statusEl.textContent = total;

  if (state.showPayments) {
    const paymentSummary = summarizePayments(records);
    countsEl.innerHTML = `
      <span class="map-count-pill">
        <strong>2024 Open Payments</strong>
        ${formatCurrency(paymentSummary.totalAmount)}
      </span>
      <span class="map-count-pill">${paymentSummary.paidLocations.toLocaleString()} paid locations</span>
      <span class="map-count-pill">${paymentSummary.matchedProviders.toLocaleString()} matched providers</span>
    `;
    return;
  }

  const counts = PRODUCTS.map((product) => ({
    ...product,
    count: records.filter((record) => record.productKey === product.key).length
  }));

  countsEl.innerHTML = counts.map((product) => `
    <span class="map-count-pill">
      <span class="map-count-swatch" style="--product-color:${product.color}"></span>
      <strong>${product.name}</strong>
      ${product.count.toLocaleString()}
    </span>
  `).join("");
}

function fitToRecords(records) {
  if (!records.length) {
    state.map.fitBounds(DEFAULT_BOUNDS);
    return;
  }

  const bounds = L.latLngBounds(records.map((record) => [record.latitude, record.longitude]));
  state.map.fitBounds(bounds.pad(0.08), { maxZoom: 12 });
}

function renderPopup(record) {
  const website = normalizeUrl(record.website);
  const profile = normalizeUrl(record.profileUrl);
  const details = (record.details || []).filter(Boolean);
  const payment = getPaymentLocation(record);
  const directLinks = [
    profile && `<p><a href="${escapeAttribute(profile)}" target="_blank" rel="noopener">Manufacturer profile</a></p>`,
    website && website !== profile && `<p><a href="${escapeAttribute(website)}" target="_blank" rel="noopener">Practice website</a></p>`
  ].filter(Boolean).join("");

  return `
    <article class="provider-popup">
      <div class="provider-product">
        <span class="map-count-swatch" style="--product-color:${record.color}"></span>
        ${escapeHtml(record.productName)}
      </div>
      <h3>${escapeHtml(record.name || "Listed provider")}</h3>
      ${record.clinician ? `<p>${escapeHtml(record.clinician)}</p>` : ""}
      ${record.address ? `<p>${escapeHtml(record.address)}</p>` : ""}
      ${record.phone ? `<p>${formatPhone(record.phone)}</p>` : ""}
      ${details.map((detail) => `<p>${escapeHtml(detail)}</p>`).join("")}
      ${renderPaymentSummary(payment)}
      ${directLinks}
    </article>
  `;
}

function getPaymentLocation(record) {
  return state.paymentLocations[record.id] || null;
}

function paymentSearchText(record) {
  const payment = getPaymentLocation(record);
  if (!payment) return "";
  return (payment.providers || []).map((provider) => [
    provider.name,
    provider.rawName,
    provider.npi,
    provider.nppesName,
    provider.openPaymentsName,
    provider.taxonomy
  ].filter(Boolean).join(" ")).join(" ").toLowerCase();
}

function summarizePayments(records) {
  return records.reduce((summary, record) => {
    const payment = getPaymentLocation(record);
    if (!payment) return summary;
    const total = Number(payment.payment_total_2024) || 0;
    summary.totalAmount += total;
    summary.matchedProviders += Number(payment.matched_provider_count) || 0;
    if (total > 0) summary.paidLocations += 1;
    return summary;
  }, { totalAmount: 0, paidLocations: 0, matchedProviders: 0 });
}

function paymentMarkerSize(payment) {
  const total = Number(payment?.payment_total_2024) || 0;
  if (!state.showPayments) return 18;
  if (!total) return 12;
  return Math.min(34, Math.max(14, 10 + Math.log10(total + 10) * 4.8));
}

function paymentMarkerColor(payment) {
  const total = Number(payment?.payment_total_2024) || 0;
  if (!total) return "#94a3b8";
  if (total >= 100000) return "#7c2d12";
  if (total >= 25000) return "#b45309";
  if (total >= 5000) return "#d97706";
  if (total >= 1000) return "#0f766e";
  return "#0891b2";
}

function renderMarkerDot(record, payment) {
  if (!state.showPayments) {
    return `<span class="provider-dot" style="--product-color:${record.color}"></span>`;
  }
  const size = paymentMarkerSize(payment);
  const color = paymentMarkerColor(payment);
  return `<span class="provider-dot payment-dot" style="--payment-size:${size}px;--payment-color:${color}"></span>`;
}

function renderPaymentSummary(payment) {
  if (!payment || !payment.candidate_count) {
    return `
      <div class="payment-popup-summary">
        <p><strong>Open Payments:</strong> no individual clinician name available for NPI matching in this locator row.</p>
      </div>
    `;
  }

  const total = Number(payment.payment_total_2024) || 0;
  const providers = (payment.providers || []).slice(0, 5);
  const providerItems = providers.map((provider) => `
    <li>
      ${escapeHtml(provider.name)}
      ${provider.npi ? ` · NPI ${escapeHtml(provider.npi)}` : ""}
      · ${formatCurrency(provider.paymentTotal2024 || 0)}
      ${provider.npiConfidence ? ` · ${escapeHtml(provider.npiConfidence)} confidence` : ""}
    </li>
  `).join("");

  return `
    <div class="payment-popup-summary">
      <p><strong>2024 Open Payments:</strong> ${formatCurrency(total)} across ${(payment.payment_transactions_2024 || 0).toLocaleString()} transactions.</p>
      <p>${(payment.matched_provider_count || 0).toLocaleString()} of ${(payment.candidate_count || 0).toLocaleString()} listed clinician names matched to an NPI.</p>
      ${providerItems ? `<ol class="payment-provider-list">${providerItems}</ol>` : ""}
    </div>
  `;
}

function clean(value) {
  return String(value || "").trim();
}

function providerNames(value) {
  if (!value) return "";
  try {
    return Object.values(JSON.parse(value)).join("; ");
  } catch {
    return "";
  }
}

function normalizeUrl(value) {
  const url = clean(value);
  if (!url) return "";
  if (/^https?:\/\//i.test(url)) return url;
  if (/^[\w.-]+\.[a-z]{2,}/i.test(url)) return `https://${url}`;
  return "";
}

function formatPhone(value) {
  const phone = clean(value);
  const digits = phone.replace(/\D/g, "");
  if (digits.length === 10) {
    return `${digits.slice(0, 3)}-${digits.slice(3, 6)}-${digits.slice(6)}`;
  }
  return escapeHtml(phone);
}

function formatCurrency(value) {
  return Number(value || 0).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0
  });
}

function escapeHtml(value) {
  return clean(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value);
}
