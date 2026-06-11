import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const runDir = path.join(root, "outputs", "botulinum_toxin_provider_lists_2026-06-04");
const outDir = path.join(root, "assets", "data");

const sources = [
  {
    key: "botox",
    product: "BOTOX Cosmetic",
    company: "AbbVie / Allergan Aesthetics",
    file: "botox_cosmetic_alle_providers.csv",
    cityField: "city",
    stateField: "state",
    zipField: "zip",
    latField: "latitude",
    lonField: "longitude",
    locatorUrl: "https://botoxcosmetic.alle.com/search",
  },
  {
    key: "dysport",
    product: "Dysport",
    company: "Ipsen / Galderma",
    file: "dysport_usa_providers.csv",
    cityField: "city",
    stateField: "state",
    zipField: "zip",
    latField: "latitude",
    lonField: "longitude",
    locatorUrl: "https://www.dysportusa.com/find-a-specialist",
  },
  {
    key: "xeomin",
    product: "Xeomin",
    company: "Merz Aesthetics",
    file: "xeomin_aesthetic_providers.csv",
    cityField: "city",
    stateField: "state",
    zipField: "zip",
    latField: "latitude",
    lonField: "longitude",
    locatorUrl: "https://www.xeominaesthetic.com/find-a-provider/",
  },
];

const stateNames = {
  AL: "Alabama", AK: "Alaska", AZ: "Arizona", AR: "Arkansas", CA: "California",
  CO: "Colorado", CT: "Connecticut", DE: "Delaware", DC: "District of Columbia",
  FL: "Florida", GA: "Georgia", HI: "Hawaii", ID: "Idaho", IL: "Illinois",
  IN: "Indiana", IA: "Iowa", KS: "Kansas", KY: "Kentucky", LA: "Louisiana",
  ME: "Maine", MD: "Maryland", MA: "Massachusetts", MI: "Michigan", MN: "Minnesota",
  MS: "Mississippi", MO: "Missouri", MT: "Montana", NE: "Nebraska", NV: "Nevada",
  NH: "New Hampshire", NJ: "New Jersey", NM: "New Mexico", NY: "New York",
  NC: "North Carolina", ND: "North Dakota", OH: "Ohio", OK: "Oklahoma",
  OR: "Oregon", PA: "Pennsylvania", RI: "Rhode Island", SC: "South Carolina",
  SD: "South Dakota", TN: "Tennessee", TX: "Texas", UT: "Utah", VT: "Vermont",
  VA: "Virginia", WA: "Washington", WV: "West Virginia", WI: "Wisconsin",
  WY: "Wyoming", PR: "Puerto Rico",
};

function readCsv(file) {
  const text = fs.readFileSync(path.join(runDir, file), "utf8").replace(/^\uFEFF/, "");
  const rows = [];
  let field = "";
  let row = [];
  let inQuotes = false;

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const next = text[i + 1];

    if (inQuotes) {
      if (char === '"' && next === '"') {
        field += '"';
        i += 1;
      } else if (char === '"') {
        inQuotes = false;
      } else {
        field += char;
      }
      continue;
    }

    if (char === '"') {
      inQuotes = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      field = "";
      row = [];
    } else {
      field += char;
    }
  }

  if (field.length || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }

  const [headers, ...dataRows] = rows.filter((csvRow) => csvRow.some((value) => value !== ""));
  return dataRows.map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index] || ""])));
}

function inc(map, key, amount = 1) {
  if (!key) return;
  map.set(key, (map.get(key) || 0) + amount);
}

function topEntries(map, limit = 12) {
  return [...map.entries()]
    .map(([key, count]) => ({ key, count }))
    .sort((a, b) => b.count - a.count || a.key.localeCompare(b.key))
    .slice(0, limit);
}

function toNumber(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
}

function summarizeSource(source) {
  const rows = readCsv(source.file);
  const stateCounts = new Map();
  const cityCounts = new Map();
  const zipCounts = new Map();
  const coordinates = [];
  const special = {};

  let withPhone = 0;
  let withWebsite = 0;
  let withReviewRating = 0;
  let financing = 0;
  let weekendOrExtended = 0;
  let aspire = 0;
  let specialistsNamed = 0;
  let xperiencePlus = 0;
  let prime = 0;

  for (const row of rows) {
    const state = String(row[source.stateField] || "").trim().toUpperCase();
    const city = String(row[source.cityField] || "").trim();
    const zip = String(row[source.zipField] || "").trim();
    const lat = toNumber(row[source.latField]);
    const lon = toNumber(row[source.lonField]);
    inc(stateCounts, state);
    inc(cityCounts, city && state ? `${city}, ${state}` : city);
    inc(zipCounts, zip.slice(0, 5));
    if (lat !== null && lon !== null) {
      coordinates.push([Number(lat.toFixed(4)), Number(lon.toFixed(4))]);
    }

    if (row.phone) withPhone += 1;
    if (row.website || row.practice_url) withWebsite += 1;
    if (row.google_reviews_rating) withReviewRating += 1;
    if (String(row.offers_financing).toLowerCase() === "true") financing += 1;
    if (/Open Saturday|Open Sunday|Extended Hours/i.test(row.indicators || "")) weekendOrExtended += 1;
    if (String(row.aspire).toLowerCase() === "true") aspire += 1;
    if ((row.specialists || row.providers_json || "").trim()) specialistsNamed += 1;
    if (/xperienceplus/i.test(row.brand_tiers || "")) xperiencePlus += 1;
    if (/\bprime\b/i.test(row.brand_tiers || "")) prime += 1;
  }

  if (source.key === "botox") {
    special.signals = [
      { label: "Offer financing", value: financing },
      { label: "Weekend or extended-hour indicators", value: weekendOrExtended },
      { label: "Google review rating exposed", value: withReviewRating },
    ];
  } else if (source.key === "dysport") {
    special.signals = [
      { label: "ASPIRE participation flag", value: aspire },
      { label: "Named specialist field populated", value: specialistsNamed },
      { label: "Phone number exposed", value: withPhone },
    ];
  } else if (source.key === "xeomin") {
    special.signals = [
      { label: "Xperience+ tier flag", value: xperiencePlus },
      { label: "Prime tier flag", value: prime },
      { label: "Named provider roster exposed", value: specialistsNamed },
    ];
  }

  return {
    ...source,
    csvPath: `outputs/botulinum_toxin_provider_lists_2026-06-04/${source.file}`,
    count: rows.length,
    statesCovered: stateCounts.size,
    citiesCovered: cityCounts.size,
    zipCodesCovered: zipCounts.size,
    withPhone,
    withWebsite,
    coordinates: coordinates.slice(0, 3000),
    stateCounts: topEntries(stateCounts, 60).map((entry) => ({
      state: entry.key,
      name: stateNames[entry.key] || entry.key,
      count: entry.count,
    })),
    topCities: topEntries(cityCounts, 12).map((entry) => ({
      city: entry.key,
      count: entry.count,
    })),
    topZips: topEntries(zipCounts, 10).map((entry) => ({
      zip: entry.key,
      count: entry.count,
    })),
    ...special,
  };
}

fs.mkdirSync(outDir, { recursive: true });

const products = sources.map(summarizeSource);
const allStates = [...new Set(products.flatMap((product) => product.stateCounts.map((row) => row.state)))].sort();
const stateComparison = allStates.map((state) => {
  const row = { state, name: stateNames[state] || state };
  for (const product of products) {
    row[product.key] = product.stateCounts.find((entry) => entry.state === state)?.count || 0;
  }
  row.total = sources.reduce((sum, source) => sum + row[source.key], 0);
  return row;
}).sort((a, b) => b.total - a.total || a.state.localeCompare(b.state));

const summary = {
  generatedAt: new Date().toISOString(),
  runDate: "2026-06-04",
  methodologyUrl: "outputs/botulinum_toxin_provider_lists_2026-06-04/source_and_methodology_notes.md",
  products,
  stateComparison,
};

fs.writeFileSync(path.join(outDir, "aesthetics_provider_summary.json"), JSON.stringify(summary, null, 2));
console.log(`Wrote ${path.join(outDir, "aesthetics_provider_summary.json")}`);
