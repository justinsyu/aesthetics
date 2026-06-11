import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const dataDir = path.join(root, "data");
const launchTimelineBuckets = ["0-12 months", "12-24 months", "24-36 months", "36+ months"];

const args = parseArgs(process.argv.slice(2));
const config = JSON.parse(await fs.readFile(path.join(root, "config.json"), "utf8"));

const areaQueries = resolveAreaQueries(args, config);
const limit = Number(args.limit || config.defaultLimit || 48);
const cadence = String(args.cadence || config.defaultCadence || "monthly");

if (args.interval) {
  const intervalMs = parseInterval(args.interval);
  await refresh();
  console.log(`Watching. Next refresh every ${args.interval}.`);
  setInterval(refresh, intervalMs);
} else {
  await refresh();
}

async function refresh() {
  const runStartedAt = new Date();
  const sourceLog = [];
  const researchOverrides = await loadResearchOverrides();
  let assets = [];
  let fallbackUsed = false;
  let clinicalTrialsError = null;
  let excludedSponsors = [];

  try {
    const studies = await fetchClinicalTrialsForAreas(areaQueries, limit, sourceLog);
    const normalizedStudies = studies.map(({ study, area, query }) => normalizeClinicalTrial(study, area, query, runStartedAt));
    const filtered = filterCommercialSponsors(normalizedStudies);
    assets = filtered.assets;
    excludedSponsors = filtered.excluded;
  } catch (error) {
    clinicalTrialsError = error.message;
    fallbackUsed = true;
  }

  if (!assets.length) {
    fallbackUsed = true;
    assets = await loadPriorAssetsForFallback();
    if (!assets.length) {
      assets = JSON.parse(await fs.readFile(path.join(dataDir, "seed-assets.json"), "utf8"));
    }
  }

  const groupedAssets = groupAssetsByDrug(assets);
  const openFdaMeta = await fetchOpenFdaMeta(sourceLog).catch((error) => {
    sourceLog.push({
      source: "openFDA",
      type: "API status",
      title: "openFDA metadata unavailable",
      url: "https://api.fda.gov/drug/drugsfda.json?limit=1",
      status: "error",
      detail: error.message,
      checked_at: runStartedAt.toISOString()
    });
    return null;
  });
  const approvalContexts = fallbackUsed ? new Map() : await fetchApprovalContexts(groupedAssets, sourceLog, runStartedAt);
  const approvalAnnotated = groupedAssets.map((asset) => applyApprovalContext(asset, approvalContexts.get(approvalLookupKey(asset.asset_name)), runStartedAt));
  const researchAnnotated = applyResearchOverrides(approvalAnnotated, researchOverrides, runStartedAt);
  const pipelineFiltered = filterPipelineAssets(researchAnnotated);

  const normalized = dedupeAssets(pipelineFiltered.assets).slice(0, limit).map((asset, index) => ensureProvenance({
    ...asset,
    rank: index + 1,
    last_updated: runStartedAt.toISOString()
  }, runStartedAt));
  validateLaunchTimelineBuckets(normalized);
  const researchAssignments = createResearchAssignments(normalized, researchOverrides, runStartedAt);

  const output = {
    metadata: {
      product: "Pipeline Intelligence",
      generated_at: runStartedAt.toISOString(),
      scope: Object.keys(areaQueries).join(", "),
      queries: areaQueries,
      limit,
      cadence,
      asset_count: normalized.length,
      excluded_non_pipeline_asset_count: pipelineFiltered.excluded.length,
      excluded_non_pipeline_asset_examples: pipelineFiltered.excluded.slice(0, 12),
      excluded_marketed_or_approved_count: pipelineFiltered.excluded.length,
      excluded_marketed_or_approved_examples: pipelineFiltered.excluded.slice(0, 12),
      excluded_non_commercial_sponsor_count: excludedSponsors.length,
      excluded_non_commercial_sponsor_examples: excludedSponsors.slice(0, 12),
      fallback_used: fallbackUsed,
      clinical_trials_error: clinicalTrialsError,
      openfda_last_updated: openFdaMeta?.last_updated || null,
      openfda_approval_matches: [...approvalContexts.values()].filter((context) => context.status === "matched").length,
      source_backed_research_packets: normalized.filter((asset) => asset.research_status === "source_backed").length,
      pending_research_assignments: researchAssignments.filter((assignment) => assignment.status !== "complete").length,
      source_notes: [
        "Every asset has a research assignment record. Detail fields marked Source-backed or Derived from registry cite direct source references; fields marked Heuristic estimate are planning estimates pending asset-level subagent research.",
        "Already marketed, launched, FDA-approved, discontinued, device, diagnostic, supplement, and other non-drug/non-active-pipeline records are excluded from the dashboard so the interface remains focused on pipeline intelligence.",
        "Commercial sponsor filtering keeps ClinicalTrials.gov studies where the lead sponsor is listed as INDUSTRY or the sponsor name matches a pharma/biotech company pattern; universities, hospitals, medical centers, institutes, and government entities are excluded.",
        "Use source URLs and analyst review before making formulary decisions."
      ]
    },
    assets: normalized,
    source_log: sourceLog
  };

  await fs.mkdir(dataDir, { recursive: true });
  await fs.writeFile(path.join(dataDir, "pipeline-assets.json"), `${JSON.stringify(output, null, 2)}\n`);
  await fs.writeFile(path.join(dataDir, "pipeline-assets.csv"), toCsv(normalized));
  await fs.writeFile(path.join(dataDir, "research-assignments.json"), `${JSON.stringify({ generated_at: runStartedAt.toISOString(), assignments: researchAssignments }, null, 2)}\n`);

  console.log(`Generated ${normalized.length} assets at ${output.metadata.generated_at}`);
  if (fallbackUsed) console.log("Fallback seed data was used.");
}

async function loadResearchOverrides() {
  const file = path.join(dataDir, "research-overrides.json");
  let base;
  try {
    base = JSON.parse(await fs.readFile(file, "utf8"));
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
    base = { metadata: {}, overrides: {} };
  }

  const packetOverrides = await loadResearchPackets();
  return {
    ...base,
    metadata: {
      ...(base.metadata || {}),
      packet_override_count: Object.keys(packetOverrides).length
    },
    overrides: {
      ...(base.overrides || {}),
      ...packetOverrides
    }
  };
}

async function loadPriorAssetsForFallback() {
  const file = path.join(dataDir, "pipeline-assets.json");
  try {
    const previous = JSON.parse(await fs.readFile(file, "utf8"));
    if (previous?.metadata?.fallback_used) return [];
    return previous.assets || [];
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
    return [];
  }
}

async function loadResearchPackets() {
  const packetsDir = path.join(root, "research", "packets");
  const overrides = {};
  let files = [];
  try {
    files = await fs.readdir(packetsDir);
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
    return overrides;
  }

  for (const fileName of files.filter((name) => name.endsWith(".json"))) {
    const packetPath = path.join(packetsDir, fileName);
    const packet = JSON.parse(await fs.readFile(packetPath, "utf8"));
    const key = packet.asset_id || path.basename(fileName, ".json");
    overrides[key] = packet;
  }

  return overrides;
}

async function fetchClinicalTrialsForAreas(queries, maxRecords, sourceLog) {
  const entries = Object.entries(queries);
  const perArea = Math.max(18, Math.ceil((maxRecords / Math.max(entries.length, 1)) * 1.8));
  const all = [];

  for (const [area, query] of entries) {
    const studies = await fetchClinicalTrials(area, query, perArea, sourceLog);
    all.push(...studies.map((study) => ({ study, area, query })));
  }

  return all;
}

async function fetchClinicalTrials(area, queryCondition, maxRecords, sourceLog) {
  const statuses = ["RECRUITING", "ACTIVE_NOT_RECRUITING", "NOT_YET_RECRUITING"];
  const perStatus = Math.max(10, Math.ceil(maxRecords / statuses.length));
  const all = [];

  for (const status of statuses) {
    const url = new URL("https://clinicaltrials.gov/api/v2/studies");
    url.searchParams.set("query.cond", queryCondition);
    url.searchParams.set("query.term", `AREA[OverallStatus]${status}`);
    url.searchParams.set("query.intr", "Drug");
    url.searchParams.set("format", "json");
    url.searchParams.set("pageSize", String(perStatus));

    const response = await fetch(url, { headers: { "Accept": "application/json" } });
    if (!response.ok) {
      throw new Error(`ClinicalTrials.gov ${response.status} for ${status}`);
    }
    const body = await response.json();
    sourceLog.push({
      source: "ClinicalTrials.gov API v2",
      type: "Clinical trials",
      title: `${area}: ${queryCondition} ${status.toLowerCase().replaceAll("_", " ")} drug studies`,
      url: url.toString(),
      status: "ok",
      count: body.studies?.length || 0,
      checked_at: new Date().toISOString()
    });
    all.push(...(body.studies || []));
  }

  return all;
}

async function fetchOpenFdaMeta(sourceLog) {
  const url = "https://api.fda.gov/drug/drugsfda.json?limit=1";
  const response = await fetch(url, { headers: { "Accept": "application/json" } });
  if (!response.ok) throw new Error(`openFDA ${response.status}`);
  const body = await response.json();
  sourceLog.push({
    source: "openFDA Drugs@FDA API",
    type: "Regulatory metadata",
    title: "Drugs@FDA API availability and last update",
    url,
    status: "ok",
    last_updated: body.meta?.last_updated || null,
    checked_at: new Date().toISOString()
  });
  return body.meta;
}

async function fetchApprovalContexts(assets, sourceLog, runDate) {
  const contexts = new Map();
  const uniqueNames = [...new Set(assets.map((asset) => asset.asset_name).map(baseIngredientName).filter((name) => name.length >= 4))];

  for (const name of uniqueNames) {
    const drugsFdaUrl = openFdaDrugsFdaUrl(name);
    const labelUrl = openFdaLabelUrl(name);
    try {
      const response = await fetch(drugsFdaUrl, { headers: { "Accept": "application/json" } });
      if (!response.ok) {
        contexts.set(approvalLookupKey(name), { status: "not_matched", query: name, url: drugsFdaUrl, detail: `openFDA Drugs@FDA ${response.status}` });
        continue;
      }
      const body = await response.json();
      const result = body.results?.[0];
      const originalApproval = originalApprovalSubmission(result?.submissions || []);
      const marketedProducts = (result?.products || []).filter((product) => /prescription|over-the-counter|otc/i.test(product.marketing_status || ""));
      if (!result?.openfda || !originalApproval || !marketedProducts.length) {
        contexts.set(approvalLookupKey(name), { status: "not_matched", query: name, url: drugsFdaUrl });
        continue;
      }

      const context = {
        status: "matched",
        query: name,
        url: drugsFdaUrl,
        label_url: labelUrl,
        checked_at: runDate.toISOString(),
        brand_names: result.openfda.brand_name || [],
        generic_names: result.openfda.generic_name || [],
        substance_names: result.openfda.substance_name || [],
        manufacturer_names: result.openfda.manufacturer_name || [],
        sponsor_name: result.sponsor_name || null,
        application_numbers: result.openfda.application_number || (result.application_number ? [result.application_number] : []),
        approval_date: formatFdaDate(originalApproval.submission_status_date),
        original_submission: originalApproval,
        marketing_statuses: [...new Set(marketedProducts.map((product) => product.marketing_status).filter(Boolean))],
        brand_product_names: [...new Set(marketedProducts.map((product) => product.brand_name).filter(Boolean))],
        source_date: body.meta?.last_updated || null
      };
      contexts.set(approvalLookupKey(name), context);
      sourceLog.push({
        source: "openFDA Drugs@FDA API",
        type: "Approval / marketed status",
        title: `${name} approval and marketing-status match`,
        url: drugsFdaUrl,
        status: "ok",
        matched_brand_names: context.brand_names,
        application_numbers: context.application_numbers,
        approval_date: context.approval_date,
        marketing_statuses: context.marketing_statuses,
        checked_at: runDate.toISOString()
      });
    } catch (error) {
      contexts.set(approvalLookupKey(name), { status: "error", query: name, url: drugsFdaUrl, detail: error.message });
    }
  }

  return contexts;
}

function openFdaDrugsFdaUrl(name) {
  const quoted = `"${name.replaceAll('"', '\\"')}"`;
  const url = new URL("https://api.fda.gov/drug/drugsfda.json");
  url.searchParams.set("search", `products.active_ingredients.name:${quoted}`);
  url.searchParams.set("limit", "1");
  return url.toString();
}

function openFdaLabelUrl(name) {
  const quoted = `"${name.replaceAll('"', '\\"')}"`;
  const search = `openfda.generic_name:${quoted}+openfda.substance_name:${quoted}+openfda.brand_name:${quoted}`;
  const url = new URL("https://api.fda.gov/drug/label.json");
  url.searchParams.set("search", search);
  url.searchParams.set("limit", "1");
  return url.toString();
}

function originalApprovalSubmission(submissions) {
  return submissions
    .filter((submission) => submission.submission_status === "AP")
    .sort((a, b) => {
      const aOrig = a.submission_type === "ORIG" ? 0 : 1;
      const bOrig = b.submission_type === "ORIG" ? 0 : 1;
      if (aOrig !== bOrig) return aOrig - bOrig;
      return String(a.submission_status_date || "").localeCompare(String(b.submission_status_date || ""));
    })[0] || null;
}

function formatFdaDate(value) {
  const text = String(value || "");
  return /^(\d{4})(\d{2})(\d{2})$/.test(text) ? `${text.slice(0, 4)}-${text.slice(4, 6)}-${text.slice(6, 8)}` : null;
}

function normalizeClinicalTrial(study, assignedArea, queryCondition, runDate) {
  const protocol = study.protocolSection || {};
  const id = protocol.identificationModule || {};
  const status = protocol.statusModule || {};
  const sponsor = protocol.sponsorCollaboratorsModule || {};
  const design = protocol.designModule || {};
  const conditions = protocol.conditionsModule?.conditions || [];
  const interventions = protocol.armsInterventionsModule?.interventions || [];
  const outcomes = protocol.outcomesModule?.primaryOutcomes || [];

  const drug = interventions.find((item) => /drug|biological|combination product/i.test(item.type || "")) || interventions[0] || {};
  const phase = normalizePhase(design.phases?.[0] || "Unknown");
  const area = assignedArea || classifyArea([queryCondition, ...conditions].join(" "));
  const launch = estimateLaunch(status.primaryCompletionDateStruct?.date, phase, runDate);
  const cost = estimateCost(area, drug.name || id.briefTitle || "Pipeline asset", phase);
  const differentiation = estimateClinicalDifferentiation(phase, outcomes, interventions);
  const budget = estimateBudgetImpact(area, cost.high, conditions);
  const risk = estimateRisk(launch.bucket, budget.level, differentiation.value, phase);
  const action = recommendAction(risk.value);
  const nctUrl = id.nctId ? `https://clinicaltrials.gov/study/${id.nctId}` : "https://clinicaltrials.gov/";
  const sponsorName = sponsor.leadSponsor?.name || sponsor.collaborators?.[0]?.name || "Not specified";
  const sponsorClass = sponsor.leadSponsor?.class || protocol.identificationModule?.organization?.class || "Not specified";

  return {
    asset_id: id.nctId || slugify(`${drug.name}-${id.briefTitle}`),
    asset_name: cleanAssetName(drug.name || id.briefTitle || "Pipeline asset"),
    manufacturer: sponsorName,
    sponsor_class: sponsorClass,
    therapeutic_area: area,
    indication: conditions[0] || titleCase(queryCondition),
    mechanism: drug.description ? summarize(drug.description, 120) : inferMechanism(drug.name || id.briefTitle || ""),
    phase,
    development_status: titleCase(String(status.overallStatus || "Unknown").replaceAll("_", " ")),
    expected_launch_window: launch.window,
    expected_launch_date: launch.date,
    launch_timeline_bucket: launch.bucket,
    launch_timeline_display: launch.display,
    estimated_launch_date_range: launch.dateRange,
    launch_timeline_confidence: launch.confidence,
    clinical_differentiation: differentiation.value,
    clinical_summary: summarize(outcomes[0]?.measure || id.briefTitle || "Primary endpoint details require analyst review.", 180),
    safety_summary: "Safety profile requires trial readout, label review, and comparator-specific assessment.",
    estimated_annual_cost_low: cost.low,
    estimated_annual_cost_high: cost.high,
    budget_impact_level: budget.level,
    disruption_risk: risk.value,
    recommended_action: action.value,
    management_tools: managementTools(area, risk.value, phase),
    evidence_gaps: evidenceGaps(phase, differentiation.value),
    rationale: {
      sponsor_filter: commercialSponsorRationale(sponsorName, sponsorClass),
      therapeutic_area: {
        value: area,
        method: "Assigned from configured refresh query; condition text is retained for analyst review.",
        source_fields: { refresh_query: queryCondition, conditions }
      },
      expected_launch_window: launch.rationale,
      launch_timeline: launch.timelineRationale,
      annual_cost_range: cost.rationale,
      clinical_differentiation: differentiation.rationale,
      budget_impact: budget.rationale,
      disruption_risk: risk.rationale,
      recommended_action: action.rationale
    },
    sources: [
      {
        title: id.briefTitle || id.nctId || "ClinicalTrials.gov study",
        source_id: id.nctId ? `ctgov:${id.nctId}` : null,
        type: "Clinical trial",
        url: nctUrl,
        date: status.lastUpdatePostDateStruct?.date || status.studyFirstPostDateStruct?.date || runDate.toISOString().slice(0, 10)
      }
    ]
  };
}

function parseArgs(argv) {
  const parsed = {};
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg.startsWith("--") && arg.includes("=")) {
      const [key, value] = arg.slice(2).split("=");
      parsed[key] = value;
    } else if (arg.startsWith("--")) {
      const key = arg.slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith("--")) {
        parsed[key] = next;
        i += 1;
      } else {
        parsed[key] = true;
      }
    }
  }
  return parsed;
}

function parseInterval(value) {
  const match = String(value).trim().match(/^(\d+(?:\.\d+)?)(m|h|d)?$/i);
  if (!match) throw new Error("Use interval formats such as 30m, 24h, or 7d.");
  const amount = Number(match[1]);
  const unit = (match[2] || "h").toLowerCase();
  const multipliers = { m: 60_000, h: 3_600_000, d: 86_400_000 };
  return amount * multipliers[unit];
}

function resolveAreaQueries(parsedArgs, appConfig) {
  if (parsedArgs.condition) {
    const condition = String(parsedArgs.condition);
    const area = classifyArea(condition);
    return { [area]: condition };
  }

  if (parsedArgs.areas) {
    const requested = String(parsedArgs.areas).split(",").map((area) => area.trim()).filter(Boolean);
    return Object.fromEntries(requested.map((area) => [area, appConfig.therapeuticAreaQueries?.[area] || area]));
  }

  return appConfig.therapeuticAreaQueries || {
    Oncology: "cancer",
    Immunology: "psoriasis",
    Cardiometabolic: "diabetes",
    Neurology: "migraine",
    Hematology: "sickle cell disease",
    Ophthalmology: "macular degeneration"
  };
}

function normalizePhase(phase) {
  const value = String(phase).replace("EARLY_PHASE1", "Phase 1").replace("PHASE", "Phase ").replaceAll("_", "/");
  if (/phase\s*3/i.test(value)) return "Phase 3";
  if (/phase\s*2/i.test(value)) return "Phase 2";
  if (/phase\s*1/i.test(value)) return "Phase 1";
  if (/phase\s*4/i.test(value)) return "Approved";
  return titleCase(value || "Unknown");
}

function classifyArea(text) {
  const value = text.toLowerCase();
  if (/cancer|tumor|oncolog|carcinoma|lymphoma|leukemia|melanoma|myeloma/.test(value)) return "Oncology";
  if (/arthritis|psoriasis|crohn|colitis|lupus|atopic|immun/.test(value)) return "Immunology";
  if (/diabetes|obesity|cardio|heart|lipid|renal|kidney/.test(value)) return "Cardiometabolic";
  if (/alzheimer|parkinson|seizure|migraine|neurolog|pain/.test(value)) return "Neurology";
  if (/sickle|hemophilia|anemia|thalassemia|hematolog|blood/.test(value)) return "Hematology";
  if (/retina|macular|glaucoma|ophthalm|eye/.test(value)) return "Ophthalmology";
  return "Other";
}

function estimateLaunch(primaryCompletionDate, phase, runDate) {
  if (!primaryCompletionDate) {
    return {
      date: null,
      window: "36+ months",
      bucket: "36+ months",
      display: "36+ months",
      dateRange: null,
      confidence: "Low",
      rationale: {
        value: "36+ months",
        method: "Planning estimate",
        explanation: "ClinicalTrials.gov did not provide a primary completion date in the ingested record, so the asset is placed in the longest launch-planning horizon pending analyst review.",
        source_fields: { primary_completion_date: null, phase }
      },
      timelineRationale: launchTimelineRationale("36+ months", "36+ months", null, "Low", "Planning estimate", "ClinicalTrials.gov did not provide a primary completion date in the ingested record, so the asset is placed in the longest launch-planning horizon pending analyst review.", { primary_completion_date: null, phase })
    };
  }

  const date = new Date(primaryCompletionDate);
  if (Number.isNaN(date.getTime())) {
    return {
      date: null,
      window: "36+ months",
      bucket: "36+ months",
      display: "36+ months",
      dateRange: null,
      confidence: "Low",
      rationale: {
        value: "36+ months",
        method: "Planning estimate",
        explanation: "ClinicalTrials.gov primary completion date was not parseable, so the asset is placed in the longest launch-planning horizon pending analyst review.",
        source_fields: { primary_completion_date: primaryCompletionDate, phase }
      },
      timelineRationale: launchTimelineRationale("36+ months", "36+ months", null, "Low", "Planning estimate", "ClinicalTrials.gov primary completion date was not parseable, so the asset is placed in the longest launch-planning horizon pending analyst review.", { primary_completion_date: primaryCompletionDate, phase })
    };
  }

  const months = phase === "Phase 3" ? 14 : phase === "Phase 2" ? 30 : phase === "Phase 1" ? 54 : 6;
  date.setMonth(date.getMonth() + months);
  const launchDate = date.toISOString().slice(0, 10);
  const window = getLaunchWindow(launchDate, runDate);
  const dateRange = { start: launchDate, end: launchDate, label: launchDate };

  return {
    date: launchDate,
    window,
    bucket: normalizedLaunchBucket(window),
    display: window,
    dateRange,
    confidence: "Medium",
    rationale: {
      value: window,
      method: "Derived estimate from ClinicalTrials.gov primary completion date plus phase-specific lag",
      explanation: `Expected launch date is estimated as primary completion date plus ${months} months for ${phase}; the resulting date is bucketed relative to the refresh date.`,
      source_fields: {
        primary_completion_date: primaryCompletionDate,
        phase,
        added_months: months,
        estimated_launch_date: launchDate,
        refresh_date: runDate.toISOString().slice(0, 10)
      }
    },
    timelineRationale: launchTimelineRationale(normalizedLaunchBucket(window), window, dateRange, "Medium", "Derived estimate from ClinicalTrials.gov primary completion date plus phase-specific lag", `Expected launch date is estimated as primary completion date plus ${months} months for ${phase}; the resulting date is bucketed relative to the refresh date.`, {
      primary_completion_date: primaryCompletionDate,
      phase,
      added_months: months,
      estimated_launch_date: launchDate,
      refresh_date: runDate.toISOString().slice(0, 10)
    })
  };
}

function getLaunchWindow(launchDate, runDate) {
  const months = (new Date(launchDate) - runDate) / (1000 * 60 * 60 * 24 * 30.44);
  if (months <= 0) return "Launched";
  if (months <= 12) return "0-12 months";
  if (months <= 24) return "12-24 months";
  if (months <= 36) return "24-36 months";
  return "36+ months";
}

function launchTimelineRationale(bucket, display, dateRange, confidence, method, explanation, sourceFields = {}) {
  return {
    value: bucket,
    method,
    explanation,
    basis_type: "source_derived",
    source_fields: {
      ...sourceFields,
      launch_timeline_bucket: bucket,
      launch_timeline_display: display,
      estimated_launch_date_range: dateRange,
      launch_timeline_confidence: confidence
    }
  };
}

function estimateCost(area, name, phase) {
  const base = {
    Oncology: [140000, 260000],
    Immunology: [38000, 78000],
    Cardiometabolic: [7200, 16800],
    Neurology: [18000, 90000],
    Hematology: [120000, 480000],
    Ophthalmology: [18000, 72000],
    Other: [12000, 80000]
  }[area] || [12000, 80000];
  const isCellOrGene = /car-t|cart|cell|gene|vector|crispr|lentiviral/i.test(name);
  const multiplier = isCellOrGene ? 2.4 : phase === "Phase 1" ? 0.75 : 1;
  const low = Math.round(base[0] * multiplier / 100) * 100;
  const high = Math.round(base[1] * multiplier / 100) * 100;
  return {
    low,
    high,
    rationale: {
      value: `${low}-${high}`,
      method: "Therapeutic-area analog planning estimate",
      explanation: "Annual cost is not sourced from ClinicalTrials.gov. It is a placeholder range based on the product's therapeutic-area cost archetype, adjusted for cell/gene therapy signals and early-phase uncertainty.",
      source_fields: { therapeutic_area: area, asset_name: name, phase, base_range: base, multiplier, cell_or_gene_signal: isCellOrGene }
    }
  };
}

function estimateClinicalDifferentiation(phase, outcomes, interventions) {
  let score = phase === "Phase 3" ? 3 : phase === "Phase 2" ? 2 : 1;
  if (outcomes.length > 1) score += 1;
  if (interventions.length > 1) score += 1;
  const value = score >= 5 ? "High" : score >= 3 ? "Meaningful" : score === 2 ? "Modest" : "Low";
  return {
    value,
    rationale: {
      value,
      method: "Heuristic score from phase and ClinicalTrials.gov endpoint/intervention structure",
      explanation: "Clinical differentiation is a triage estimate, not a readout-based conclusion. Higher phase, multiple primary outcomes, and multiple interventions increase the score.",
      source_fields: { phase, primary_outcome_count: outcomes.length, intervention_count: interventions.length, score }
    }
  };
}

function estimateBudgetImpact(area, highCost, conditions) {
  const broad = conditions.join(" ").toLowerCase();
  const broadPopulationSignal = /obesity|diabetes|heart failure|asthma|atopic/.test(broad);
  const value = highCost > 250000 || broadPopulationSignal ? "High" : highCost > 60000 || ["Oncology", "Immunology", "Hematology"].includes(area) ? "Medium" : "Low";
  return {
    level: value,
    rationale: {
      value,
      method: "Heuristic from estimated high-end annual cost, therapeutic area, and broad-population condition signals",
      explanation: "Budget impact is a planning classification. It uses the generated cost range and broad condition keywords until plan-specific prevalence, lives, and uptake are connected.",
      source_fields: { therapeutic_area: area, high_cost: highCost, conditions, broad_population_signal: broadPopulationSignal }
    }
  };
}

function estimateRisk(window, budgetImpact, differentiation, phase) {
  let score = 0;
  if (["0-12 months", "12-24 months", "Launched"].includes(window)) score += 2;
  if (window === "24-36 months") score += 1;
  if (budgetImpact === "High") score += 2;
  if (budgetImpact === "Medium") score += 1;
  if (["High", "Meaningful"].includes(differentiation)) score += 1;
  if (phase === "Phase 3") score += 1;
  const value = score >= 5 ? "High" : score >= 3 ? "Medium" : "Low";
  return {
    value,
    rationale: {
      value,
      method: "Weighted formulary-readiness score",
      explanation: "Risk combines launch proximity, budget impact, clinical differentiation, and Phase 3 readiness. It is intended to prioritize review, not replace payer committee judgment.",
      source_fields: { launch_window: window, budget_impact: budgetImpact, clinical_differentiation: differentiation, phase, score }
    }
  };
}

function recommendAction(risk) {
  const value = risk === "High" ? "Actively Plan" : risk === "Medium" ? "Prepare" : "Monitor";
  const explanation = {
    "Actively Plan": "High-risk assets should move into scenario modeling, evidence-gap review, contracting watch, and draft utilization-management planning.",
    Prepare: "Medium-risk assets should be tracked with evidence updates, analog price checks, and preliminary policy considerations.",
    Monitor: "Low-risk assets should remain in routine pipeline monitoring until launch proximity, evidence maturity, or cost signals change."
  }[value];
  return {
    value,
    rationale: {
      value,
      method: "Mapped from disruption risk",
      explanation,
      source_fields: { disruption_risk: risk }
    }
  };
}

function managementTools(area, risk, phase) {
  const tools = risk === "High" ? ["PA", "ST", "QL"] : risk === "Medium" ? ["PA", "QL"] : ["Monitor"];
  if (["Oncology", "Hematology", "Ophthalmology"].includes(area) || /phase 3/i.test(phase)) tools.push("SP");
  return [...new Set(tools)];
}

function evidenceGaps(phase, differentiation) {
  const gaps = ["Comparative effectiveness versus standard of care", "Real-world persistence and adherence"];
  if (phase !== "Approved") gaps.unshift("Final label, indication breadth, and safety language");
  if (["High", "Meaningful"].includes(differentiation)) gaps.push("Budget impact under alternative uptake scenarios");
  return gaps;
}

function filterCommercialSponsors(assets) {
  const excluded = [];
  const kept = [];

  for (const asset of assets) {
    if (isCommercialSponsor(asset.manufacturer, asset.sponsor_class)) {
      kept.push(asset);
    } else {
      excluded.push({
        asset_id: asset.asset_id,
        asset_name: asset.asset_name,
        manufacturer: asset.manufacturer,
        sponsor_class: asset.sponsor_class,
        therapeutic_area: asset.therapeutic_area,
        reason: "Lead sponsor did not appear to be a pharma/biotech company"
      });
    }
  }

  return { assets: kept, excluded };
}

function groupAssetsByDrug(assets) {
  const grouped = new Map();

  for (const asset of assets) {
    const key = [
      approvalLookupKey(asset.asset_name),
      asset.manufacturer.toLowerCase(),
      asset.therapeutic_area,
      normalizeIndication(asset.indication)
    ].join("|");
    const existing = grouped.get(key);

    if (!existing) {
      grouped.set(key, {
        ...asset,
        clinical_trial_links: (asset.sources || []).filter((source) => source.type === "Clinical trial"),
        supporting_study_count: 1
      });
      continue;
    }

    existing.supporting_study_count += 1;
    existing.sources = mergeSources(existing.sources, asset.sources);
    existing.clinical_trial_links = mergeSources(existing.clinical_trial_links, asset.sources?.filter((source) => source.type === "Clinical trial") || []);
    existing.phase = highestPhase(existing.phase, asset.phase);
    existing.expected_launch_date = earliestDate(existing.expected_launch_date, asset.expected_launch_date);
    existing.expected_launch_window = earliestLaunchWindow(existing.expected_launch_window, asset.expected_launch_window);
    existing.launch_timeline_bucket = earliestLaunchWindow(existing.launch_timeline_bucket, asset.launch_timeline_bucket);
    existing.launch_timeline_display = existing.launch_timeline_display || asset.launch_timeline_display || existing.expected_launch_window;
    existing.estimated_launch_date_range = existing.estimated_launch_date_range || asset.estimated_launch_date_range || null;
    existing.launch_timeline_confidence = highestConfidence(existing.launch_timeline_confidence, asset.launch_timeline_confidence);
    existing.clinical_differentiation = highestDifferentiation(existing.clinical_differentiation, asset.clinical_differentiation);
    existing.disruption_risk = highestRisk(existing.disruption_risk, asset.disruption_risk);
    existing.recommended_action = existing.disruption_risk === "High" ? "Actively Plan" : existing.disruption_risk === "Medium" ? "Prepare" : "Monitor";
    existing.rationale.expected_launch_window.explanation = `Aggregated from ${existing.supporting_study_count} ClinicalTrials.gov study record(s). Earliest estimated launch window among retained studies is ${existing.expected_launch_window}.`;
    existing.rationale.expected_launch_window.source_fields.supporting_study_count = existing.supporting_study_count;
    existing.rationale.expected_launch_window.source_fields.ctgov_urls = existing.clinical_trial_links.map((source) => source.url);
    existing.rationale.launch_timeline = existing.rationale.launch_timeline || existing.rationale.expected_launch_window;
    existing.rationale.launch_timeline.explanation = `Aggregated from ${existing.supporting_study_count} ClinicalTrials.gov study record(s). Earliest normalized launch timeline bucket among retained studies is ${existing.launch_timeline_bucket}.`;
    existing.rationale.launch_timeline.source_fields.supporting_study_count = existing.supporting_study_count;
    existing.rationale.launch_timeline.source_fields.ctgov_urls = existing.clinical_trial_links.map((source) => source.url);
    existing.rationale.disruption_risk.source_fields.supporting_study_count = existing.supporting_study_count;
  }

  return [...grouped.values()];
}

function applyApprovalContext(asset, approvalContext, runDate) {
  if (!approvalContext || approvalContext.status !== "matched") return asset;

  const marketedSource = {
    title: `${asset.asset_name} openFDA Drugs@FDA record`,
    source_id: approvalContext.application_numbers?.[0] ? `openfda:${approvalContext.application_numbers[0]}` : `openfda:${approvalLookupKey(asset.asset_name)}`,
    type: "FDA approval / marketed status",
    url: approvalContext.url,
    date: approvalContext.approval_date || approvalContext.source_date || runDate.toISOString().slice(0, 10),
    supports: ["marketed_status", "approval_context"]
  };
  const updated = {
    ...asset,
    marketed_status: "FDA-approved / marketed",
    approval_context: approvalContext,
    development_status: `FDA-approved / marketed; ${asset.development_status} study`,
    expected_launch_window: "Marketed",
    expected_launch_date: approvalContext.approval_date || asset.expected_launch_date,
    launch_timeline_bucket: "0-12 months",
    launch_timeline_display: "Marketed",
    estimated_launch_date_range: approvalContext.approval_date ? { start: approvalContext.approval_date, end: approvalContext.approval_date, label: approvalContext.approval_date } : null,
    launch_timeline_confidence: "High",
    recommended_action: asset.disruption_risk === "High" ? "Prepare" : asset.recommended_action,
    sources: mergeSources(asset.sources, [marketedSource])
  };
  updated.rationale = {
    ...asset.rationale,
    expected_launch_window: {
      value: "Marketed",
      method: "openFDA Drugs@FDA approval / marketed-product override",
      explanation: `openFDA Drugs@FDA matched ${asset.asset_name} to FDA-approved marketed product record(s) (${approvalContext.brand_names.join(", ") || "brand not listed"}; ${approvalContext.application_numbers.join(", ") || "application not listed"}; approval date ${approvalContext.approval_date || "not listed"}; marketing status ${approvalContext.marketing_statuses.join(", ") || "not listed"}). Ongoing ClinicalTrials.gov studies are treated as post-approval or label-expansion evidence, not initial launch timing.`,
      source_fields: {
        openfda_query: approvalContext.query,
        brand_names: approvalContext.brand_names,
        generic_names: approvalContext.generic_names,
        manufacturer_names: approvalContext.manufacturer_names,
        application_numbers: approvalContext.application_numbers,
        approval_date: approvalContext.approval_date,
        marketing_statuses: approvalContext.marketing_statuses,
        openfda_drugsfda_url: approvalContext.url,
        ctgov_urls: updated.clinical_trial_links?.map((source) => source.url) || []
      }
    },
    launch_timeline: {
      value: "0-12 months",
      method: "openFDA Drugs@FDA approval / marketed-product override",
      explanation: "Marketed products are mapped to the nearest launch timeline bucket only for exclusion and pipeline-scope handling; active dashboard assets should not include marketed products.",
      source_fields: {
        approval_date: approvalContext.approval_date,
        marketed_statuses: approvalContext.marketing_statuses,
        openfda_drugsfda_url: approvalContext.url,
        ctgov_urls: updated.clinical_trial_links?.map((source) => source.url) || []
      }
    },
    recommended_action: {
      value: updated.recommended_action,
      method: "Mapped from marketed status and residual pipeline risk",
      explanation: "Because the product is already FDA-approved / marketed, action focuses on monitoring ongoing studies, label-expansion signals, and utilization-management implications rather than initial launch preparation.",
      source_fields: { marketed_status: updated.marketed_status, disruption_risk: updated.disruption_risk }
    }
  };
  return updated;
}

function applyResearchOverrides(assets, researchOverrides, runDate) {
  const overrides = researchOverrides?.overrides || {};
  return assets.map((asset) => {
    const override = overrides[asset.asset_id] || overrides[approvalLookupKey(asset.asset_name)];
    if (!override) return asset;

    const mergedSources = mergeSources(asset.sources, override.sources || []);
    const mergedRationale = { ...asset.rationale };
    for (const [key, value] of Object.entries(override.rationale || {})) {
      mergedRationale[key] = normalizeRationale(value, value.basis_type || "source_derived", override, mergedSources);
    }
    if (override.launch_timeline_rationale) {
      mergedRationale.launch_timeline = normalizeRationale(override.launch_timeline_rationale, override.launch_timeline_rationale?.basis_type || "source_derived", override, mergedSources);
    }

    const updated = {
      ...asset,
      ...pickOverrideFields(override),
      sources: mergedSources,
      clinical_trial_links: mergeSources(asset.clinical_trial_links, (override.sources || []).filter((source) => source.type === "Clinical trial")),
      rationale: mergedRationale,
      research_status: override.research_status || "source_backed",
      research_agent: override.research_agent || null,
      research_checked_at: override.checked_at || runDate.toISOString()
    };

    const costValue = updated.rationale?.annual_cost_range?.value;
    if (costValue && /^\d+-\d+$/.test(String(costValue))) {
      const [low, high] = String(costValue).split("-").map(Number);
      updated.estimated_annual_cost_low = low;
      updated.estimated_annual_cost_high = high;
    }

    if (override.launch_timeline_bucket) {
      updated.launch_timeline_bucket = normalizedLaunchBucket(override.launch_timeline_bucket, override.launch_timeline_display || override.expected_launch_window, runDate);
      updated.launch_timeline_display = override.launch_timeline_display || override.expected_launch_window || updated.expected_launch_window;
      updated.estimated_launch_date_range = override.estimated_launch_date_range || updated.estimated_launch_date_range || null;
      updated.launch_timeline_confidence = override.launch_timeline_confidence || updated.launch_timeline_confidence || "Medium";
    } else if (override.expected_launch_window || override.rationale?.expected_launch_window) {
      const display = override.expected_launch_window || updated.expected_launch_window;
      const bucket = bucketFromLaunchText(display, runDate);
      updated.launch_timeline_bucket = bucket;
      updated.launch_timeline_display = display || bucket;
      updated.estimated_launch_date_range = override.estimated_launch_date_range || updated.estimated_launch_date_range || null;
      updated.launch_timeline_confidence = override.launch_timeline_confidence || updated.launch_timeline_confidence || "Medium";
      const basis = override.rationale?.expected_launch_window || {
        method: "Source-backed asset research packet",
        explanation: "Normalized launch timeline bucket derived from the asset-level source-backed expected launch timing."
      };
      mergedRationale.launch_timeline = normalizeRationale({
        ...basis,
        value: bucket,
        source_fields: {
          ...(basis.source_fields || {}),
          expected_launch_window: display,
          launch_timeline_bucket: bucket,
          launch_timeline_display: updated.launch_timeline_display,
          estimated_launch_date_range: updated.estimated_launch_date_range,
          launch_timeline_confidence: updated.launch_timeline_confidence
        }
      }, basis.basis_type || "source_derived", override, mergedSources, runDate);
    }

    return updated;
  });
}

function filterPipelineAssets(assets) {
  const excluded = [];
  const kept = [];

  for (const asset of assets) {
    if (isNonPipelineAsset(asset)) {
      excluded.push({
        asset_id: asset.asset_id,
        asset_name: asset.asset_name,
        manufacturer: asset.manufacturer,
        therapeutic_area: asset.therapeutic_area,
        phase: asset.phase,
        expected_launch_window: asset.expected_launch_window,
        development_status: asset.development_status,
        reason: exclusionReason(asset)
      });
    } else {
      kept.push(asset);
    }
  }

  return { assets: kept, excluded };
}

function isNonPipelineAsset(asset) {
  const text = [
    asset.phase,
    asset.expected_launch_window,
    asset.development_status,
    asset.marketed_status,
    asset.rationale?.expected_launch_window?.value,
    ...(asset.quality_flags || [])
  ].join(" ");
  return /\bapproved\b|marketed|launched|discontinued|terminated|asset sale|sold program|no launch|no forecast|device|diagnostic|supplement|non-drug|not a drug|not a pipeline|not a pipeline development asset|reference product|biosimilar\/process-change/i.test(text);
}

function exclusionReason(asset) {
  const text = [
    asset.phase,
    asset.expected_launch_window,
    asset.development_status,
    asset.marketed_status,
    asset.rationale?.expected_launch_window?.value,
    ...(asset.quality_flags || [])
  ].join(" ");
  if (/device|diagnostic|supplement|non-drug|not a drug/i.test(text)) {
    return "Excluded because the record is a device, diagnostic, supplement, or other non-drug treatment rather than a pipeline drug asset";
  }
  if (/reference product|biosimilar\/process-change/i.test(text)) {
    return "Excluded because the record is a biosimilar/process-change or reference-product study rather than a novel pipeline asset";
  }
  if (/discontinued|terminated|asset sale|sold program|no launch|no forecast/i.test(text)) {
    return "Excluded because source-backed research indicates the program is discontinued, terminated, sold, or no longer forecast as an active pipeline asset";
  }
  return "Excluded because the record is already marketed, launched, or FDA-approved rather than an active pipeline asset";
}

function pickOverrideFields(override) {
  const fields = [
    "mechanism",
    "phase",
    "development_status",
    "expected_launch_window",
    "expected_launch_date",
    "launch_timeline_bucket",
    "launch_timeline_display",
    "estimated_launch_date_range",
    "launch_timeline_confidence",
    "clinical_differentiation",
    "clinical_summary",
    "safety_summary",
    "estimated_annual_cost_low",
    "estimated_annual_cost_high",
    "budget_impact_level",
    "disruption_risk",
    "recommended_action",
    "management_tools",
    "evidence_gaps",
    "quality_flags"
  ];
  return Object.fromEntries(fields.filter((field) => Object.hasOwn(override, field)).map((field) => [field, override[field]]));
}

function ensureProvenance(asset, runDate) {
  const sources = (asset.sources || []).map((source) => ({
    ...source,
    source_id: source.source_id || inferSourceId(source)
  }));
  const rationale = {};
  for (const [key, value] of Object.entries(asset.rationale || {})) {
    rationale[key] = normalizeRationale(value, inferBasisType(key, value), asset, sources, runDate);
  }

  const bucket = normalizedLaunchBucket(asset.launch_timeline_bucket || bucketFromLaunchText(asset.expected_launch_window, runDate));
  const display = asset.launch_timeline_display || asset.expected_launch_window || bucket;
  if (!rationale.launch_timeline) {
    rationale.launch_timeline = normalizeRationale(launchTimelineRationale(bucket, display, asset.estimated_launch_date_range || null, asset.launch_timeline_confidence || "Low", "Derived from existing launch timing display", "No asset-level launch timeline packet was available, so the normalized bucket was derived from the existing expected launch display for charting and filtering.", {
      expected_launch_window: asset.expected_launch_window,
      expected_launch_date: asset.expected_launch_date
    }), "heuristic", asset, sources, runDate);
  }

  return {
    ...asset,
    launch_timeline_bucket: bucket,
    launch_timeline_display: display,
    estimated_launch_date_range: asset.estimated_launch_date_range || null,
    launch_timeline_confidence: asset.launch_timeline_confidence || "Low",
    sources,
    clinical_trial_links: (asset.clinical_trial_links || []).map((source) => ({
      ...source,
      source_id: source.source_id || inferSourceId(source)
    })),
    rationale,
    research_status: asset.research_status || "pending_subagent_research",
    research_agent: asset.research_agent || null
  };
}

function normalizeRationale(rationale, basisType, context = {}, sources = [], runDate = new Date()) {
  const normalized = typeof rationale === "string" ? {
    value: context.launch_timeline_bucket || context.expected_launch_window || "",
    method: "Source-backed asset research packet",
    explanation: rationale
  } : (rationale || {});
  const sourceRefs = normalized.source_refs || inferSourceRefs(normalized, sources);
  const existingAgent = typeof normalized.research_agent === "object" ? normalized.research_agent : null;
  const agentId = existingAgent?.id || normalized.research_agent || context.research_agent;
  return {
    ...normalized,
    basis_type: basisType,
    source_refs: sourceRefs,
    research_agent: agentId ? {
      id: agentId,
      checked_at: existingAgent?.checked_at || context.checked_at || context.research_checked_at || runDate.toISOString()
    } : undefined,
    review_required: rationale.review_required ?? basisType === "heuristic"
  };
}

function inferBasisType(key, rationale) {
  if (rationale?.basis_type) return rationale.basis_type;
  if (key === "launch_timeline") return "source_derived";
  if (key === "expected_launch_window" && /openFDA|approval|marketed/i.test(`${rationale?.method || ""} ${rationale?.explanation || ""}`)) return "source_direct";
  if (key === "expected_launch_window" && /ClinicalTrials\.gov primary completion date/i.test(rationale?.explanation || "")) return "source_derived";
  if (key === "sponsor_filter" || key === "therapeutic_area") return "source_derived";
  return "heuristic";
}

function normalizedLaunchBucket(value, display = "", runDate = new Date()) {
  if (launchTimelineBuckets.includes(value)) return value;
  return bucketFromLaunchText(`${value || ""} ${display || ""}`, runDate);
}

function bucketFromLaunchText(value, runDate = new Date()) {
  const text = String(value || "");
  if (launchTimelineBuckets.includes(text)) return text;
  if (/marketed|launched/i.test(text)) return "0-12 months";
  const yearMatch = text.match(/\b(20\d{2})(?:[-/](\d{1,2})(?:[-/](\d{1,2}))?)?\b/);
  if (!yearMatch) return "36+ months";
  const year = Number(yearMatch[1]);
  const quarter = Number(text.match(/\bQ([1-4])\b/i)?.[1]);
  const month = Number(yearMatch[2] || (quarter ? quarter * 3 - 1 : 7));
  const day = Number(yearMatch[3] || 1);
  const estimateDate = new Date(Date.UTC(year, Math.max(0, month - 1), day));
  const months = (estimateDate - runDate) / (1000 * 60 * 60 * 24 * 30.44);
  if (months <= 12) return "0-12 months";
  if (months <= 24) return "12-24 months";
  if (months <= 36) return "24-36 months";
  return "36+ months";
}

function validateLaunchTimelineBuckets(assets) {
  const invalid = assets.filter((asset) => !launchTimelineBuckets.includes(asset.launch_timeline_bucket));
  if (invalid.length) {
    throw new Error(`Invalid launch_timeline_bucket for ${invalid.map((asset) => `${asset.asset_id}:${asset.launch_timeline_bucket}`).join(", ")}`);
  }
}

function inferSourceRefs(rationale, sources) {
  const refs = new Set();
  const fields = rationale?.source_fields || {};
  for (const url of fields.ctgov_urls || []) {
    const nct = String(url).match(/NCT\d{8}/i)?.[0];
    if (nct) refs.add(`ctgov:${nct.toUpperCase()}`);
  }
  for (const app of fields.application_numbers || []) refs.add(`openfda:${app}`);
  for (const source of sources || []) {
    const id = source.source_id || inferSourceId(source);
    if (id && /source|approval|marketed|ClinicalTrials|sponsor/i.test(`${rationale?.method || ""} ${rationale?.explanation || ""}`)) refs.add(id);
  }
  return [...refs];
}

function inferSourceId(source) {
  const text = `${source?.url || ""} ${source?.title || ""}`;
  const nct = text.match(/NCT\d{8}/i)?.[0];
  if (nct) return `ctgov:${nct.toUpperCase()}`;
  const app = text.match(/\b(?:BLA|NDA)\d{6}\b/i)?.[0];
  if (app && /openfda|drugsfda/i.test(text)) return `openfda:${app.toUpperCase()}`;
  return null;
}

function createResearchAssignments(assets, researchOverrides, runDate) {
  const overrides = researchOverrides?.overrides || {};
  return assets.map((asset) => {
    const override = overrides[asset.asset_id] || overrides[approvalLookupKey(asset.asset_name)];
    return {
      asset_id: asset.asset_id,
      asset_name: asset.asset_name,
      manufacturer: asset.manufacturer,
      therapeutic_area: asset.therapeutic_area,
      indication: asset.indication,
      status: override ? "complete" : "pending",
      assigned_agent: override?.research_agent || "new subagent required",
      checked_at: override?.checked_at || null,
      required_outputs: [
        "mechanism",
        "expected launch / marketed timing",
        "clinical profile",
        "annual cost range",
        "budget impact and disruption risk",
        "recommended action",
        "evidence gaps",
        "management tools",
        "direct CT.gov links and supporting sources"
      ],
      source_seed_urls: (asset.sources || []).map((source) => source.url).filter(Boolean),
      prompt: `Assign a new subagent to research ${asset.asset_name} (${asset.asset_id}) and return source-backed values for the dashboard detail pane. Checked from refresh ${runDate.toISOString()}.`
    };
  });
}

function mergeSources(left = [], right = []) {
  const seen = new Set();
  const merged = [];
  for (const source of [...left, ...right]) {
    const key = source.url || `${source.title}-${source.date}`;
    if (seen.has(key)) continue;
    seen.add(key);
    merged.push(source);
  }
  return merged;
}

function normalizeIndication(value) {
  return String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function baseIngredientName(name) {
  return String(name || "")
    .split(/\s+(?:and|plus|with|\+|,)\s+/i)[0]
    .replace(/\b\d+(\.\d+)?\s*(mg|mcg|g|ml)\b/gi, "")
    .replace(/\([^)]*\)/g, "")
    .trim();
}

function approvalLookupKey(name) {
  return baseIngredientName(name).toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function highestPhase(a, b) {
  const order = { Unknown: 0, "Phase 1": 1, "Phase 2": 2, "Phase 3": 3, Approved: 4 };
  return (order[b] || 0) > (order[a] || 0) ? b : a;
}

function earliestDate(a, b) {
  if (!a) return b || null;
  if (!b) return a;
  return new Date(b) < new Date(a) ? b : a;
}

function earliestLaunchWindow(a, b) {
  const order = { Marketed: -1, Launched: 0, "0-12 months": 1, "12-24 months": 2, "24-36 months": 3, "36+ months": 4 };
  return (order[b] ?? 99) < (order[a] ?? 99) ? b : a;
}

function highestConfidence(a, b) {
  const order = { Low: 1, Medium: 2, High: 3 };
  return (order[b] || 0) > (order[a] || 0) ? b : a;
}

function highestDifferentiation(a, b) {
  const order = { Low: 1, Modest: 2, Meaningful: 3, High: 4 };
  return (order[b] || 0) > (order[a] || 0) ? b : a;
}

function highestRisk(a, b) {
  const order = { Low: 1, Medium: 2, High: 3 };
  return (order[b] || 0) > (order[a] || 0) ? b : a;
}

function isCommercialSponsor(name, sponsorClass) {
  const sponsor = String(name || "").toLowerCase();
  const sponsorType = String(sponsorClass || "").toUpperCase();
  if (sponsorType === "INDUSTRY") return true;
  if (/(university|college|hospital|clinic|medical center|cancer center|institute|institut|foundation|cooperative group|government|nih|national cancer institute|ministry|department|school of medicine|health system|research center|centre hospital|academ)/i.test(sponsor)) return false;
  return /(pharma|pharmaceutical|therapeutics|biotech|bioscience|biopharma|biomed|oncology|laboratories|laboratory|inc\.?$|corp\.?$|ltd\.?$|limited|gmbh|ag$|sa$|sas$|plc|llc|co\.,? ltd|company|abbvie|amgen|astrazeneca|bayer|biogen|bms|boehringer|daiichi|eli lilly|gilead|gsk|janssen|merck|novartis|novo nordisk|pfizer|regeneron|roche|sanofi|takeda|vertex)/i.test(sponsor);
}

function commercialSponsorRationale(name, sponsorClass) {
  return {
    value: isCommercialSponsor(name, sponsorClass) ? "Included" : "Excluded",
    method: "ClinicalTrials.gov sponsor class and name-pattern screening",
    explanation: "Included when the lead sponsor is classed as INDUSTRY or the sponsor name matches a pharma/biotech company pattern; academic medical centers, hospitals, universities, institutes, foundations, and government sponsors are excluded.",
    source_fields: { manufacturer: name, sponsor_class: sponsorClass }
  };
}

function cleanAssetName(name) {
  return String(name || "Pipeline asset").replace(/^drug:\s*/i, "").replace(/\s+/g, " ").trim();
}

function inferMechanism(name) {
  if (/antibody|mab\b/i.test(name)) return "Antibody-based therapy";
  if (/car-t|cart|cell/i.test(name)) return "Cell therapy";
  if (/gene|vector|crispr/i.test(name)) return "Gene or genetic medicine";
  if (/inhibitor/i.test(name)) return "Small-molecule inhibitor";
  return "Mechanism requires source review";
}

function summarize(text, max) {
  const clean = String(text || "").replace(/\s+/g, " ").trim();
  return clean.length > max ? `${clean.slice(0, max - 1).trim()}...` : clean;
}

function dedupeAssets(assets) {
  const seen = new Set();
  return assets.filter((asset) => {
    const key = asset.asset_id || `${asset.asset_name}-${asset.indication}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function slugify(value) {
  return String(value || "asset").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

function titleCase(value) {
  return String(value || "").toLowerCase().replace(/\b[a-z]/g, (char) => char.toUpperCase());
}

function toCsv(rows) {
  const columns = [
    "rank",
    "asset_id",
    "asset_name",
    "ctgov_urls",
    "manufacturer",
    "sponsor_class",
    "therapeutic_area",
    "indication",
    "phase",
    "development_status",
    "marketed_status",
    "expected_launch_window",
    "expected_launch_date",
    "launch_timeline_bucket",
    "launch_timeline_display",
    "launch_timeline_confidence",
    "estimated_launch_date_range",
    "clinical_differentiation",
    "estimated_annual_cost_low",
    "estimated_annual_cost_high",
    "budget_impact_level",
    "disruption_risk",
    "recommended_action",
    "expected_launch_rationale",
    "expected_launch_basis_type",
    "expected_launch_source_refs",
    "launch_timeline_rationale",
    "launch_timeline_basis_type",
    "launch_timeline_source_refs",
    "annual_cost_rationale",
    "annual_cost_basis_type",
    "annual_cost_source_refs",
    "risk_rationale",
    "risk_basis_type",
    "risk_source_refs",
    "action_rationale",
    "action_basis_type",
    "action_source_refs",
    "research_status",
    "research_agent"
  ];
  const lines = [columns.join(",")];
  for (const row of rows) {
    lines.push(columns.map((column) => csvEscape(csvValue(row, column))).join(","));
  }
  return `${lines.join("\n")}\n`;
}

function csvValue(row, column) {
  const rationaleMap = {
    expected_launch_rationale: row.rationale?.expected_launch_window?.explanation,
    expected_launch_basis_type: row.rationale?.expected_launch_window?.basis_type,
    expected_launch_source_refs: (row.rationale?.expected_launch_window?.source_refs || []).join("; "),
    launch_timeline_rationale: row.rationale?.launch_timeline?.explanation,
    launch_timeline_basis_type: row.rationale?.launch_timeline?.basis_type,
    launch_timeline_source_refs: (row.rationale?.launch_timeline?.source_refs || []).join("; "),
    estimated_launch_date_range: row.estimated_launch_date_range ? JSON.stringify(row.estimated_launch_date_range) : "",
    annual_cost_rationale: row.rationale?.annual_cost_range?.explanation,
    annual_cost_basis_type: row.rationale?.annual_cost_range?.basis_type,
    annual_cost_source_refs: (row.rationale?.annual_cost_range?.source_refs || []).join("; "),
    risk_rationale: row.rationale?.disruption_risk?.explanation,
    risk_basis_type: row.rationale?.disruption_risk?.basis_type,
    risk_source_refs: (row.rationale?.disruption_risk?.source_refs || []).join("; "),
    action_rationale: row.rationale?.recommended_action?.explanation,
    action_basis_type: row.rationale?.recommended_action?.basis_type,
    action_source_refs: (row.rationale?.recommended_action?.source_refs || []).join("; "),
    ctgov_urls: (row.clinical_trial_links || []).map((source) => source.url).join("; ")
  };
  return Object.hasOwn(rationaleMap, column) ? rationaleMap[column] : row[column];
}

function csvEscape(value) {
  const text = value == null ? "" : String(value);
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}
