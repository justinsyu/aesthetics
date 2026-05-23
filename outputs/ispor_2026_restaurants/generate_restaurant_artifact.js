const fs = require("fs");
const path = require("path");

const outDir = "/Users/justinyu/Desktop/linkedin-posts/outputs/ispor_2026_restaurants";
const rawFeed = JSON.parse(fs.readFileSync(path.join(outDir, "google_maps_search_feed_raw.json"), "utf8"));

const conventionCenter = { lat: 39.953573, lon: -75.160616 };
const WALKING_RADIUS_MI = 0.75;

const enrichment = {
  "reading terminal market": { reviews: "45,706", price: "$$", dist: "0.04", category: "Market", description: "Historic hub for eclectic foods & goods" },
  "dutch eating place": { reviews: "1,056", price: "$10-20", dist: "0.04", category: "Pennsylvania Dutch restaurant", description: "Pennsylvania Dutch breakfasts & lunches" },
  "down home diner": { reviews: "6,457", price: "$10-20", dist: "0.06", category: "Breakfast restaurant", description: "Southern-inspired homestyle cooking" },
  "maggiano's little italy": {
    reviews: "5,001",
    price: "$20-60",
    dist: "0.08",
    category: "Italian restaurant",
    description: "Semi-upscale chain for classic Italian fare served family-style in a relaxed, polished space",
    sun: "11:15 AM-10 PM",
    mon: "11:15 AM-10 PM",
    tue: "11:15 AM-10 PM",
    wed: "11:15 AM-10 PM",
    popular: "Sun 6 PM 42%; Mon 6 PM 46%; Tue 7 PM 56%; Wed 7 PM 48%",
    scope: "Google Maps detail panel verified for Sun-Wed hours and Popular Times"
  },
  "hard rock cafe": { reviews: "5,196", price: "$20-30", dist: "0.11", category: "American restaurant", description: "Music-themed chain with an American menu" },
  "iron hill brewery & restaurant - center city": { reviews: "3,028", price: "$20-30", dist: "0.14", category: "Brewpub", description: "Microbrews & comfort food classics", address: "1150 Market St" },
  "bank & bourbon": { reviews: "904", price: "$$$", dist: "0.16", category: "Bar", description: "Farm-to-fork American restaurant & bar" },
  "the wayward": { reviews: "236", price: "$$", dist: "0.19", category: "Restaurant", description: "Seafood plates in a stylish eatery", address: "1170 Ludlow St" },
  "terakawa ramen": { reviews: "3,904", price: "$20-30", dist: "0.26", category: "Ramen restaurant", description: "Cool find for bespoke Japanese noodles" },
  "fogo de chao brazilian steakhouse": { reviews: "8,202", price: "$50-100", dist: "0.29", category: "Brazilian restaurant", description: "Upmarket Brazilian churrascaria", address: "1337 Chestnut St", status: "Closed - Opens 11:30 AM" },
  "sang kee peking duck house": { reviews: "2,311", price: "$20-30", dist: "0.31", category: "Chinese restaurant", description: "No-frills landmark for Chinese cuisine" },
  "barbuzzo": { reviews: "2,270", price: "$20-60", dist: "0.31", category: "Mediterranean restaurant", description: "Mediterranean spot with a locavore slant" },
  "el purepecha": { reviews: "895", price: "$20-30", dist: "0.31", category: "Mexican restaurant" },
  "el vez": { reviews: "6,399", price: "$20-30", dist: "0.32", category: "Restaurant", description: "Hip & flashy Mexican restaurant" },
  "sampan": { reviews: "2,342", price: "$30-70", dist: "0.34", category: "Pan-Asian restaurant", description: "Modern Pan-Asian restaurant and bar" },
  "high street philadelphia": { reviews: "1,171", price: "$20-30", dist: "0.34", category: "Restaurant", description: "Fork's casual sibling with baked goods" },
  "bud & marilyn's": { reviews: "2,438", price: "$20-30", dist: "0.44", category: "American restaurant", description: "American fare with a throwback vibe", address: "1234 Locust St", status: "Closed - Opens 5 PM" },
  "little nonna's": { reviews: "1,764", price: "$20-30", dist: "0.44", category: "Italian restaurant", description: "Trattoria serving homestyle Italian eats", address: "1234 Locust St", status: "Closed - Opens 5 PM" },
  "lascala's fire - center city": { reviews: "1,650", price: "$20-50", dist: "0.45", category: "Italian restaurant", description: "Classy Italian spot with seating choices" },
  "shay's steaks": { reviews: "3,165", price: "$20-30", dist: "0.46", category: "Cheesesteak restaurant" },
  "1518 bar & grill": { reviews: "758", price: "$20-30", dist: "0.47", category: "Bar & grill", description: "Local beers & a Mediterranean menu" },
  "buca d'oro ristorante": { reviews: "428", price: "$40-50", dist: "0.53", category: "Italian restaurant", description: "Old-world Italian neighborhood eatery" },
  "cafe lift": { reviews: "2,067", price: "$20-30", dist: "0.55", category: "American restaurant", description: "Unassuming American brunch/lunch spot" },
  "square 1682": { reviews: "759", price: "$20-30", dist: "0.56", category: "Restaurant", description: "Stylish & modern American restaurant" },
  "p. j. clarke's at the curtis": { reviews: "621", price: "$20-60", dist: "0.57", category: "American restaurant", description: "Burgers & beer in a casual pub setting", address: "601 Walnut St", status: "Closed - Opens 11:30 AM" }
};

function normalizeName(name) {
  return name.toLowerCase().replace(/[’]/g, "'").replace(/\s+/g, " ").trim();
}

function distanceMi(lat, lon) {
  const R = 3958.8;
  const p1 = conventionCenter.lat * Math.PI / 180;
  const p2 = lat * Math.PI / 180;
  const dp = (lat - conventionCenter.lat) * Math.PI / 180;
  const dl = (lon - conventionCenter.lon) * Math.PI / 180;
  const a = Math.sin(dp / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

function parseFeedCard(card) {
  const lines = card.text
    .split(/\n+/)
    .map(line => line.replace(/\u202f/g, " ").trim())
    .filter(line => line && !["", "", "Reserve a table", "Order online"].includes(line));
  const rating = /^\d\.\d$/.test(lines[1] || "") ? lines[1] : "Not visible in Google Maps result card";
  const categoryAddress = rating !== "Not visible in Google Maps result card" ? (lines[2] || "") : "";
  const parts = categoryAddress.split("·").map(part => part.trim()).filter(part => part && part !== "" && part !== "");
  const category = parts[0] || "Not visible in Google Maps result card";
  const address = parts.length > 1 ? parts[parts.length - 1] : "Not visible in Google Maps result card";
  let description = "Not visible in Google Maps result card";
  let status = "Not visible in Google Maps result card";
  for (const line of lines.slice(3)) {
    if (/^(Open|Closed)\b/.test(line)) status = line.replace(" · ", " - ");
    else if (description === "Not visible in Google Maps result card") description = line;
  }
  const coord = /!3d(-?\d+(?:\.\d+)?)!4d(-?\d+(?:\.\d+)?)/.exec(card.href || "");
  return {
    name: card.aria,
    googleMapsUrl: card.href || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(card.aria + " Philadelphia PA")}`,
    lat: coord ? Number(coord[1]) : null,
    lon: coord ? Number(coord[2]) : null,
    dist: coord ? distanceMi(Number(coord[1]), Number(coord[2])).toFixed(2) : null,
    rating,
    reviews: "Not visible in Google Maps result card",
    price: "Not visible in Google Maps result card",
    category,
    address,
    description,
    status,
    sun: "Not visible in Google Maps result card/detail panel",
    mon: "Not visible in Google Maps result card/detail panel",
    tue: "Not visible in Google Maps result card/detail panel",
    wed: "Not visible in Google Maps result card/detail panel",
    popular: "Not visible in Google Maps result card/detail panel",
    scope: "Google Maps result-feed card"
  };
}

const excludeCategories = new Set(["Convention center", "Hotel", "4-star hotel", "5-star hotel", "Tour operator"]);
const restaurants = new Map();

for (const card of rawFeed) {
  const row = parseFeedCard(card);
  if (excludeCategories.has(row.category)) continue;
  if (row.dist !== null && Number(row.dist) > WALKING_RADIUS_MI) continue;
  restaurants.set(normalizeName(row.name), row);
}

for (const [key, extra] of Object.entries(enrichment)) {
  const row = restaurants.get(key) || {
    name: key.replace(/\b\w/g, c => c.toUpperCase()),
    googleMapsUrl: `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(key + " Philadelphia PA")}`,
    dist: extra.dist || null,
    rating: "Not visible in Google Maps result card",
    reviews: "Not visible in Google Maps result card",
    price: "Not visible in Google Maps result card",
    category: "Not visible in Google Maps result card",
    address: extra.address || "Not visible in Google Maps result card",
    description: "Not visible in Google Maps result card",
    status: extra.status || "Not visible in Google Maps result card",
    sun: "Not visible in Google Maps result card/detail panel",
    mon: "Not visible in Google Maps result card/detail panel",
    tue: "Not visible in Google Maps result card/detail panel",
    wed: "Not visible in Google Maps result card/detail panel",
    popular: "Not visible in Google Maps result card/detail panel",
    scope: "Google Maps search-result card"
  };
  Object.assign(row, {
    reviews: extra.reviews || row.reviews,
    price: extra.price || row.price,
    dist: extra.dist || row.dist,
    category: extra.category || row.category,
    description: extra.description || row.description,
    address: extra.address || row.address,
    status: extra.status || row.status,
    sun: extra.sun || row.sun,
    mon: extra.mon || row.mon,
    tue: extra.tue || row.tue,
    wed: extra.wed || row.wed,
    popular: extra.popular || row.popular,
    scope: extra.scope || `${row.scope}; enriched by prior Google Maps search-card extraction`
  });
  restaurants.set(key, row);
}

const rows = Array.from(restaurants.values())
  .filter(row => row.dist !== null && Number(row.dist) <= WALKING_RADIUS_MI)
  .sort((a, b) => Number(a.dist) - Number(b.dist) || a.name.localeCompare(b.name));

function esc(v) {
  return String(v ?? "Not visible").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function csvEscape(v) {
  const s = String(v ?? "Not visible");
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

const csvHeader = [
  "name",
  "google_maps_url",
  "address",
  "coordinate_distance_mi",
  "rating",
  "reviews",
  "price",
  "category",
  "google_maps_description",
  "google_maps_current_status",
  "sunday_regular_hours",
  "monday_regular_hours",
  "tuesday_regular_hours",
  "wednesday_regular_hours",
  "popular_times_peak",
  "source_scope"
];
const csv = [csvHeader.join(",")].concat(rows.map(r => [
  r.name,
  r.googleMapsUrl,
  r.address,
  r.dist,
  r.rating,
  r.reviews,
  r.price,
  r.category,
  r.description,
  r.status,
  r.sun,
  r.mon,
  r.tue,
  r.wed,
  r.popular,
  r.scope
].map(csvEscape).join(","))).join("\n");

fs.writeFileSync(path.join(outDir, "ispor_2026_restaurants_google_maps_extract.csv"), csv);

const visibleHours = rows.filter(r => !r.popular.startsWith("Not visible")).length;
const bodyRows = rows.map((r, i) => `
  <tr>
    <td class="rank">${String(i + 1).padStart(2, "0")}</td>
    <td><a href="${esc(r.googleMapsUrl)}">${esc(r.name)}</a><div class="micro">${esc(r.address)}</div></td>
    <td>${esc(r.dist)}</td>
    <td><strong>${esc(r.rating)}</strong><div class="micro">${esc(r.reviews)} reviews</div></td>
    <td>${esc(r.category)}<div class="micro">${esc(r.price)}</div></td>
    <td>${esc(r.status)}</td>
    <td>${esc(r.sun)}<br>${esc(r.mon)}<br>${esc(r.tue)}<br>${esc(r.wed)}</td>
    <td>${esc(r.popular)}</td>
  </tr>`).join("\n");

const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ISPOR 2026 Nearby Restaurants</title>
  <style>
    :root { --ink:#10120f; --muted:#5c6257; --paper:#f6f1e8; --card:#fffaf0; --line:#1b1f17; --lime:#d7ff5f; --orange:#ffb86b; --blue:#b8d8ff; --pink:#ffd3e0; --radius:18px; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--paper); color:var(--ink); font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .sheet { width:1200px; min-height:4600px; padding:54px 44px 44px; background:radial-gradient(circle at 8% 3%, rgba(215,255,95,.30), transparent 360px), radial-gradient(circle at 90% 2%, rgba(184,216,255,.28), transparent 320px), var(--paper); }
    .top { display:grid; grid-template-columns: 560px 1fr; gap:26px; align-items:end; }
    .eyebrow { display:inline-flex; width:fit-content; border:1.5px solid var(--line); background:var(--lime); border-radius:999px; padding:8px 12px; font-size:14px; line-height:1; font-weight:850; text-transform:uppercase; letter-spacing:.06em; margin-bottom:18px; }
    h1 { margin:0; font-size:62px; line-height:.9; letter-spacing:0; font-weight:560; }
    .summary { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
    .metric { border:1.5px solid var(--line); border-radius:var(--radius); background:var(--card); padding:16px; min-height:106px; }
    .metric.dark { background:#11130f; color:var(--paper); }
    .num { font-size:36px; line-height:.9; font-weight:900; letter-spacing:0; }
    .label { margin-top:9px; color:var(--muted); font-size:12px; line-height:1.25; font-weight:720; }
    .dark .label { color:rgba(246,241,232,.72); }
    .note { margin-top:22px; border:1.5px solid var(--line); border-radius:var(--radius); background:var(--blue); padding:16px 18px; font-size:15px; line-height:1.32; font-weight:650; }
    table { width:100%; border-collapse:separate; border-spacing:0; margin-top:24px; border:1.5px solid var(--line); border-radius:14px; overflow:hidden; background:var(--card); table-layout:fixed; }
    th { background:#11130f; color:var(--paper); font-size:10px; line-height:1.1; text-align:left; padding:8px 7px; text-transform:uppercase; letter-spacing:.04em; }
    td { border-top:1px solid var(--line); border-right:1px solid rgba(27,31,23,.22); padding:7px; vertical-align:top; font-size:10.5px; line-height:1.18; overflow-wrap:anywhere; }
    td:last-child, th:last-child { border-right:0; }
    th:nth-child(1), td:nth-child(1) { width:36px; }
    th:nth-child(2), td:nth-child(2) { width:230px; }
    th:nth-child(3), td:nth-child(3) { width:42px; }
    th:nth-child(4), td:nth-child(4) { width:94px; }
    th:nth-child(5), td:nth-child(5) { width:150px; }
    th:nth-child(6), td:nth-child(6) { width:112px; }
    th:nth-child(7), td:nth-child(7) { width:220px; }
    .rank { font-weight:900; color:var(--muted); }
    a { color:var(--ink); font-weight:850; text-decoration:underline; text-decoration-thickness:1px; text-underline-offset:2px; }
    .micro { margin-top:4px; color:var(--muted); font-size:9.5px; line-height:1.16; font-weight:650; }
    .footer { display:grid; grid-template-columns:1fr 260px; gap:20px; margin-top:18px; color:var(--muted); font-size:11px; line-height:1.3; font-weight:650; }
    @page { size: 12.5in 45in; margin:0; }
    @media print { body,*,*::before,*::after { -webkit-print-color-adjust:exact; print-color-adjust:exact; } .sheet { width:1200px; min-height:4600px; } }
  </style>
</head>
<body>
  <main class="sheet">
    <section class="top">
      <div>
        <div class="eyebrow">ISPOR 2026 / Google Maps extract / May 14 2026</div>
        <h1>Nearby restaurant map</h1>
      </div>
      <div class="summary">
        <div class="metric dark"><div class="num">${rows.length}</div><div class="label">Google Maps restaurant/feed listings retained within ${WALKING_RADIUS_MI.toFixed(2)} mi coordinate radius</div></div>
        <div class="metric"><div class="num">${WALKING_RADIUS_MI.toFixed(2)} mi</div><div class="label">walking-distance screen used; coordinate distance is shown, not route time</div></div>
        <div class="metric"><div class="num">${visibleHours}</div><div class="label">listing with directly visible Sun-Wed hours and Popular Times; all other unavailable fields are marked</div></div>
      </div>
    </section>
    <div class="note">No inferred values are used. The Google Maps result-feed cards exposed restaurant names, ratings, categories, addresses, current status, and place links. Review counts/prices are included only where retrieved in the earlier Google Maps card extraction. Future ISPOR dates and most weekly hours/Popular Times were not visible in the extractable Maps panel, so those fields are explicitly marked not visible rather than estimated.</div>
    <table>
      <thead>
        <tr>
          <th></th><th>Restaurant</th><th>Mi</th><th>Rating</th><th>Food type</th><th>Maps status</th><th>Sun / Mon / Tue / Wed regular hours</th><th>Popular Times peak</th>
        </tr>
      </thead>
      <tbody>${bodyRows}</tbody>
    </table>
    <section class="footer">
      <div>Source: Google Maps result-feed cards for restaurants near Pennsylvania Convention Center / 1101 Arch St, Philadelphia, plus selected Google Maps search-card details already visible from the same Maps extraction run. Excluded visible non-restaurant categories: hotels, convention center, tour operator.</div>
      <div>Data file: ispor_2026_restaurants_google_maps_extract.csv</div>
    </section>
  </main>
</body>
</html>`;

fs.writeFileSync(path.join(outDir, "ispor_2026_restaurants_cohere_tan.html"), html);
console.log(`Wrote ${rows.length} rows`);
