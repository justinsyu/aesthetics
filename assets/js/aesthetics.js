const formatNumber = new Intl.NumberFormat("en-US");

const productClass = {
  botox: "product-botox",
  dysport: "product-dysport",
  xeomin: "product-xeomin",
};

const productColor = {
  botox: "#ea18a8",
  dysport: "#1c71ed",
  xeomin: "#00844f",
};

function number(value) {
  return formatNumber.format(value || 0);
}

function setHtml(id, html) {
  document.getElementById(id).innerHTML = html;
}

function renderSummary(products) {
  setHtml(
    "summary-cards",
    products
      .map(
        (product) => `
          <div class="${productClass[product.key]}">
            <strong>${product.product}</strong>
            <span>${number(product.count)}</span>
            <small>${product.company} | ${number(product.statesCovered)} states and territories | ${number(product.citiesCovered)} cities</small>
          </div>
        `,
      )
      .join(""),
  );
}

function renderCountBars(products) {
  const max = Math.max(...products.map((product) => product.count));
  setHtml(
    "count-bars",
    products
      .map((product) => {
        const width = Math.max(3, (product.count / max) * 100);
        return `
          <div class="count-row ${productClass[product.key]}">
            <div class="count-label">${product.product}</div>
            <div class="bar-track" aria-hidden="true"><div class="bar-fill" style="width:${width}%"></div></div>
            <div class="count-value">${number(product.count)}</div>
          </div>
        `;
      })
      .join(""),
  );
}

function coordinateToPoint(lat, lon) {
  const minLon = -126;
  const maxLon = -66;
  const minLat = 24;
  const maxLat = 50;
  return {
    x: ((lon - minLon) / (maxLon - minLon)) * 100,
    y: (1 - (lat - minLat) / (maxLat - minLat)) * 100,
  };
}

function renderMaps(products) {
  setHtml(
    "map-grid",
    products
      .map((product) => {
        const dots = product.coordinates
          .filter(([lat, lon]) => lat >= 24 && lat <= 50 && lon >= -126 && lon <= -66)
          .map(([lat, lon]) => {
            const point = coordinateToPoint(lat, lon);
            return `<span class="dot" style="left:${point.x}%; top:${point.y}%"></span>`;
          })
          .join("");
        return `
          <div class="mini-map ${productClass[product.key]}" role="img" aria-label="${product.product} provider coordinate sample">
            <h3>${product.product}</h3>
            ${dots}
          </div>
        `;
      })
      .join(""),
  );
}

function renderStates(data) {
  const rows = data.stateComparison.slice(0, 18);
  const max = Math.max(...rows.map((row) => row.total));
  setHtml(
    "state-comparison",
    rows
      .map((row) => {
        const botox = (row.botox / max) * 100;
        const dysport = (row.dysport / max) * 100;
        const xeomin = (row.xeomin / max) * 100;
        return `
          <div class="state-row">
            <div>
              <div class="state-name">${row.name}</div>
              <div class="state-counts">B ${number(row.botox)} | D ${number(row.dysport)} | X ${number(row.xeomin)}</div>
            </div>
            <div class="stacked-bar" aria-label="${row.name} total ${number(row.total)}">
              <span class="stack-botox" style="width:${botox}%"></span>
              <span class="stack-dysport" style="width:${dysport}%"></span>
              <span class="stack-xeomin" style="width:${xeomin}%"></span>
            </div>
          </div>
        `;
      })
      .join(""),
  );
}

function renderProductCards(products) {
  setHtml(
    "product-grid",
    products
      .map(
        (product) => `
          <article class="product-card ${productClass[product.key]}">
            <header>
              <div>
                <h3>${product.product}</h3>
                <p>${product.company}</p>
              </div>
              <span class="chip">${number(product.count)} records</span>
            </header>
            <div class="metric-pair">
              <div>
                <strong>${number(product.statesCovered)}</strong>
                <span>states and territories</span>
              </div>
              <div>
                <strong>${number(product.zipCodesCovered)}</strong>
                <span>ZIP codes represented</span>
              </div>
            </div>
            <div>
              <h3>Locator-specific signals</h3>
              <ul class="signal-list">
                ${product.signals
                  .map((signal) => `<li><span>${signal.label}</span><strong>${number(signal.value)}</strong></li>`)
                  .join("")}
              </ul>
            </div>
            <div>
              <h3>Top cities</h3>
              <ul class="city-list">
                ${product.topCities
                  .slice(0, 6)
                  .map((city) => `<li><span>${city.city}</span><strong>${number(city.count)}</strong></li>`)
                  .join("")}
              </ul>
            </div>
            <a href="${product.locatorUrl}">Open source locator</a>
          </article>
        `,
      )
      .join(""),
  );
}

function renderDownloads(data) {
  const productLinks = data.products.map(
    (product) => `
      <a href="${product.csvPath}">
        <strong>${product.product} CSV</strong>
        <span>${number(product.count)} rows | ${product.company}</span>
      </a>
    `,
  );
  productLinks.push(`
    <a href="${data.methodologyUrl}">
      <strong>Methodology notes</strong>
      <span>Source URLs, limitations, and reproducibility notes</span>
    </a>
  `);
  setHtml("download-list", productLinks.join(""));
}

async function init() {
  const response = await fetch("assets/data/aesthetics_provider_summary.json");
  if (!response.ok) throw new Error(`Summary fetch failed: ${response.status}`);
  const data = await response.json();
  renderSummary(data.products);
  renderCountBars(data.products);
  renderMaps(data.products);
  renderStates(data);
  renderProductCards(data.products);
  renderDownloads(data);
}

init().catch((error) => {
  console.error(error);
  document.body.classList.add("load-error");
  setHtml("summary-cards", `<div class="loading-card">Unable to load provider summary data</div>`);
});
