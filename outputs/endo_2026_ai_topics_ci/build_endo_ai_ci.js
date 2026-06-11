const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const OUT_DIR = __dirname;
const DATA_DIR = "C:\\Users\\Justin\\Desktop\\endo-2026\\data";
const JSON_PATH = path.join(DATA_DIR, "conference_records.json");
const MD_PATH = path.join(DATA_DIR, "conference_records.md");
const SOURCE_LOG_PATH = "C:\\Users\\Justin\\Desktop\\endo-2026\\source-log.json";
const VALIDATION_PATH = "C:\\Users\\Justin\\Desktop\\endo-2026\\validation-report.json";

const TERMS = [
  ["artificial intelligence", /\bartificial intelligence\b/gi],
  ["AI", /\bAI\b/g],
  ["machine learning", /\bmachine learning\b/gi],
  ["ML", /\bML\b/g],
  ["deep learning", /\bdeep learning\b/gi],
  ["neural network", /\bneural networks?\b/gi],
  ["algorithm", /\balgorithms?\b/gi],
  ["automated", /\bautomated\b/gi],
  ["prediction model", /\bprediction models?\b/gi],
  ["image analysis", /\bimage analysis\b/gi],
  ["radiomics", /\bradiomics\b/gi],
  ["NLP", /\bNLP\b/g],
  ["chatbot", /\bchatbots?\b/gi],
  ["LLM", /\bLLMs?\b/g],
  ["large language model", /\blarge language models?\b/gi],
  ["retrieval-augmented generation", /\bretrieval[- ]augmented generation\b/gi],
  ["RAG", /\bRAG\b/g],
  ["digital pathology", /\bdigital pathology\b/gi],
  ["computer-aided", /\bcomputer[- ]aided\b/gi],
  ["EfficientNet", /\bEfficientNet[A-Za-z0-9-]*\b/gi],
  ["ResNet", /\bResNet[A-Za-z0-9-]*\b/gi],
  ["support vector machine", /\bsupport vector machine\b/gi],
  ["SVM", /\bSVM\b/g],
  ["random forest", /\brandom forest\b/gi],
  ["kNN", /\bkNN\b|\bK-Nearest Neighbor\b/gi],
];

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function clean(value) {
  if (value == null) return "";
  return String(value).replace(/\s+/g, " ").trim();
}

function cleanTrack(value) {
  return clean(value).replace(/^\|+\s*(?=Website\b)/i, "");
}

function csvEscape(value) {
  const s = clean(value);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function htmlEscape(value) {
  return clean(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function unique(arr) {
  return [...new Set(arr.filter(Boolean))];
}

function sourceUrls(r) {
  if (!r.source_urls || typeof r.source_urls !== "object") return [];
  return Object.entries(r.source_urls).map(([label, url]) => `${label}: ${url}`);
}

function primaryText(r) {
  return [
    r.title,
    r.abstract_text,
    r.summary,
    ...Object.values(r.sections || {}),
  ].filter(Boolean).join("\n");
}

function sessionText(r) {
  return [r.session_title, cleanTrack(r.track), cleanTrack(r.topic), r.session_type].filter(Boolean).join("\n");
}

function allText(r) {
  return [primaryText(r), sessionText(r)].filter(Boolean).join("\n");
}

function contexts(text, regex) {
  const out = [];
  for (const match of text.matchAll(regex)) {
    const start = Math.max(0, match.index - 110);
    const end = Math.min(text.length, match.index + match[0].length + 140);
    out.push(clean(text.slice(start, end)));
    if (out.length >= 3) break;
  }
  return out;
}

function matchedTerms(text) {
  return TERMS
    .map(([name, regex]) => [name, contexts(text, regex)])
    .filter(([, hits]) => hits.length)
    .map(([name, hits]) => ({ term: name, contexts: hits }));
}

function hasAny(text, patterns) {
  return patterns.some((p) => p.test(text));
}

function inclusionReview(record, primaryMatches, sessionMatches) {
  const text = primaryText(record);
  const title = clean(record.title);
  const lower = text.toLowerCase();
  const titleLower = title.toLowerCase();
  const termNames = primaryMatches.map((m) => m.term);
  const sessionTermNames = sessionMatches.map((m) => m.term);
  const reasons = [];
  const exclusions = [];
  const isSessionLike = ["session", "symposium", "meet the professor", "master clinician"].includes(clean(record.record_type).toLowerCase());

  if (!primaryMatches.length && !(isSessionLike && sessionMatches.length)) {
    return { include: false, reason: "Matched term appeared only in an umbrella session/title field for a child record.", exclusions: ["session-only match"] };
  }

  const editingDisclosureOnly = hasAny(text, [
    /\bAI Use:\s*Artificial intelligence\s*\(ChatGPT\)\s*was used only for language editing/i,
    /\bAI-assisted tools were used for grammatical editing/i,
  ]);
  const explicitAI = hasAny(text, [
    /\bartificial intelligence\b/i,
    /\bAI[-](?:based|driven|enabled|assisted)\b/i,
    /\bAI (?:tool|tools|application|software|implementation)\b/i,
    /\bAI in (?:real life|the academic setting|endocrinology)\b/i,
    /\bfrugal AI\b/i,
  ]);
  const llmOrGenerative = hasAny(text, [
    /\bChatGPT\b/i,
    /\bLLMs?\b/,
    /\blarge language models?\b/i,
    /\bchatbots?\b/i,
    /\bretrieval[- ]augmented generation\b/i,
    /\bRAG\b/,
  ]);
  const explicitML = hasAny(text, [
    /\bmachine learning\b/i,
    /\bdeep learning\b/i,
    /\bneural networks?\b/i,
    /\bEfficientNet/i,
    /\bResNet/i,
    /\brandom forest\b/i,
    /\bsupport vector machine\b/i,
    /\bSVM\b/,
    /\bkNN\b/i,
    /\bK-Nearest Neighbor\b/i,
  ]);
  const aiControlSystem = hasAny(text, [
    /\bself-adapting artificial intelligence algorithms?\b/i,
    /\bartificial intelligence[- ]based control systems?\b/i,
    /\bAI[- ]based control systems?\b/i,
  ]);
  const diagnosticImageMethod = hasAny(text, [
    /\bfundus imaging\b/i,
    /\bultrasound images?\b/i,
    /\broutine histology\b/i,
    /\bMRI\b/i,
    /\bDXA images?\b/i,
    /\bimage analysis\b/i,
    /\bcomputer vision\b/i,
    /\bradiomics\b/i,
    /\bautomated detection\b/i,
    /\bautomated deep[- ]learning\b/i,
  ]);
  const radiomicsActual = termNames.includes("radiomics") && diagnosticImageMethod && !/\bcould further improve diagnostic accuracy\b/i.test(text);
  const excludedAIAbbrev = hasAny(text, [
    /\badrenal insufficiency\s*\(AI\)/i,
    /\bAI after\b/i,
    /\bAI due\b/i,
    /\bprimary AI\b/i,
    /\bsecondary AI\b/i,
    /\bpatients? with AI\b/i,
    /\bAI receiving\b/i,
    /\bdeveloped AI\b/i,
    /\bAI was assessed\b/i,
    /\bno patient developed AI\b/i,
    /\bAromatase Inhibitor\s*\(AI\)/i,
    /\bGnRHa,\s*AI,/i,
    /\bantibody .*?\bAI\b/i,
    /\bnormal reference range < .*?\bAI\b/i,
  ]);
  const excludedAutomated = hasAny(text, [
    /\bautomated .*?immunoassays?\b/i,
    /\bautomated functional assay\b/i,
    /\bautomated scheduled appointments?\b/i,
  ]);
  const genericAutomationOnly = termNames.includes("automated") && !explicitAI && !explicitML && !aiControlSystem && !llmOrGenerative;
  const genericPredictionOnly = (termNames.includes("algorithm") || termNames.includes("prediction model")) && !explicitAI && !explicitML && !aiControlSystem && !llmOrGenerative;
  const algorithmSessionOnly = titleLower.includes("algorithms and organoids") && !explicitAI && !explicitML && !aiControlSystem;

  if (editingDisclosureOnly) exclusions.push("AI/ChatGPT mention is a language- or grammar-editing disclosure only.");
  if (explicitAI && !editingDisclosureOnly) reasons.push("Explicit artificial-intelligence technology or AI-focused programming.");
  if (llmOrGenerative && !editingDisclosureOnly) reasons.push("Generative AI, LLM, chatbot, or retrieval-augmented-generation content.");
  if (explicitML) reasons.push("Machine-learning, deep-learning, neural-network architecture, or named ML method.");
  if (aiControlSystem) reasons.push("AI-based algorithm or control-system language.");
  if (radiomicsActual) reasons.push("Radiomics or computer-vision/image-analysis method used diagnostically.");
  if (isSessionLike && !primaryMatches.length && sessionMatches.length) {
    reasons.push("AI-related session or symposium metadata record.");
  }

  if (excludedAIAbbrev && !explicitAI && !explicitML) exclusions.push("AI abbreviation is clinical/assay shorthand, not artificial intelligence.");
  if (excludedAutomated || genericAutomationOnly) exclusions.push("Automated term lacks explicit AI, ML, neural-network, or AI-control-system language.");
  if (genericPredictionOnly) exclusions.push("Prediction/model/algorithm term is generic or statistical without substantive AI/ML language.");
  if (algorithmSessionOnly) exclusions.push("Session title uses algorithm broadly without record-level AI/ML evidence.");

  const include = reasons.length > 0 && exclusions.length === 0;
  return {
    include,
    reason: include ? unique(reasons).join(" ") : unique(exclusions).join(" ") || "No AI-relevant context after false-positive review.",
    exclusions: unique(exclusions),
  };
}

function themeFor(record, terms, reason) {
  const t = `${record.title} ${record.abstract_text} ${record.summary}`.toLowerCase();
  const termText = terms.join(" ").toLowerCase();
  const combined = `${t} ${termText}`;
  if (/insulin delivery|closed-loop|artificial pancreas|pump|cgm|glucose management|control system/.test(combined)) return "AI-enabled glucose-control systems";
  if (/pcos|diabetes prediction|biomarker|risk score|random forest|phenotyping|subtypes/.test(combined)) return "ML prediction and computational phenotyping";
  if (/retinopathy|fundus|ultrasound|histology|radiomics|\bimage\b|\bimaging\b|\bmri\b|\bdxa\b|computed tomography|resnet|efficientnet|computer vision|prostate volume|pituitary gland/.test(combined)) return "Imaging AI and quantitative image analysis";
  if (/large language|llm|chatgpt|chatbot|retrieval-augmented|\brag\b|evidence rx/.test(combined)) return "Generative AI, LLMs, and decision support";
  if (/support vector machine|svm|diagnostic model/.test(combined)) return "ML prediction and computational phenotyping";
  if (/artificial intelligence in endocrinology|academic setting|implementation/.test(t)) return "AI implementation, education, and governance";
  if (/mobile health|personalized nudges|family engagement/.test(combined)) return "AI-enabled clinical interventions";
  return "Other substantive AI/ML topic";
}

function conciseEvidence(record) {
  const text = clean(record.abstract_text || record.summary || record.title);
  return text.length > 270 ? `${text.slice(0, 267)}...` : text;
}

function buildInventory(records) {
  const included = [];
  const excluded = [];
  for (const r of records) {
    const primaryMatches = matchedTerms(primaryText(r));
    const sessionMatches = matchedTerms(sessionText(r));
    if (!primaryMatches.length && !sessionMatches.length) continue;
    const review = inclusionReview(r, primaryMatches, sessionMatches);
    const primaryTerms = primaryMatches.map((m) => m.term);
    const terms = primaryTerms.length ? primaryTerms : sessionMatches.map((m) => m.term);
    const contextsOut = Object.fromEntries((primaryMatches.length ? primaryMatches : sessionMatches).map((m) => [m.term, m.contexts]));
    const item = {
      uid: r.uid,
      title: clean(r.title),
      type: clean(r.record_type),
      display_code: clean(r.display_code || r.session_code),
      session_code: clean(r.session_code),
      session_title: clean(r.session_title),
      track: cleanTrack(r.track),
      topic: cleanTrack(r.topic),
      date: clean(r.date),
      time: clean(r.time),
      timezone: clean(r.timezone),
      presenters_authors: clean(r.authors_text || r.presenter),
      source_urls: r.source_urls || {},
      retrieved_at: clean(r.retrieved_at),
      parse_status: clean(r.parse_status),
      matched_terms: unique(terms),
      matched_contexts: contextsOut,
      reason: review.reason,
      theme: themeFor(r, unique(terms), review.reason),
      evidence_excerpt: conciseEvidence(r),
    };
    if (review.include) included.push(item);
    else excluded.push({ ...item, exclusion_reason: review.reason });
  }
  included.sort((a, b) => (a.date + a.time + a.uid).localeCompare(b.date + b.time + b.uid));
  excluded.sort((a, b) => a.uid.localeCompare(b.uid));
  return { included, excluded };
}

function summarize(included) {
  const byTheme = {};
  const byTrack = {};
  const byType = {};
  const byDate = {};
  for (const item of included) {
    byTheme[item.theme] = (byTheme[item.theme] || 0) + 1;
    byTrack[item.track || "Unspecified"] = (byTrack[item.track || "Unspecified"] || 0) + 1;
    byType[item.type || "Unspecified"] = (byType[item.type || "Unspecified"] || 0) + 1;
    byDate[item.date || "Unspecified"] = (byDate[item.date || "Unspecified"] || 0) + 1;
  }
  const sortEntries = (obj) => Object.entries(obj).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  return {
    total_ai_related_records: included.length,
    by_theme: Object.fromEntries(sortEntries(byTheme)),
    by_track: Object.fromEntries(sortEntries(byTrack)),
    by_type: Object.fromEntries(sortEntries(byType)),
    by_date: Object.fromEntries(sortEntries(byDate)),
  };
}

function writeInventory(included, excluded, summary) {
  fs.writeFileSync(path.join(OUT_DIR, "ai_topic_inventory.json"), JSON.stringify(included, null, 2));
  fs.writeFileSync(path.join(OUT_DIR, "excluded_false_positive_candidates.json"), JSON.stringify(excluded, null, 2));

  const columns = ["uid", "title", "type", "display_code", "session_code", "track", "topic", "date", "time", "presenters_authors", "source_urls", "retrieved_at", "matched_terms", "theme", "reason"];
  const csvRows = [columns.join(",")];
  for (const item of included) {
    csvRows.push(columns.map((col) => {
      if (col === "source_urls") return csvEscape(sourceUrls(item).join(" | "));
      if (col === "matched_terms") return csvEscape(item.matched_terms.join("; "));
      return csvEscape(item[col]);
    }).join(","));
  }
  fs.writeFileSync(path.join(OUT_DIR, "ai_topic_inventory.csv"), csvRows.join("\n"));

  const md = [];
  md.push("# ENDO 2026 AI-Related Topic Inventory");
  md.push("");
  md.push(`- Included AI-related records: ${included.length}`);
  md.push(`- Excluded lexical candidates after false-positive review: ${excluded.length}`);
  md.push(`- Evidence basis: local ENDO 2026 archive in \`${DATA_DIR}\``);
  md.push("");
  md.push("## Topic Clusters");
  for (const [theme, count] of Object.entries(summary.by_theme)) md.push(`- ${theme}: ${count}`);
  md.push("");
  md.push("## Records");
  for (const item of included) {
    md.push(`### ${item.uid} | ${item.display_code || "No display code"} | ${item.title}`);
    md.push(`- Type: ${item.type}`);
    md.push(`- Track/topic: ${item.track || "Unspecified"} / ${item.topic || "Unspecified"}`);
    md.push(`- Date/time: ${item.date || "Unspecified"} ${item.time || ""}`.trim());
    md.push(`- Presenter/authors: ${item.presenters_authors || "Not listed"}`);
    md.push(`- Matched terms: ${item.matched_terms.join(", ")}`);
    md.push(`- Theme: ${item.theme}`);
    md.push(`- Reason: ${item.reason}`);
    md.push(`- Source URLs: ${sourceUrls(item).join("; ")}`);
    md.push("");
  }
  fs.writeFileSync(path.join(OUT_DIR, "ai_topic_inventory.md"), md.join("\n"));
}

function ref(item, n) {
  const url = item.source_urls.detail || item.source_urls.session || item.source_urls.agenda || "#";
  return `<a class="cite" href="${htmlEscape(url)}">${n}</a>`;
}

function shortTitle(item) {
  const code = item.display_code ? `${item.display_code}: ` : "";
  return `${code}${item.title}`;
}

function renderReport(included, excluded, summary) {
  const refs = [];
  const sourceInventoryRef = `<a class="cite" href="ai_topic_inventory.json">A</a>`;
  const manifestRef = `<a class="cite" href="run_manifest.json">B</a>`;
  const addRef = (uid) => {
    const item = included.find((x) => x.uid === uid);
    if (!item) return "";
    let idx = refs.findIndex((x) => x.uid === uid);
    if (idx === -1) {
      refs.push(item);
      idx = refs.length - 1;
    }
    return ref(item, idx + 1);
  };
  const citeUid = (uid) => {
    const item = included.find((x) => x.uid === uid);
    if (!item) return sourceInventoryRef;
    const idx = refs.findIndex((x) => x.uid === uid);
    return idx === -1 ? sourceInventoryRef : ref(item, idx + 1);
  };

  const examples = {
    cgmSession: addRef("endo-2026-M-1763904"),
    cgmMl: sourceInventoryRef,
    aiControl: addRef("endo-2026-P-1844101"),
    retina1: addRef("endo-2026-P-1830619"),
    retina2: sourceInventoryRef,
    thyroid1: addRef("endo-2026-P-1830671"),
    thyroid2: sourceInventoryRef,
    histology: addRef("endo-2026-P-1830692"),
    pcos: addRef("endo-2026-P-1843540"),
    svm: addRef("endo-2026-P-1843392"),
    diabetesModel: sourceInventoryRef,
    bone: sourceInventoryRef,
    llmEdu: addRef("endo-2026-M-1788077"),
    diabetesChatbot: sourceInventoryRef,
    rag: addRef("endo-2026-P-1844097"),
    aiSession: addRef("endo-2026-M-1763889"),
    aiImplementation: sourceInventoryRef,
    aiUse: manifestRef,
  };

  const themeRows = Object.entries(summary.by_theme).map(([theme, count]) => {
    const width = Math.max(8, Math.round((count / included.length) * 100));
    return `<div class="bar-row"><div class="bar-label">${htmlEscape(theme)}</div><div class="bar-track"><div style="width:${width}%"></div></div><div class="bar-val">${count}</div></div>`;
  }).join("");

  const notable = [
    "endo-2026-M-1763889",
    "endo-2026-M-1763904",
    "endo-2026-P-1830619",
    "endo-2026-P-1830671",
    "endo-2026-P-1830684",
    "endo-2026-P-1844097",
  ].map((uid) => included.find((x) => x.uid === uid)).filter(Boolean);
  const notableRows = notable.map((item) => {
    const displayTrack = htmlEscape(cleanTrack(item.track));
    return `<div class="row notable"><div class="cell code">${htmlEscape(item.display_code)}</div><div class="cell"><strong>${htmlEscape(item.title)}</strong><br><span>${htmlEscape(item.theme)}</span></div><div class="cell">${displayTrack}${sourceInventoryRef}</div></div>`;
  }).join("");

  const referenceRows = refs.map((item, i) => `<div class="row refs">
    <div class="cell">${i + 1}</div>
    <div class="cell">${htmlEscape(shortTitle(item))}${ref(item, i + 1)}</div>
    <div class="cell">${htmlEscape(item.date || "Conference record")}<br>${htmlEscape(item.retrieved_at || "retrieved_at not listed")}</div>
    <div class="cell">${htmlEscape(item.reason)}</div>
  </div>`).join("");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Artificial intelligence-related topics at ENDO 2026</title>
  <style>
    :root { --ink:#10120f; --muted:#5c6257; --paper:#f6f1e8; --paper-2:#ebe4d6; --card:#fffaf0; --line:#1b1f17; --lime:#d7ff5f; --orange:#ffb86b; --blue:#b8d8ff; --pink:#ffd3e0; --gray:#d6d0c2; --red:#ff8a76; --shadow:0 18px 48px rgba(16,18,15,.08); --radius:24px; }
    * { box-sizing:border-box; }
    html, body { margin:0; background:var(--paper); color:var(--ink); scrollbar-width:none; }
    html::-webkit-scrollbar, body::-webkit-scrollbar { display:none; }
    body, *, *::before, *::after { -webkit-print-color-adjust:exact; print-color-adjust:exact; font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    a { color:inherit; text-decoration-thickness:1px; text-underline-offset:3px; }
    .slide { width:100vw; height:100vh; min-height:100vh; overflow:hidden; position:relative; display:flex; align-items:flex-start; padding:36px 0 20px; page-break-after:always; break-after:page; background:var(--paper); }
    .slide:last-child { page-break-after:auto; break-after:auto; }
    .slide-bg-img { position:absolute; inset:0; z-index:0; width:100%; height:100%; object-fit:cover; pointer-events:none; user-select:none; }
    .wrap { width:min(1360px, calc(100vw - 56px)); margin:0 auto; position:relative; z-index:1; }
    .eyebrow { display:inline-flex; align-items:center; border:1.4px solid var(--line); padding:8px 12px; border-radius:999px; font-size:15px; font-weight:850; letter-spacing:0; text-transform:uppercase; margin-bottom:18px; background:var(--lime); }
    h1,h2,h3,p { margin:0; }
    h1 { font-size:76px; line-height:.94; letter-spacing:0; font-weight:400; max-width:1320px; font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    h2 { font-size:52px; line-height:.98; letter-spacing:0; font-weight:400; max-width:1300px; font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    h3 { font-size:28px; line-height:1.04; letter-spacing:0; font-weight:700; font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .dek { margin-top:18px; color:var(--muted); font-size:27px; line-height:1.22; max-width:1260px; }
    .section-head { margin-bottom:34px; }
    .section-head p { margin-top:12px; color:var(--muted); font-size:24px; line-height:1.18; max-width:1280px; }
    .grid-2 { display:grid; grid-template-columns:repeat(2,1fr); gap:16px; }
    .grid-3 { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
    .grid-4 { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }
    .panel,.metric,.card,.table,.callout { border:1.5px solid var(--line); background:rgba(255,250,240,.88); border-radius:var(--radius); box-shadow:var(--shadow); overflow:hidden; }
    .panel { padding:22px; }
    .panel.dark,.callout { background:#11130f; color:var(--paper); border-color:#11130f; }
    .panel.dark p,.panel.dark li,.callout p,.callout li { color:rgba(246,241,232,.88); }
    .panel.dark h3 { color:var(--lime); font-weight:700; }
    .metric { padding:21px; min-height:156px; }
    .num { font-size:50px; line-height:.92; font-weight:400; letter-spacing:0; }
    .label { margin-top:12px; font-size:22px; line-height:1.12; color:var(--muted); }
    .card { padding:22px; min-height:250px; }
    .card p { color:var(--muted); font-size:22px; line-height:1.15; margin-top:12px; }
    .tag { display:inline-block; padding:5px 9px; border:1.2px solid var(--line); border-radius:999px; font-size:12px; font-weight:850; text-transform:uppercase; background:var(--paper-2); white-space:nowrap; margin-bottom:11px; }
    .lime{background:var(--lime);} .orange{background:var(--orange);} .blue{background:var(--blue);} .pink{background:var(--pink);} .red{background:var(--red);} .gray{background:var(--gray);}
    .callout { padding:22px 26px; }
    .callout h3 { font-size:31px; font-weight:700; color:var(--lime); }
    .summary-list { margin:12px 0 0; padding-left:22px; display:grid; gap:8px; }
    .summary-list li { color:rgba(246,241,232,.88); font-size:23px; line-height:1.13; }
    .cite { font-size:.58em; vertical-align:super; margin-left:2px; font-weight:500; text-decoration:none; }
    .slide-num { position:absolute; right:40px; bottom:24px; font-size:11px; letter-spacing:.12em; text-transform:uppercase; color:rgba(16,18,15,.38); font-weight:500; z-index:2; }
    .source-note { color:var(--muted); font-size:15px; line-height:1.22; margin-top:12px; }
    .bar-wrap { display:grid; gap:18px; }
    .bar-row { display:grid; grid-template-columns:430px 1fr 42px; gap:12px; align-items:center; font-size:19px; line-height:1.12; }
    .bar-label { font-weight:500; }
    .bar-track { height:30px; border:1.3px solid var(--line); background:var(--paper-2); border-radius:999px; overflow:hidden; }
    .bar-track div { height:100%; background:var(--lime); border-right:1.3px solid var(--line); }
    .bar-val { font-weight:500; text-align:right; }
    .table { display:grid; }
    .row { display:grid; border-bottom:1px solid var(--line); min-height:68px; }
    .row:last-child { border-bottom:0; }
    .row.notable { grid-template-columns:.55fr 2.35fr 1.1fr; min-height:60px; }
    .row.refs { grid-template-columns:.32fr 1.2fr .92fr 1.65fr; min-height:0; }
    .cell { padding:13px 14px; border-right:1px solid var(--line); font-size:18px; line-height:1.12; }
    .cell:last-child { border-right:0; }
    .head .cell { background:#11130f; color:var(--paper); font-weight:500; text-transform:uppercase; font-size:17px; line-height:1; white-space:nowrap; }
    .cell span { color:var(--muted); }
    .cell.code { font-weight:500; }
    .refs .cell { font-size:12px; line-height:1.04; padding:7px 8px; }
    .refs.head .cell { font-size:12px; }
    .refs .cell:first-child { text-align:center; }
    .accent-heading { color:var(--lime); }
    .callout h3.accent-heading { font-weight:700; }
    .slide:nth-of-type(n+2):nth-of-type(-n+9) .section-head { margin-bottom:44px; }
    .slide:nth-of-type(n+2):nth-of-type(-n+9) .card p,
    .slide:nth-of-type(n+2):nth-of-type(-n+9) .panel p,
    .slide:nth-of-type(n+2):nth-of-type(-n+9) .summary-list li,
    .slide:nth-of-type(n+2):nth-of-type(-n+9) .bar-row,
    .slide:nth-of-type(n+2):nth-of-type(-n+9) .bar-label,
    .slide:nth-of-type(n+2):nth-of-type(-n+9) .bar-val,
    .slide:nth-of-type(n+2):nth-of-type(-n+9) .row:not(.head) .cell,
    .slide:nth-of-type(n+2):nth-of-type(-n+9) .row:not(.head) .cell.code,
    .slide:nth-of-type(n+2):nth-of-type(-n+9) .row:not(.head) strong,
    .slide:nth-of-type(n+2):nth-of-type(-n+9) .source-note,
    .slide:nth-of-type(n+2):nth-of-type(-n+9) .cite {
      font-weight:400;
    }
    .references-slide h2 { font-size:48px; }
    @page { size:1600px 900px; margin:0; }
    @media print { html,body{width:1600px;height:900px;} .slide{width:1600px;height:900px;min-height:900px;padding:36px 0 20px;} .wrap{width:1360px;} .panel,.metric,.card,.table,.callout{box-shadow:none;} }
    @media screen and (max-width:900px){ .slide{width:1600px;height:900px;} }
  </style>
</head>
<body>
  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="eyebrow">ENDO 2026 AI topic scan | Conference data retrieved May 30, 2026</div>
      <h1>Artificial intelligence-related topics at ENDO 2026</h1>
      <p class="dek">A full scan of 2,079 ENDO 2026 conference records identified ${included.length} AI-related or AI-adjacent records after excluding non-AI abbreviations and disclosure-only uses.${sourceInventoryRef}${manifestRef}</p>
      <div class="grid-4" style="margin-top:28px;">
        <div class="metric"><div class="num">${included.length}</div><div class="label">Substantive AI/ML records retained.${sourceInventoryRef}</div></div>
        <div class="metric"><div class="num">${Object.keys(summary.by_theme).length}</div><div class="label">Topic clusters in the data.${sourceInventoryRef}</div></div>
        <div class="metric"><div class="num">${summary.by_track["Diabetes and Vascular Disease"] || 0}</div><div class="label">Diabetes and vascular disease records retained.${sourceInventoryRef}</div></div>
        <div class="metric"><div class="num">${excluded.length}</div><div class="label">Lexical candidates excluded or marked borderline.${manifestRef}</div></div>
      </div>
      <div class="callout" style="margin-top:24px;">
        <h3 class="accent-heading">Executive summary</h3>
        <ul class="summary-list">
          <li>The largest cluster was imaging AI and computer vision, including retinal fundus deep-learning models and thyroid ultrasound/molecular/histology AI applications.${examples.retina1}${examples.thyroid1}${examples.histology}</li>
          <li>Diabetes technology content retained CGM-linked machine-learning markers and artificial-pancreas control systems, while AID-only records without AI/ML/control-system language were excluded.${examples.cgmSession}${examples.cgmMl}${examples.aiControl}</li>
          <li>Generative-AI content appeared in education, diabetes education chatbot/tool building, and retrieval-augmented clinical decision support; AI/ChatGPT language-editing disclosures only were excluded.${examples.llmEdu}${examples.diabetesChatbot}${examples.rag}${manifestRef}</li>
        </ul>
      </div>
    </div>
    <div class="slide-num">01 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Conference-scan scope</div>
        <h2>Source basis was ENDO 2026 conference record data, not a live web refresh</h2>
        <p>The scan covered ENDO 2026 abstract, poster, presentation, and session records with associated public source URLs and record metadata.${manifestRef}</p>
      </div>
      <div class="grid-3">
        <div class="card"><span class="tag lime">Full run</span><h3>2,079 records scanned</h3><p>The ENDO 2026 conference data includes 2,079 records, with source URLs available for the included abstracts, posters, sessions, and presentations.${manifestRef}</p></div>
        <div class="card"><span class="tag blue">Inclusive terms</span><h3>AI, ML, algorithms, automation</h3><p>Screening terms included artificial intelligence, AI, machine learning, ML, deep learning, neural network, algorithms, automated, prediction models, radiomics, LLMs, chatbots, and related phrases.${manifestRef}</p></div>
        <div class="card"><span class="tag orange">False positives</span><h3>Clinical abbreviations removed</h3><p>Records were excluded when AI meant adrenal insufficiency, aromatase inhibitor, or assay index, when ML appeared only in names/credentials, or when AI appeared only in an umbrella session title.${manifestRef}</p></div>
      </div>
      <div class="panel dark" style="margin-top:18px;">
        <h3 class="accent-heading">Interpretation boundary</h3>
        <p style="font-size:24px;line-height:1.16;margin-top:10px;">Included records are AI-related conference topics identified from the record text. The report does not infer clinical validity beyond the abstract, poster, session, and presentation metadata.${sourceInventoryRef}${manifestRef}</p>
      </div>
    </div>
    <div class="slide-num">02 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Topic clusters</div>
        <h2>Substantive AI/ML records concentrated in imaging, LLMs, and phenotyping</h2>
      </div>
      <div class="grid-2">
        <div class="panel">
          <h3>Included records by cluster</h3>
          <div class="bar-wrap" style="margin-top:18px;">${themeRows}</div>
          <p class="source-note">Counts reflect the topic cluster assigned to each retained record.${sourceInventoryRef}</p>
        </div>
        <div class="panel dark">
          <h3 class="accent-heading">Readout</h3>
          <ul class="summary-list">
            <li>Imaging topics covered retina, thyroid nodule/cancer, routine histology, MRI-derived measures, DXA, and radiomics.${examples.retina2}${examples.thyroid2}${examples.bone}</li>
            <li>Prediction and phenotyping topics retained machine-learning or named-ML methods, including PCOS subtyping, diabetes prediction, random-forest biomarkers, and SVM diagnostic models.${examples.pcos}${examples.diabetesModel}${examples.svm}</li>
            <li>Implementation content included conference-level AI sessions and a healthcare implementation talk; language-editing-only disclosures are excluded from the retained AI-topic count.${examples.aiSession}${examples.aiImplementation}${examples.aiUse}</li>
          </ul>
        </div>
      </div>
    </div>
    <div class="slide-num">03 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Diabetes technology</div>
        <h2>Glucose-management AI content focused on CGM ML markers and control logic</h2>
      </div>
      <div class="grid-3">
        <div class="card"><span class="tag lime">CGM + ML</span><h3>Progression tracking</h3><p>The SY08 symposium description links CGM, self-adapting AI algorithms in insulin delivery, and CGM-based dynamic markers with machine learning for diabetes progression tracking.${examples.cgmSession}${examples.cgmMl}</p></div>
        <div class="card"><span class="tag blue">AID boundary</span><h3>Automation alone excluded</h3><p>Automated insulin-delivery records were excluded when they described devices or real-world outcomes without explicit AI, ML, neural-network, or AI-control-system language.${manifestRef}</p></div>
        <div class="card"><span class="tag orange">Artificial pancreas</span><h3>Control systems</h3><p>One diabetes poster states that insulin-delivery results can be optimized by integrating artificial-intelligence-based control systems with artificial-pancreas technology.${examples.aiControl}</p></div>
      </div>
      <div class="panel" style="margin-top:18px;">
        <h3>Boundary note</h3>
        <p style="font-size:24px;line-height:1.16;margin-top:10px;color:var(--muted);">Automated insulin delivery alone is not counted as an AI topic. AID and glucose-control records are retained only when the record also states AI, ML, or AI-based control-system content.${manifestRef}</p>
      </div>
    </div>
    <div class="slide-num">04 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Imaging AI</div>
        <h2>Computer-vision topics appeared across retina, thyroid, histology, and quantitative imaging</h2>
      </div>
      <div class="grid-3">
        <div class="card"><span class="tag lime">Retina</span><h3>EfficientNet and ResNet</h3><p>Diabetic-retinopathy records described EfficientNetB0/B1/B3 and ResNet152 neural-network approaches using fundus imaging for detection, severity staging, and differential diagnosis.${examples.retina1}${examples.retina2}${sourceInventoryRef}</p></div>
        <div class="card"><span class="tag blue">Thyroid</span><h3>Ultrasound and histology</h3><p>Thyroid records included AIBx ultrasound software, an AI-driven multimodal thyroid tumor score, and a systematic review of predicting molecular alterations from routine histology.${examples.thyroid1}${examples.thyroid2}${examples.histology}</p></div>
        <div class="card"><span class="tag orange">Quantitative imaging</span><h3>Deep learning and DXA</h3><p>Adjacent imaging records included automated deep-learning-derived prostate volume from MRI and kNN-assisted bone pore-space measurement from spinal DXA images.${sourceInventoryRef}${examples.bone}</p></div>
      </div>
      <div class="panel dark" style="margin-top:18px;">
        <h3 class="accent-heading">Caveat</h3>
        <p style="font-size:24px;line-height:1.16;margin-top:10px;">The retained data separates records that report AI/ML or computer-vision methods from records that only mention radiomics or advanced imaging as a potential future modality.${sourceInventoryRef}</p>
      </div>
    </div>
    <div class="slide-num">05 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Prediction and phenotyping</div>
        <h2>ML prediction and phenotyping topics were retained only when AI/ML methods were explicit</h2>
      </div>
      <div class="grid-3">
        <div class="card"><span class="tag lime">Metabolic disease</span><h3>Diabetes and PCOS</h3><p>Records described external validation of a diabetes prediction machine-learning model, unsupervised machine-learning PCOS subtypes, and a frugal AI PCOS risk score.${examples.diabetesModel}${examples.pcos}${sourceInventoryRef}</p></div>
        <div class="card"><span class="tag blue">Diagnostic modeling</span><h3>SVM and routine biomarkers</h3><p>One retained biochemical-marker record used support-vector-machine diagnostic models to distinguish primary hyperparathyroidism from IGF-I-induced metabolic changes in acromegaly.${examples.svm}</p></div>
        <div class="card"><span class="tag orange">Biomarker panels</span><h3>Random forest</h3><p>One type 1 diabetes biomarker record used a machine-learning random forest model to identify a multivariate protein panel for autoantibody prediction.${sourceInventoryRef}</p></div>
      </div>
    </div>
    <div class="slide-num">06 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Generative AI and implementation</div>
        <h2>LLMs appeared in education, patient education tool-building, and evidence-based diabetes decision support</h2>
      </div>
      <div class="grid-3">
        <div class="card"><span class="tag lime">Teaching</span><h3>LLM-assisted learning design</h3><p>An education session states that large language models would be used to design learning pathways and case studies in a hands-on teaching workshop.${examples.llmEdu}</p></div>
        <div class="card"><span class="tag blue">Patient education</span><h3>Clinician-built tools</h3><p>A diabetes poster asks whether clinicians can build acceptable AI tools for diabetes education and matches the chatbot/LLM term set.${examples.diabetesChatbot}</p></div>
        <div class="card"><span class="tag orange">Clinical decision support</span><h3>RAG for type 2 diabetes</h3><p>Evidence Rx is described as evidence-based clinical decision support in type 2 diabetes using a retrieval-augmented generation system.${examples.rag}</p></div>
      </div>
      <div class="panel" style="margin-top:18px;">
        <h3>AI implementation and disclosure</h3>
        <p style="font-size:24px;line-height:1.16;margin-top:10px;color:var(--muted);">Conference programming also included AI implementation sessions. Records that disclosed ChatGPT or AI-assisted tools only for language or grammar editing are excluded from the retained AI-topic count.${examples.aiSession}${examples.aiImplementation}${examples.aiUse}</p>
      </div>
    </div>
    <div class="slide-num">07 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Notable records</div>
        <h2>Selected records illustrate the range of AI-related conference topics</h2>
      </div>
      <div class="table">
        <div class="row notable head"><div class="cell">Code</div><div class="cell">Record</div><div class="cell">Track</div></div>
        ${notableRows}
      </div>
      <p class="source-note">Selection is illustrative; the retained record set includes all ${included.length} AI-related or AI-adjacent records.${sourceInventoryRef}</p>
    </div>
    <div class="slide-num">08 / 09</div>
  </article>

  <article class="slide references-slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">References 1-${refs.length} plus data notes</div>
        <h2>References</h2>
      </div>
      <div class="table">
        <div class="row refs head"><div class="cell">Ref</div><div class="cell">Source</div><div class="cell">Date / Status / Source Owner</div><div class="cell">Evidence Used in Report</div></div>
        ${referenceRows}
        <div class="row refs"><div class="cell">A</div><div class="cell">Conference record dataset<a class="cite" href="ai_topic_inventory.json">A</a></div><div class="cell">ENDO 2026 abstract/session records</div><div class="cell">Retained records, matched terms, topic clusters, and record-level classification basis.</div></div>
        <div class="row refs"><div class="cell">B</div><div class="cell">Screening method notes<a class="cite" href="run_manifest.json">B</a><a class="cite" href="source-log.md">B</a></div><div class="cell">ENDO 2026 record metadata</div><div class="cell">Screened records, excluded lexical candidates, source URLs, caveats, and record metadata.</div></div>
      </div>
    </div>
    <div class="slide-num">09 / 09</div>
  </article>
</body>
</html>`;
}

function writeSourceLog(records, included, excluded, summary, sourceLogSample, validation) {
  const manifest = {
    run_name: "endo_2026_ai_topics_ci",
    generated_at: new Date().toISOString(),
    run_mode: "Full run: all requested local conference records scanned",
    workspace_output_dir: OUT_DIR,
    source_basis: {
      conference_records_json: JSON_PATH,
      conference_records_json_sha256: sha256(JSON_PATH),
      conference_records_md: MD_PATH,
      conference_records_md_sha256: sha256(MD_PATH),
      upstream_source_log: SOURCE_LOG_PATH,
      upstream_validation_report: VALIDATION_PATH,
      retrieved_at_basis: "Per-record retrieved_at/source_urls fields from local JSON archive; no live web refresh performed.",
    },
    source_counts: {
      json_records_scanned: records.length,
      validation_record_count: validation.record_count,
      validation_expected_count: validation.expected_count,
      validation_matches_expected_count: validation.matches_expected_count,
      md_file_bytes: fs.statSync(MD_PATH).size,
      upstream_source_log_entries: Array.isArray(sourceLogSample) ? sourceLogSample.length : null,
    },
    search_terms: TERMS.map(([name]) => name),
    inclusion_summary: summary,
    lexical_false_positive_candidates_excluded: excluded.length,
    false_positive_handling: [
      "Standalone AI excluded when context indicated adrenal insufficiency, aromatase inhibitor, or assay index rather than artificial intelligence.",
      "Standalone ML excluded when it appeared only in author names, credentials, or citations; author fields were not used for term matching.",
      "Child presentation records were not included solely because an umbrella session title contained AI unless the record's own title, abstract, summary, or structured sections contained an AI-related term.",
      "Automated insulin delivery, automated registries, EMR protocols, assay automation, and scheduling automation were excluded unless the same record stated AI, ML, neural-network, or AI-based control-system language.",
      "Generic clinical prediction/risk models and ordinary statistical algorithms were excluded unless the record stated machine learning, deep learning, neural-network architecture, named ML methods, or AI-based control systems.",
      "AI/ChatGPT language- or grammar-editing disclosures only were kept in the excluded/borderline JSON and not counted as AI-related topics.",
      "Radiomics/computer-vision terms were retained only when used as a diagnostic or image-analysis method, not when mentioned only as a possible future modality.",
    ],
    limitations: [
      "The output is based on the local archive retrieved May 30, 2026; no claims are made about changes after that retrieval timestamp.",
      "Lexical/rule-based inclusion is inclusive and intended for analyst review; borderline automation records are labeled as automation or AI-adjacent rather than as artificial intelligence methods.",
      "Some archive records are metadata-only because detail fetches returned 403; those records can only support title/session metadata, not abstract-level claims.",
    ],
    outputs: {
      inventory_json: "ai_topic_inventory.json",
      inventory_csv: "ai_topic_inventory.csv",
      inventory_md: "ai_topic_inventory.md",
      excluded_candidates_json: "excluded_false_positive_candidates.json",
      report_html: "endo_2026_ai_topics_ci_report.html",
      report_pdf: "endo_2026_ai_topics_ci_report.pdf",
      browser_export_screenshots: "screenshots/browser-export/slide_01.png through slide_09.png",
      source_log_md: "source-log.md",
    },
  };
  fs.writeFileSync(path.join(OUT_DIR, "run_manifest.json"), JSON.stringify(manifest, null, 2));

  const md = [];
  md.push("# Source Log and Run Notes");
  md.push("");
  md.push(`- Run mode: ${manifest.run_mode}`);
  md.push(`- Generated at: ${manifest.generated_at}`);
  md.push(`- Records scanned: ${records.length}`);
  md.push(`- Included records: ${included.length}`);
  md.push(`- Excluded lexical candidates: ${excluded.length}`);
  md.push(`- Evidence basis: local JSON and MD records from \`${DATA_DIR}\``);
  md.push(`- Retrieval basis: per-record \`retrieved_at\` and \`source_urls\` fields from the archive; no live web refresh was performed.`);
  md.push("");
  md.push("## Source Files");
  md.push(`- conference_records.json SHA-256: ${manifest.source_basis.conference_records_json_sha256}`);
  md.push(`- conference_records.md SHA-256: ${manifest.source_basis.conference_records_md_sha256}`);
  md.push(`- validation-report.json record count: ${validation.record_count}`);
  md.push("");
  md.push("## Search Terms");
  md.push(manifest.search_terms.map((t) => `- ${t}`).join("\n"));
  md.push("");
  md.push("## False-Positive Rules");
  md.push(manifest.false_positive_handling.map((t) => `- ${t}`).join("\n"));
  md.push("");
  md.push("## Topic Cluster Counts");
  for (const [theme, count] of Object.entries(summary.by_theme)) md.push(`- ${theme}: ${count}`);
  md.push("");
  md.push("## Caveats");
  md.push(manifest.limitations.map((t) => `- ${t}`).join("\n"));
  fs.writeFileSync(path.join(OUT_DIR, "source-log.md"), md.join("\n"));
}

function main() {
  const records = readJson(JSON_PATH);
  const validation = readJson(VALIDATION_PATH);
  const upstreamSourceLog = readJson(SOURCE_LOG_PATH);
  fs.readFileSync(MD_PATH, "utf8");
  const { included, excluded } = buildInventory(records);
  const summary = summarize(included);
  writeInventory(included, excluded, summary);
  writeSourceLog(records, included, excluded, summary, upstreamSourceLog, validation);
  fs.writeFileSync(path.join(OUT_DIR, "endo_2026_ai_topics_ci_report.html"), renderReport(included, excluded, summary));
  console.log(JSON.stringify({
    records_scanned: records.length,
    included: included.length,
    excluded: excluded.length,
    by_theme: summary.by_theme,
  }, null, 2));
}

main();
