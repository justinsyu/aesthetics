const formatNumber = new Intl.NumberFormat("en-US");

const productLabels = {
  botox: "BOTOX",
  dysport: "Dysport",
  xeomin: "Xeomin",
};

function number(value) {
  return formatNumber.format(value || 0);
}

function productColor(key) {
  return {
    botox: "#1c71ed",
    dysport: "#76a6eb",
    xeomin: "#00844f",
  }[key] || "#06254a";
}

function renderProducts(summary) {
  const max = Math.max(...summary.products.map((product) => product.providerCount));
  const container = document.querySelector("[data-products]");
  container.innerHTML = summary.products.map((product) => {
    const width = Math.max(4, Math.round((product.providerCount / max) * 100));
    return `
      <article class="product-card" data-product="${product.key}">
        <h3>${product.name}</h3>
        <p class="product-meta">${product.company}</p>
        <div class="big-number">${number(product.providerCount)}</div>
        <div class="bar-shell" aria-hidden="true">
          <div class="bar-fill" style="width:${width}%; background:${product.color};"></div>
        </div>
        <div class="metric-row">
          <span><b>${number(product.stateCount)}</b> states / territories</span>
          <span><b>${number(product.zipCount)}</b> ZIP codes</span>
        </div>
      </article>
    `;
  }).join("");
}

function renderStateDensity(summary) {
  const rows = summary.comparisonByState.slice(0, 18);
  const max = Math.max(...rows.map((row) => row.total));
  const bars = document.querySelector("[data-state-bars]");
  bars.innerHTML = rows.map((row) => {
    const width = Math.round((row.total / max) * 100);
    const botox = (row.botox / row.total) * 100;
    const dysport = (row.dysport / row.total) * 100;
    const xeomin = (row.xeomin / row.total) * 100;
    return `
      <div class="state-row">
        <span class="state-label">${row.state}</span>
        <span class="state-bar-track" title="${row.state}: ${number(row.total)} rows">
          <span class="stacked" style="width:${width}%">
            <span style="width:${botox}%; background:${productColor("botox")}"></span>
            <span style="width:${dysport}%; background:${productColor("dysport")}"></span>
            <span style="width:${xeomin}%; background:${productColor("xeomin")}"></span>
          </span>
        </span>
        <span class="state-total">${number(row.total)}</span>
      </div>
    `;
  }).join("");

  document.querySelector("[data-state-table]").innerHTML = rows.map((row) => `
    <tr>
      <td>${row.state}</td>
      <td>${number(row.total)}</td>
      <td>${number(row.botox)}</td>
      <td>${number(row.dysport)}</td>
      <td>${number(row.xeomin)}</td>
    </tr>
  `).join("");
}

function renderMarkets(summary) {
  const container = document.querySelector("[data-market-grid]");
  container.innerHTML = summary.products.map((product) => `
    <article class="market-card">
      <h3>${product.name}</h3>
      <div class="market-list">
        ${product.topCities.slice(0, 10).map((city) => `
          <div class="market-item">
            <span class="market-name">${city.name}</span>
            <span class="market-count">${number(city.count)}</span>
          </div>
        `).join("")}
      </div>
    </article>
  `).join("");
}

function renderSources(summary) {
  const sourceList = document.querySelector("[data-source-list]");
  sourceList.innerHTML = summary.products.map((product) => `
    <div class="source-item">
      <strong>${product.name}</strong><br>
      ${number(product.providerCount)} public locator rows. Source CSV: <a href="${product.file}">${product.file.split("/").pop()}</a>
    </div>
  `).join("") + `
    <div class="source-item">
      DAXXIFY and Jeuveau were investigated separately. DAXXIFY remained rate-limited during retry; Jeuveau required browser-origin requests and is not included in these three-product infographics.
    </div>
  `;
}

async function init() {
  const response = await fetch("assets/data/provider-summary.json");
  const summary = await response.json();
  document.querySelector("[data-total-providers]").textContent = number(summary.nationalTotals.providers);
  document.querySelector("[data-total-products]").textContent = number(summary.nationalTotals.products);
  document.querySelector("[data-total-states]").textContent = number(summary.nationalTotals.states);
  renderProducts(summary);
  renderStateDensity(summary);
  renderMarkets(summary);
  renderSources(summary);
}

init().catch((error) => {
  document.body.insertAdjacentHTML("beforeend", `<pre>${error.message}</pre>`);
});
