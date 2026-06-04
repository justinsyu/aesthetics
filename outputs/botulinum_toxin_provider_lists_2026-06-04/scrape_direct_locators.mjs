import fs from "node:fs";
import path from "node:path";

const outDir = path.dirname(new URL(import.meta.url).pathname).replace(/^\/([A-Za-z]:)/, "$1");

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function csvValue(value) {
  if (value == null) return "";
  const text = Array.isArray(value) || typeof value === "object" ? JSON.stringify(value) : String(value);
  return /[",\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function writeCsv(fileName, rows, columns) {
  const csv = [
    columns.join(","),
    ...rows.map((row) => columns.map((column) => csvValue(row[column])).join(",")),
  ].join("\n");
  fs.writeFileSync(path.join(outDir, fileName), csv + "\n", "utf8");
}

function makeGrid(mode = "standard") {
  const scale = mode === "coarse" ? 1.75 : 1;
  const regions = [
    { name: "CONUS", minLat: 24.4, maxLat: 49.4, minLon: -124.9, maxLon: -66.8, stepLat: 1.0 * scale, stepLon: 1.25 * scale },
    { name: "AK", minLat: 55.0, maxLat: 64.9, minLon: -161.0, maxLon: -131.0, stepLat: 1.5 * scale, stepLon: 2.5 * scale },
    { name: "HI", minLat: 18.8, maxLat: 22.4, minLon: -160.5, maxLon: -154.7, stepLat: 0.8 * scale, stepLon: 1.0 * scale },
    { name: "PR", minLat: 17.8, maxLat: 18.6, minLon: -67.4, maxLon: -65.2, stepLat: 0.4 * scale, stepLon: 0.5 * scale },
  ];
  const points = [];
  for (const region of regions) {
    for (let lat = region.minLat; lat <= region.maxLat + 1e-9; lat += region.stepLat) {
      for (let lon = region.minLon; lon <= region.maxLon + 1e-9; lon += region.stepLon) {
        points.push({ lat: Number(lat.toFixed(5)), lon: Number(lon.toFixed(5)), region: region.name });
      }
    }
  }
  return points;
}

async function fetchJson(url, options = {}, attempts = 3) {
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), options.timeoutMs || 15000);
    try {
      const { timeoutMs, ...fetchOptions } = options;
      const response = await fetch(url, { ...fetchOptions, signal: controller.signal });
      const text = await response.text();
      if (!response.ok) throw new Error(`${response.status} ${text.slice(0, 300)}`);
      return text ? JSON.parse(text) : null;
    } catch (error) {
      lastError = error;
      await sleep(250 * attempt);
    } finally {
      clearTimeout(timer);
    }
  }
  throw lastError;
}

async function runLimited(items, limit, worker) {
  let next = 0;
  let done = 0;
  const runners = Array.from({ length: limit }, async () => {
    while (next < items.length) {
      const index = next++;
      await worker(items[index], index);
      done += 1;
      if (done % 100 === 0) console.log(`  ${done}/${items.length}`);
    }
  });
  await Promise.all(runners);
}

const selectedArgs = new Set(process.argv.slice(2));
const grid = makeGrid(selectedArgs.size === 1 && selectedArgs.has("jeuveau") ? "coarse" : "standard");
console.log(`Grid points: ${grid.length}`);

async function scrapeBotox() {
  const byId = new Map();
  const errors = [];
  const query = `query SearchQuery($limit: Int!, $offset: Int!, $searchInput: ProviderSearchInput!) {
    providerSearch(limit: $limit, offset: $offset, searchInput: $searchInput) {
      offsetPageInfo { totalResults limit offset nextOffset previousOffset }
      edges {
        displayDistance
        node {
          id providerOrganizationId parentProviderOrganizationId displayName profileSlug practiceType profileCompletenessPercentage
          address { address1 address2 city state zipcode }
          avatarImageUrl phoneNumber productIds treatmentAreaIds
          languages { id name }
          geoLocation { latitude longitude }
          consultationRequestSettings { feeTowardsTreatmentCost }
          indicators { nodes { label slug } }
          offersFinancing displayAmiBadge
          optInMarketingEvents { nodes { id title providerIsEnrolled } }
          businessHours { day open close closed }
          googleData { placeId reviewsRating totalNumReviews }
        }
      }
    }
  }`;
  const headers = {
    "Content-Type": "application/json",
    Accept: "*/*",
    "apollographql-client-version": "1.23.0",
    "apollographql-client-name": "brands-web-ssr",
    "adl-consumer-anon": "89bfbb60-a8e7-46df-a316-8a137b2228f1",
    "User-Agent": "Mozilla/5.0",
  };
  async function pageAt(point, offset = 0) {
    const searchInput = {
      sort: { column: "DEFAULT", order: "ASCENDING" },
      filters: {
        proximity: { geoPoint: { latitude: point.lat, longitude: point.lon }, radiusInMiles: 100 },
        hours: {},
        profile: { brandNames: ["botox"], treatmentAreaIds: [] },
      },
    };
    const body = JSON.stringify({ operationName: "SearchQuery", variables: { limit: 100, offset, searchInput }, query });
    return fetchJson("https://api.alle.com/graphql", { method: "POST", headers, body });
  }
  await runLimited(grid, 6, async (point) => {
    try {
      let offset = 0;
      for (let guard = 0; guard < 10; guard += 1) {
        const json = await pageAt(point, offset);
        const search = json?.data?.providerSearch;
        for (const edge of search?.edges || []) {
          const node = edge.node || {};
          const address = node.address || {};
          const geo = node.geoLocation || {};
          byId.set(node.id || node.providerOrganizationId || `${node.displayName}-${address.zipcode}`, {
            source_product: "BOTOX Cosmetic",
            source_company: "AbbVie / Allergan Aesthetics",
            source_locator_url: "https://botoxcosmetic.alle.com/search",
            id: node.id,
            provider_organization_id: node.providerOrganizationId,
            parent_provider_organization_id: node.parentProviderOrganizationId,
            display_name: node.displayName,
            profile_slug: node.profileSlug,
            profile_url: node.profileSlug ? `https://botoxcosmetic.alle.com/provider/${node.profileSlug}` : "",
            practice_type: node.practiceType,
            profile_completeness_percentage: node.profileCompletenessPercentage,
            address1: address.address1,
            address2: address.address2,
            city: address.city,
            state: address.state,
            zip: address.zipcode,
            phone: node.phoneNumber,
            latitude: geo.latitude,
            longitude: geo.longitude,
            product_ids: node.productIds,
            treatment_area_ids: node.treatmentAreaIds,
            languages: (node.languages || []).map((x) => x.name).join("; "),
            indicators: (node.indicators?.nodes || []).map((x) => x.label).join("; "),
            offers_financing: node.offersFinancing,
            display_ami_badge: node.displayAmiBadge,
            fee_towards_treatment_cost: node.consultationRequestSettings?.feeTowardsTreatmentCost,
            google_place_id: node.googleData?.placeId,
            google_reviews_rating: node.googleData?.reviewsRating,
            google_total_reviews: node.googleData?.totalNumReviews,
            business_hours_json: node.businessHours,
            marketing_events_json: node.optInMarketingEvents?.nodes,
          });
        }
        const info = search?.offsetPageInfo;
        if (!info || info.nextOffset == null || info.nextOffset < 0 || info.nextOffset === offset) break;
        offset = info.nextOffset;
      }
    } catch (error) {
      errors.push({ point, error: error.message });
    }
  });
  const rows = [...byId.values()].sort((a, b) => `${a.state || ""}${a.city || ""}${a.display_name || ""}`.localeCompare(`${b.state || ""}${b.city || ""}${b.display_name || ""}`));
  writeCsv("botox_cosmetic_alle_providers.csv", rows, Object.keys(rows[0] || { source_product: "" }));
  fs.writeFileSync(path.join(outDir, "botox_cosmetic_alle_errors.json"), JSON.stringify(errors, null, 2));
  console.log(`BOTOX rows: ${rows.length}, errors: ${errors.length}`);
}

async function scrapeDysport() {
  const byId = new Map();
  const errors = [];
  await runLimited(grid, 5, async (point) => {
    const url = `https://www.dysportusa.com/api/find-a-specialist?latitude=${point.lat}&longitude=${point.lon}&take=1500&radius=100&zipToSortBy=`;
    try {
      const json = await fetchJson(url, {
        headers: {
          "User-Agent": "Mozilla/5.0",
          Accept: "application/json, text/javascript, */*; q=0.01",
          "X-Requested-With": "XMLHttpRequest",
          Referer: "https://www.dysportusa.com/find-a-specialist",
        },
      });
      for (const row of json?.data || []) {
        if (row.Dysport !== true) continue;
        byId.set(row.ID || `${row.PracticeName}-${row.Zip}`, {
          source_product: "Dysport",
          source_company: "Ipsen / Galderma",
          source_locator_url: "https://www.dysportusa.com/find-a-specialist",
          id: row.ID,
          practice_name: row.PracticeName,
          first_name: row.FirstName,
          last_name: row.LastName,
          specialists: Array.isArray(row.Specialists) ? row.Specialists.join("; ") : row.Specialists,
          specialty: row.Specialty,
          specialty_description: row.SpecialtyDescription,
          specialty_group: row.SpecialtyGroup,
          address: row.Address,
          address_optional: row.AddressOptional,
          city: row.City,
          state: row.State,
          zip: row.Zip,
          phone: row.Phone,
          email: row.Email,
          practice_url: row.PracticeURL,
          latitude: row.Latitude,
          longitude: row.Longitude,
          aspire: row.Aspire,
          gain: row.GAIN,
          dysport: row.Dysport,
          restylane: row.RestyLane,
          defyne: row.Defyne,
          refyne_dollars: row.RefyneDollars,
          dysport_dollars: row.DysportDollars,
          total_dollars: row.TotalDollars,
          products_flags_json: {
            Lyft: row.Lyft, Silk: row.Silk, Sculptraaes: row.Sculptraaes, RestyLane: row.RestyLane,
            Defyne: row.Defyne, Kysse: row.Kysse, Contour: row.Contour, Multi: row.Multi,
          },
        });
      }
    } catch (error) {
      errors.push({ point, error: error.message });
    }
  });
  const rows = [...byId.values()].sort((a, b) => `${a.state || ""}${a.city || ""}${a.practice_name || ""}`.localeCompare(`${b.state || ""}${b.city || ""}${b.practice_name || ""}`));
  writeCsv("dysport_usa_providers.csv", rows, Object.keys(rows[0] || { source_product: "" }));
  fs.writeFileSync(path.join(outDir, "dysport_usa_errors.json"), JSON.stringify(errors, null, 2));
  console.log(`Dysport rows: ${rows.length}, errors: ${errors.length}`);
}

async function scrapeXeomin() {
  const byId = new Map();
  const errors = [];
  await runLimited(grid, 5, async (point) => {
    const body = JSON.stringify({
      namespace: "",
      classname: "PFMapboxController",
      method: "getNearbyProviders",
      params: {
        latitude: point.lat,
        longitude: point.lon,
        radius: 100,
        isFly: false,
        sortingFunction: "distance",
        website: "xeomin",
        brands: null,
        badges: null,
        brandsFlag: false,
        badgesFlag: false,
      },
      cacheable: false,
      isContinuation: false,
    });
    try {
      const json = await fetchJson("https://merzcommunities.my.site.com/PhysicianFinder/webruntime/api/apex/execute?language=en-US&asGuest=true&htmlEncode=false", {
        method: "POST",
        headers: {
          "Content-Type": "application/json; charset=utf-8",
          Accept: "application/json",
          Referer: "https://merzcommunities.my.site.com/PhysicianFinder/xeomin",
          "User-Agent": "Mozilla/5.0",
        },
        body,
      });
      for (const row of json?.returnValue || []) {
        const account = row.account || {};
        const ship = account.ShippingAddress || {};
        const hours = account.PracticeOpenHours__r?.records?.[0] || {};
        byId.set(account.Id || `${account.Name}-${ship.postalCode}`, {
          source_product: "Xeomin",
          source_company: "Merz Aesthetics",
          source_locator_url: "https://www.xeominaesthetic.com/find-a-provider/",
          account_id: account.Id,
          name: account.Practice_Name_Override__c || account.Name,
          legal_account_name: account.Name,
          phone: account.Practice_Phone_Override__c || account.Phone,
          website: account.Practice_Website_Override__c || account.Practice_Website__c || account.Website,
          address_text: account.MedPro_Primary_Address__c,
          street: ship.street,
          city: ship.city,
          state: ship.stateCode || ship.state,
          zip: ship.postalCode,
          country: ship.country,
          latitude: row.lat || account.ShippingLatitude || account.BillingLatitude,
          longitude: row.lng || account.ShippingLongitude || account.BillingLongitude,
          brands_listed_for: account.Brands_Listed_For__c,
          brand_tiers: account.Brand_Tiers__c,
          providers_json: account.Practice_Providers__c,
          logo_public_url: row.logoPublicUrl,
          badge_value: row.badgeValue,
          available_procedures: hours.AvailableProcedures__c,
          facebook: hours.SocialLinkFacebook__c,
          instagram: hours.SocialLinkInstagram__c,
          hours_json: hours,
        });
      }
    } catch (error) {
      errors.push({ point, error: error.message });
    }
  });
  const rows = [...byId.values()].sort((a, b) => `${a.state || ""}${a.city || ""}${a.name || ""}`.localeCompare(`${b.state || ""}${b.city || ""}${b.name || ""}`));
  writeCsv("xeomin_aesthetic_providers.csv", rows, Object.keys(rows[0] || { source_product: "" }));
  fs.writeFileSync(path.join(outDir, "xeomin_aesthetic_errors.json"), JSON.stringify(errors, null, 2));
  console.log(`Xeomin rows: ${rows.length}, errors: ${errors.length}`);
}

async function scrapeJeuveau() {
  const byId = new Map();
  const errors = [];
  await runLimited(grid, 5, async (point) => {
    const params = new URLSearchParams({
      latitude: String(point.lat),
      longitude: String(point.lon),
      radius: "100",
      product: "jeuveau",
    });
    try {
      const rows = await fetchJson(`https://txcvquhsn7.execute-api.us-east-1.amazonaws.com/production/getRankedFacilityProfilesWithinRadius?${params}`, {
        headers: {
          "User-Agent": "Mozilla/5.0",
          Accept: "application/json",
          Origin: "https://www.evolus.com",
          Referer: "https://www.evolus.com/jeuveau/find-a-practice?product=jeuveau",
        },
      });
      for (const row of rows || []) {
        if (row.has_purchased_jeuveau === false) continue;
        byId.set(row.facility_id || `${row.name}-${row.zip}`, {
          source_product: "Jeuveau",
          source_company: "Evolus",
          source_locator_url: "https://www.evolus.com/jeuveau/find-a-practice?product=jeuveau",
          facility_id: row.facility_id,
          account_id: row.account_id,
          name: row.name,
          profile_url: row.facility_id ? `https://www.evolus.com/jeuveau/practices/${String(row.name || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}-${row.facility_id}?product=jeuveau` : "",
          address_line_1: row.address_line_1,
          address_line_2: row.address_line_2,
          city: row.city,
          state: row.state,
          zip: row.zip,
          email: row.email,
          phone: row.phone,
          latitude: row.latitude,
          longitude: row.longitude,
          description: row.description,
          specialties: row.specialties,
          service_options: row.service_options,
          operating_hours_json: row.operating_hours,
          is_open_after_5pm: row.is_open_after_5pm,
          is_open_on_weekend: row.is_open_on_weekend,
          opt_in: row.opt_in,
          account_club_opt_in: row.account_club_opt_in,
          is_club_opt_in: row.is_club_opt_in,
          is_accept_club_evolus: row.is_accept_club_evolus,
          is_suspended: row.is_suspended,
          max_invoiced_amount: row.max_invoiced_amount,
          override_invoiced_amount: row.override_invoiced_amount,
          has_purchased_jeuveau: row.has_purchased_jeuveau,
          has_purchased_evolysse: row.has_purchased_evolysse,
          media_json: row.media,
        });
      }
    } catch (error) {
      errors.push({ point, error: error.message });
    }
  });
  const rows = [...byId.values()].sort((a, b) => `${a.state || ""}${a.city || ""}${a.name || ""}`.localeCompare(`${b.state || ""}${b.city || ""}${b.name || ""}`));
  writeCsv("jeuveau_evolus_practices.csv", rows, Object.keys(rows[0] || { source_product: "" }));
  fs.writeFileSync(path.join(outDir, "jeuveau_evolus_errors.json"), JSON.stringify(errors, null, 2));
  console.log(`Jeuveau rows: ${rows.length}, errors: ${errors.length}`);
}

const tasks = [
  ["botox", scrapeBotox],
  ["dysport", scrapeDysport],
  ["xeomin", scrapeXeomin],
  ["jeuveau", scrapeJeuveau],
].filter(([name]) => selectedArgs.size === 0 || selectedArgs.has(name));

for (const [name, task] of tasks) {
  console.log(`Starting ${name}`);
  await task();
}
