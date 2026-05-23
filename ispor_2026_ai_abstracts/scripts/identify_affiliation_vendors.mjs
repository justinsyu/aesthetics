import fs from "node:fs/promises";
import path from "node:path";

const root = "/Users/justinyu/Desktop/linkedin-posts/ispor_2026_ai_abstracts";
const inputPath = path.join(root, "data", "abstracts.json");
const outputDir = path.join(root, "vendors");

const criteria = [
  "Included organizations are non-academic, non-provider, non-government entities visible in author affiliation text, including HEOR consultancies, evidence vendors, CROs, analytics/data firms, AI/software/platform firms, and pharma/biotech/medtech sponsors.",
  "Excluded organizations are universities, hospitals, health systems, public agencies, regulators, academic medical centers, departments, job titles, and individual author names.",
  "Classification is inferred from affiliation names only; ambiguous entities are preserved as manual-review cases rather than treated as confirmed vendors.",
  "Obvious case, spelling, punctuation, location, and subsidiary variants are consolidated under one canonical organization name.",
];

const vendorRules = [
  ["Amazon Web Services", "cloud / technology platform", "likely_vendor", [/Amazon Web Services/i, /\bAWS\b/i]],
  ["argenx", "pharma / biotech sponsor", "likely_vendor", [/argenx/i]],
  ["Arysana", "HEOR / AI platform or consultancy", "likely_vendor", [/Arysana/i]],
  ["AstraZeneca", "pharma / biotech sponsor", "likely_vendor", [/AstraZeneca/i]],
  ["AureusIQ", "AI / analytics firm", "likely_vendor", [/AureusIQ/i]],
  ["BeOne Medicines", "pharma / biotech sponsor", "likely_vendor", [/BeOne Medicines/i]],
  ["Booz Allen Hamilton", "consulting / analytics firm", "likely_vendor", [/Booz Allen Hamilton/i]],
  ["Boston Scientific", "medtech sponsor", "likely_vendor", [/Boston Scientific/i]],
  ["Carevive", "health technology / oncology care platform", "manual_review", [/Carevive/i]],
  ["Columbia Data Analytics", "analytics firm", "likely_vendor", [/Columbia Data Analytics/i]],
  ["ConnectHEOR", "HEOR consultancy", "likely_vendor", [/ConnectHEOR/i]],
  ["Costello Medical", "medical / HEOR consultancy", "likely_vendor", [/Costello Medical/i]],
  ["Covalence Research", "research consultancy", "likely_vendor", [/Covalence Research/i]],
  ["Cytel", "CRO / biostatistics vendor", "likely_vendor", [/Cytel(?: Inc)?/i]],
  ["Dandelion Health", "health data / AI platform", "manual_review", [/Dandelion Health/i]],
  ["DataUnite", "data / analytics firm", "likely_vendor", [/DataUnite/i]],
  ["EasySLR", "evidence synthesis software", "likely_vendor", [/EasySLR/i]],
  ["EVERSANA", "life sciences services / HEOR vendor", "likely_vendor", [/EVERSANA/i]],
  ["Evidence Prime", "evidence synthesis software / services", "likely_vendor", [/Evidence Prime/i]],
  ["Evidinno Outcomes Research", "outcomes research consultancy", "likely_vendor", [/Evidinno Outcomes Research/i]],
  ["Eviviz", "software / analytics firm", "likely_vendor", [/Eviviz/i]],
  ["Flatiron Health", "health data / oncology analytics firm", "likely_vendor", [/Flatiron Health/i]],
  ["Forian", "health data / analytics firm", "likely_vendor", [/Forian/i]],
  ["Gilead Sciences", "pharma / biotech sponsor", "likely_vendor", [/Gilead Sciences/i]],
  ["GSK", "pharma / biotech sponsor", "likely_vendor", [/\bGSK(?: US)?\b/i]],
  ["Harvey L. Neiman Health Policy Institute", "policy institute", "manual_review", [/Harvey L\.?\s+Neiman Health Policy Institute/i]],
  ["Health Catalyst", "health data / analytics firm", "manual_review", [/Health Catalyst/i]],
  ["Heorlytics", "HEOR consultancy", "likely_vendor", [/Heorlytics/i]],
  ["HTA-Hive", "HTA / evidence platform or consultancy", "manual_review", [/HTA-Hive/i]],
  ["Independent Consultant", "independent consultancy", "manual_review", [/Independent Consultant/i, /\bIndependent\b/i]],
  ["Johnson & Johnson", "pharma / medtech sponsor", "likely_vendor", [/Johnson\s*(?:&|and)\s*Johnson/i]],
  ["JPS Healthcare", "healthcare organization", "manual_review", [/JPS Healthcare/i]],
  ["Keiji.AI", "AI / analytics firm", "likely_vendor", [/Keiji\.AI/i]],
  ["Klick Health", "health agency / technology firm", "likely_vendor", [/Klick Health/i]],
  ["Knight Therapeutics", "pharma / biotech sponsor", "manual_review", [/Knight Therapeutics/i]],
  ["KolateAI PharmaTech", "AI / pharma technology firm", "likely_vendor", [/KolateAI PharmaTech/i]],
  ["Landmark Science", "life sciences technology / analytics firm", "likely_vendor", [/Landmark Science/i]],
  ["McKesson", "healthcare services / data firm", "likely_vendor", [/McKesson/i]],
  ["Menarini Group", "pharma / biotech sponsor", "likely_vendor", [/Menarini Group/i]],
  ["Merck & Co.", "pharma / biotech sponsor", "likely_vendor", [/Merck\s*&\s*Co/i]],
  ["Microsoft", "technology platform", "likely_vendor", [/Microsoft/i]],
  ["MILLER ECONOMICS", "health economics consultancy", "likely_vendor", [/MILLER ECONOMICS/i]],
  ["NAMina Bio", "pharma / biotech sponsor", "likely_vendor", [/NAMina Bio/i]],
  ["Nested Knowledge", "evidence synthesis software / services", "likely_vendor", [/Nested Knowledge/i]],
  ["Northwell", "health system", "manual_review", [/Northwell/i]],
  ["Novo Nordisk", "pharma / biotech sponsor", "likely_vendor", [/Novo Nordisk/i]],
  ["Oncomed BH / Grupo Orizonti", "healthcare organization", "manual_review", [/Oncomed BH/i, /Grupo Orizonti/i]],
  ["Oncoscope-AI", "AI / oncology analytics firm", "likely_vendor", [/Oncoscope-AI/i]],
  ["Ontada", "oncology data / analytics firm", "likely_vendor", [/Ontada/i]],
  ["OPEN Health", "HEOR / medical consultancy", "likely_vendor", [/OPEN Health/i]],
  ["Optum", "health services / data analytics firm", "likely_vendor", [/Optum(?: Global Solution[s]?| Life Sciences| Lifesciences)?/i]],
  ["Oracle Life Sciences", "technology / life sciences platform", "likely_vendor", [/Oracle Life Sciences/i]],
  ["PAIML Scientific Working Group", "working group", "manual_review", [/(?:S)?PAIML Scientific Working Group/i]],
  ["Parexel", "CRO / life sciences services", "likely_vendor", [/Parexel/i, /PAREXEL/i]],
  ["Pfizer", "pharma / biotech sponsor", "likely_vendor", [/Pfizer/i]],
  ["Pharmacoevidence", "HEOR consultancy", "likely_vendor", [/Pharmacoevidence(?:\s+Pvt\.?\s+Ltd\.?)?/i]],
  ["PharmaQuant", "HEOR / analytics consultancy", "likely_vendor", [/PharmaQuant(?: Insights| International)?(?: Private Limited| Pvt\.?\s+Ltd\.?| Limited)?/i]],
  ["PHAROS Labs", "AI / analytics firm", "likely_vendor", [/PHAROS Labs(?: GmbH)?/i]],
  ["Pomelo Care", "care delivery / digital health organization", "manual_review", [/Pomelo Care/i]],
  ["Precision AQ", "life sciences consultancy", "likely_vendor", [/Precision AQ/i]],
  ["Principal Health Economics", "health economics consultancy", "likely_vendor", [/Principal Health Economics/i]],
  ["Regeneron Pharmaceuticals", "pharma / biotech sponsor", "likely_vendor", [/Regeneron Pharmaceuticals/i]],
  ["Sandpiper Analytics", "analytics firm", "likely_vendor", [/Sandpiper Analytics/i]],
  ["Sarepta Therapeutics", "pharma / biotech sponsor", "likely_vendor", [/Sarepta Therapeutics/i]],
  ["SAS Institute", "analytics software vendor", "likely_vendor", [/SAS Institute/i]],
  ["Sciensus", "healthcare services organization", "manual_review", [/Sciensus/i]],
  ["Skyward Analytics", "analytics firm", "likely_vendor", [/Skyward Analytics/i]],
  ["Star Biopharma Consulting", "life sciences consultancy", "likely_vendor", [/Star Biopharma Consulting/i]],
  ["Swipha Pharma Nig", "pharma / biotech sponsor", "likely_vendor", [/Swipha Pharma Nig/i]],
  ["Syreon Research Institute", "research institute / consultancy", "manual_review", [/Syreon Research Institute/i]],
  ["Systematic Review Ltd.", "evidence synthesis consultancy", "likely_vendor", [/Systematic Review Ltd/i]],
  ["Takeda Pharmaceuticals", "pharma / biotech sponsor", "likely_vendor", [/Takeda Pharmaceuticals/i]],
  ["Teva Pharmaceuticals", "pharma / biotech sponsor", "likely_vendor", [/Teva Pharma(?:cieticals|ceuticals)?/i]],
  ["The Synthesis Company of California", "evidence synthesis consultancy", "likely_vendor", [/The Synthesis Company of California(?: Ltd\.?)?/i]],
  ["Thermo Fisher Scientific", "life sciences services / technology firm", "likely_vendor", [/Thermo Fish(?:er|cer) Scientific/i]],
  ["Trinity Life Sciences", "life sciences consultancy", "likely_vendor", [/Trinity Life Sciences/i]],
  ["Truveta", "health data / analytics firm", "likely_vendor", [/Truveta/i]],
  ["Unimed-BH", "healthcare payer/provider organization", "manual_review", [/Unimed-BH/i, /UNIMED-BH/i]],
  ["Value Analytics Labs", "analytics consultancy", "likely_vendor", [/Value Analytics Labs/i]],
  ["Veev Consulting", "consultancy", "likely_vendor", [/Veev Consulting/i]],
  ["Xplain Data", "data / analytics firm", "likely_vendor", [/Xplain Data/i]],
  ["ZS Associates", "life sciences consultancy", "likely_vendor", [/ZS Associates/i]],
];

function csvEscape(value) {
  if (value == null) return "";
  const text = String(value);
  return /[",\n\r]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function uniqueByName(items) {
  const seen = new Set();
  return items.filter((item) => {
    if (seen.has(item.name)) return false;
    seen.add(item.name);
    return true;
  });
}

function findVendors(text) {
  const matches = [];
  for (const [name, category, status, patterns] of vendorRules) {
    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match) {
        matches.push({
          name,
          category,
          status,
          matched_text: match[0],
        });
        break;
      }
    }
  }
  return uniqueByName(matches).sort((a, b) => {
    if (a.status !== b.status) return a.status.localeCompare(b.status);
    return a.name.localeCompare(b.name);
  });
}

function summarize(records) {
  const byName = new Map();
  for (const record of records) {
    for (const vendor of record.vendors) {
      if (!byName.has(vendor.name)) {
        byName.set(vendor.name, {
          name: vendor.name,
          status: vendor.status,
          category: vendor.category,
          matched_texts: new Set(),
          abstracts: [],
        });
      }
      const entry = byName.get(vendor.name);
      entry.matched_texts.add(vendor.matched_text);
      entry.abstracts.push({
        index: record.index,
        session_code: record.session_code,
        title: record.title,
      });
    }
  }
  return [...byName.values()]
    .map((entry) => ({
      ...entry,
      matched_texts: [...entry.matched_texts].sort(),
      record_count: new Set(entry.abstracts.map((abstract) => abstract.index)).size,
      abstracts: entry.abstracts.sort((a, b) => a.index - b.index),
    }))
    .sort((a, b) => b.record_count - a.record_count || a.name.localeCompare(b.name));
}

function markdownFor(summary, records) {
  const likely = summary.filter((entry) => entry.status === "likely_vendor");
  const ambiguous = summary.filter((entry) => entry.status === "manual_review");
  const withoutVendors = records.filter((record) => !record.vendors.length);
  const lines = [
    "# ISPOR 2026 AI Abstract Affiliation Vendor Scan",
    "",
    "## Classification Criteria",
    "",
    ...criteria.map((item) => `- ${item}`),
    "",
    "## Likely Vendor Organizations",
    "",
    ...likely.map(
      (entry) =>
        `- ${entry.name} (${entry.category}; ${entry.record_count} abstract${entry.record_count === 1 ? "" : "s"}): ${entry.abstracts
          .map((abstract) => abstract.session_code)
          .join(", ")}`,
    ),
    "",
    "## Manual-Review Organizations",
    "",
    ...ambiguous.map(
      (entry) =>
        `- ${entry.name} (${entry.category}; ${entry.record_count} abstract${entry.record_count === 1 ? "" : "s"}): ${entry.abstracts
          .map((abstract) => abstract.session_code)
          .join(", ")}`,
    ),
    "",
    "## Records Without a Potential Vendor Match",
    "",
    ...withoutVendors.map((record) => `- ${record.index}. ${record.session_code}: ${record.title}`),
    "",
  ];
  return lines.join("\n");
}

async function main() {
  const abstracts = JSON.parse(await fs.readFile(inputPath, "utf8"));
  await fs.mkdir(outputDir, { recursive: true });

  const records = abstracts.map((abstract) => {
    const vendors = findVendors(abstract.authors || "");
    return {
      index: abstract.index,
      session_code: abstract.session_code,
      title: abstract.title,
      authors_affiliations: abstract.authors,
      vendors,
      likely_vendors: vendors.filter((vendor) => vendor.status === "likely_vendor"),
      manual_review_organizations: vendors.filter((vendor) => vendor.status === "manual_review"),
    };
  });
  const summary = summarize(records);

  await fs.writeFile(
    path.join(outputDir, "vendor_classification_criteria.json"),
    JSON.stringify({ criteria, generated_at: new Date().toISOString() }, null, 2),
  );
  await fs.writeFile(path.join(outputDir, "abstract_vendor_mapping.json"), JSON.stringify(records, null, 2));
  await fs.writeFile(path.join(outputDir, "vendor_summary.json"), JSON.stringify(summary, null, 2));
  await fs.writeFile(path.join(outputDir, "vendor_summary.md"), markdownFor(summary, records));

  const mappingColumns = [
    "index",
    "session_code",
    "title",
    "likely_vendors",
    "manual_review_organizations",
    "all_potential_organizations",
    "authors_affiliations",
  ];
  const mappingCsv = [
    mappingColumns.join(","),
    ...records.map((record) =>
      [
        record.index,
        record.session_code,
        record.title,
        record.likely_vendors.map((vendor) => vendor.name).join("; "),
        record.manual_review_organizations.map((vendor) => vendor.name).join("; "),
        record.vendors.map((vendor) => `${vendor.name} [${vendor.status}]`).join("; "),
        record.authors_affiliations,
      ]
        .map(csvEscape)
        .join(","),
    ),
  ].join("\n");
  await fs.writeFile(path.join(outputDir, "abstract_vendor_mapping.csv"), `${mappingCsv}\n`);

  const summaryColumns = ["name", "status", "category", "record_count", "session_codes", "matched_texts"];
  const summaryCsv = [
    summaryColumns.join(","),
    ...summary.map((entry) =>
      [
        entry.name,
        entry.status,
        entry.category,
        entry.record_count,
        entry.abstracts.map((abstract) => abstract.session_code).join("; "),
        entry.matched_texts.join("; "),
      ]
        .map(csvEscape)
        .join(","),
    ),
  ].join("\n");
  await fs.writeFile(path.join(outputDir, "vendor_summary.csv"), `${summaryCsv}\n`);

  console.log(
    JSON.stringify(
      {
        abstracts: records.length,
        abstracts_with_likely_vendor: records.filter((record) => record.likely_vendors.length).length,
        abstracts_with_manual_review_org: records.filter((record) => record.manual_review_organizations.length).length,
        likely_vendor_count: summary.filter((entry) => entry.status === "likely_vendor").length,
        manual_review_count: summary.filter((entry) => entry.status === "manual_review").length,
        outputDir,
      },
      null,
      2,
    ),
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
