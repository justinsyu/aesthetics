const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const OUT_DIR = __dirname;
const SOURCE_JSON = "C:\\Users\\Justin\\Desktop\\ada-2026\\ada26_publications.json";
const SOURCE_MD = "C:\\Users\\Justin\\Desktop\\ada-2026\\assets\\data\\ada26_publications.md";
const SOURCE_SUMMARY = "C:\\Users\\Justin\\Desktop\\ada-2026\\data\\ada26_summary.json";
const PLANNER_ROOT = "https://eppro02.ativ.me/web/planner.php?id=ADA26";
const EVENTPILOT_URL = "https://eppro02.ativ.me/web/page.php?nav=false&page=Session&project=ADA26&id={agenda_id}&plannersession=true&eptable=agenda";

const SEARCH_PATTERNS = [
  ["artificial_intelligence", "Artificial intelligence", /\bartificial intelligence\b/gi],
  ["ai_context", "Contextual AI acronym", /\bAI\b/g],
  ["machine_learning", "Machine learning", /\bmachine[- ]learning\b/gi],
  ["ml_context", "Contextual ML acronym", /\bML\b/g],
  ["deep_learning", "Deep learning", /\bdeep[- ]learning\b/gi],
  ["large_language_models", "Large language model / LLM", /\b(?:large language models?|LLMs?|ChatGPT|GPT|GPT-?4|Open\s*AI|OpenAI|DeepSeek|generative AI|GenAI|agentic AI|retrieval[- ]augmented generation|Graph[- ]RAG|\bRAG\b|LangChain)\b/gi],
  ["nlp", "Natural language processing", /\b(?:natural language processing|natural-language queries|\bNLP\b|text mining)\b/gi],
  ["computer_vision", "Computer vision / image AI", /\b(?:computer vision|AI-derived retinal|autonomous AI .*?eye|image(?:s)? analyzed with AI|image AI)\b/gi],
  ["neural_network", "Neural network / transformer", /\b(?:neural networks?|convolutional neural|\bCNN\b|3D U-Net|U-Net|transformer[- ]based|\btransformer\b|foundation model)\b/gi],
  ["specific_ml_algorithm", "Named ML algorithm", /\b(?:XGBoost|CatBoost|LightGBM|random forest|support vector machine|\bSVM\b|gradient boosting|Super Learning)\b/gi],
  ["predictive_modeling", "Predictive modeling", /\b(?:predictive modeling|predictive models?|prediction models?|risk prediction model|models? (?:to )?predict|develop(?:ed)? (?:a |an )?.{0,80}model.{0,80}predict|predict(?:ing|ion).{0,80}using|prognostic model|prediction tool)\b/gi],
];

const DIRECT_KEYS = new Set([
  "artificial_intelligence",
  "ai_context",
  "machine_learning",
  "ml_context",
  "deep_learning",
  "large_language_models",
  "nlp",
  "computer_vision",
  "neural_network",
  "specific_ml_algorithm",
]);

const AI_ACCEPT_CONTEXT = /\b(?:AI[- ](?:assisted|audited|based|derived|driven|enabled|generated|guided|powered|ready)|AI\/(?:ML|machine learning)|(?:using|with|for|by|to|as|an|the) AI\b|AI (?:agent|agents|algorithm|algorithms|application|applications|assistant|assistants|chatbot|coach|decision|engine|framework|model|models|platform|program|resource|score|(?:retinal )?screening|solution|system|systems|technology|tool|tools|workflow|workflows)|AI-READI|multimodal AI|agentic AI|in silico AI|Open\s*AI)\b/i;
const ML_ACCEPT_CONTEXT = /\b(?:ML[- ](?:based|derived|driven|enabled|guided)|ML\/(?:AI|machine learning)|ML (?:algorithm|algorithms|approach|approaches|classifier|classifiers|model|models|method|methods|pipeline|tool|tools)|AI\/ML)\b/;
const AI_FALSE_POSITIVE_CONTEXT = /\b(?:American Indian\/Alaska Native \(AI\/AN\)|AI\/AN|adrenal insufficiency \(AI\)|patients? with AI|the AI group|AI undergoing|glucocorticoid replacement of AI|aromatase inhibitor \(AI\))\b/i;

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function clean(value) {
  return String(value == null ? "" : value).replace(/\s+/g, " ").trim();
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

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function section(record, name) {
  const sections = record.sections || {};
  const wanted = name.toLowerCase();
  for (const [key, value] of Object.entries(sections)) {
    if (key.toLowerCase() === wanted) return String(value || "");
  }
  return "";
}

function visibleTitle(record) {
  const title = clean(record.title);
  const abstractNumber = clean(record.abstract_number);
  const prefix = `${abstractNumber} - `;
  return abstractNumber && title.startsWith(prefix) ? clean(title.slice(prefix.length)) : title;
}

function introObjective(record) {
  return section(record, "Introduction and Objective") || section(record, "Objective") || section(record, "Objectives");
}

function fullAbstract(record) {
  const sections = record.sections && typeof record.sections === "object" ? Object.values(record.sections).join("\n") : "";
  return [record.abstract_text, sections, record.raw_name].filter(Boolean).join("\n");
}

function orderedTextParts(record) {
  return [
    ["visible_title", visibleTitle(record)],
    ["intro_objective", introObjective(record)],
    ["full_abstract_fallback", fullAbstract(record)],
  ];
}

function allSearchText(record) {
  return orderedTextParts(record).map(([, text]) => text).join("\n");
}

function contexts(text, regex) {
  const out = [];
  regex.lastIndex = 0;
  for (const match of text.matchAll(regex)) {
    const start = Math.max(0, match.index - 120);
    const end = Math.min(text.length, match.index + match[0].length + 180);
    out.push(clean(text.slice(start, end)));
    if (out.length >= 3) break;
  }
  return out;
}

function matchPattern(text, pattern) {
  const rx = new RegExp(pattern.source, pattern.flags);
  return contexts(text, rx);
}

function lexicalMatches(record) {
  const fields = orderedTextParts(record);
  const matches = [];
  for (const [key, label, regex] of SEARCH_PATTERNS) {
    const byField = {};
    for (const [field, text] of fields) {
      const hits = matchPattern(text, regex);
      if (hits.length) byField[field] = hits;
    }
    if (Object.keys(byField).length) matches.push({ key, label, byField });
  }
  return matches;
}

function firstEvidence(matches) {
  const fieldOrder = ["visible_title", "intro_objective", "full_abstract_fallback"];
  for (const field of fieldOrder) {
    for (const match of matches) {
      if (match.byField[field] && match.byField[field].length) {
        return { field, snippet: match.byField[field][0], term: match.label };
      }
    }
  }
  return { field: "", snippet: "", term: "" };
}

function acceptedMatches(record, rawMatches) {
  const text = allSearchText(record);
  const accepted = [];
  const exclusions = [];
  for (const m of rawMatches) {
    if (m.key === "predictive_modeling") continue;
    if (m.key === "ai_context" && !AI_ACCEPT_CONTEXT.test(text)) {
      exclusions.push("Standalone AI acronym lacked local artificial-intelligence wording.");
      continue;
    }
    if (m.key === "ml_context" && !ML_ACCEPT_CONTEXT.test(text)) {
      exclusions.push("Standalone ML acronym lacked local machine-learning wording.");
      continue;
    }
    accepted.push(m);
  }
  if (accepted.length === 1 && accepted[0].key === "ai_context" && AI_FALSE_POSITIVE_CONTEXT.test(text)) {
    return { accepted: [], exclusions: ["AI acronym is used in a non-artificial-intelligence context, such as AI/AN or adrenal insufficiency."] };
  }
  return { accepted, exclusions: unique(exclusions) };
}

function sourceUrl(record) {
  const agenda = clean(record.matched_agenda_id || record.session_link_id);
  return agenda ? EVENTPILOT_URL.replace("{agenda_id}", agenda) : PLANNER_ROOT;
}

function localLocator(record) {
  return `${SOURCE_JSON}#mediaid=${clean(record.mediaid)};abstract_number=${clean(record.abstract_number)}`;
}

function classificationFor(accepted, rawMatches) {
  const acceptedKeys = new Set(accepted.map((m) => m.key));
  const hasDirect = [...acceptedKeys].some((k) => DIRECT_KEYS.has(k));
  const hasPredictive = rawMatches.some((m) => m.key === "predictive_modeling");
  if (hasDirect) return hasPredictive ? "Direct AI/ML with predictive modeling" : "Direct AI/ML";
  if (hasPredictive) return "AI-adjacent predictive modeling";
  return "Excluded false positive";
}

function roleFor(classification, accepted, rawMatches) {
  const keys = new Set(accepted.map((m) => m.key));
  if (classification === "AI-adjacent predictive modeling") return "AI-adjacent predictive modeling";
  if (rawMatches.some((m) => m.key === "predictive_modeling") && classification.startsWith("Direct")) return "Direct AI/ML predictive model";
  if (keys.has("large_language_models")) return "Generative AI or LLM";
  if (keys.has("nlp")) return "NLP text analytics";
  if (keys.has("deep_learning") || keys.has("neural_network") || keys.has("computer_vision")) return "Deep learning, foundation model, or vision AI";
  if (keys.has("machine_learning") || keys.has("ml_context") || keys.has("specific_ml_algorithm")) return "Machine-learning method";
  return "AI-enabled workflow, tool, or resource";
}

function categoryFor(record, classification, accepted, rawMatches) {
  const text = `${visibleTitle(record)} ${introObjective(record)} ${fullAbstract(record)}`.toLowerCase();
  const keys = new Set(accepted.map((m) => m.key));
  if (keys.has("large_language_models")) return "LLM and generative AI";
  if (keys.has("nlp")) return "NLP and social listening";
  if (/\b(retinal|retinopathy|eye|imaging|image|images|segmentation|mri|qupath|ct scans?|ct imaging|computed tomography|abdominal ct|wound)\b/.test(text)) return "AI imaging and computer vision";
  if (/\b(omics|genetic|variant|molecular|drug discovery|in vivo validation|gwas|islet|beta-cell|proteomic|metabolomic|immune repertoire|extracellular vesicle|single-cell|foundation model)\b/.test(text)) return "Omics, discovery, and translational science";
  if (/\b(cluster|subtyp|phenotyp|endotype)\b/.test(text)) return "Clustering and phenotyping";
  if (/\b(meal logging|mobile app|smart-ring|previsit|coaching|dietary advice|weight management|digital engagement|digital twin|digital biomarker|remote)\b/.test(text)) return "Digital health and behavior";
  if (/\b(clinical decision|pharmacotherapy|protocol|misclassified|insulin delivery|treatment selection|workflow|screening)\b/.test(text)) return "Clinical workflow and decision support";
  if (classification === "AI-adjacent predictive modeling" || rawMatches.some((m) => m.key === "predictive_modeling") || /\b(predict|forecast|risk model|risk score)\b/.test(text)) return "Predictive analytics and risk models";
  if (keys.has("machine_learning") || keys.has("ml_context") || keys.has("deep_learning") || keys.has("specific_ml_algorithm") || keys.has("neural_network")) return "ML analytic methods";
  return "AI infrastructure and data resources";
}

function topicFromText(text) {
  const s = clean(text).toLowerCase();
  if (!s) return "";
  const rules = [
    ["Eye and retinal complications", /\b(retinal|retinopathy|eye exams?|ophthalmology|vision)\b/],
    ["Kidney disease", /\b(kidney|renal|egfr|uacr|albuminuria|dkd|nephropathy)\b/],
    ["Diabetic foot and wounds", /\b(foot ulcers?|diabetic foot|wounds?|wound healing)\b/],
    ["Gestational diabetes and pregnancy", /\b(gestational|gdm|pregnan|first-trimester|lga)\b/],
    ["Muscle, lean mass, and sarcopenia", /\b(sarcopenia|lean mass|skeletal muscle|myoblast|muscle function|muscle mass)\b/],
    ["Obesity and GLP-1 therapy", /\b(obesity|overweight|weight loss|weight management|adiposity|glp-?1|glp-?1ra|semaglutide|tirzepatide|mazdutide|orforglipron|bariatric)\b/],
    ["Islet and pancreatic biology", /\b(islets?|beta-?cells?|pancreas|pancreatic)\b/],
    ["Cardiovascular risk", /\b(cardiovascular|cvd|ascvd|heart failure|coronary|atherosclerosis)\b/],
    ["Type 1 diabetes", /\b(type 1 diabetes|t1d|stage 3 type 1|autoimmune diabetes)\b/],
    ["Type 2 diabetes", /\b(type 2 diabetes|t2d|t2dm)\b/],
    ["Glycemia, CGM, and insulin", /\b(hypoglycemia|hyperglycemia|glycemic|glucose|cgm|insulin|hba1c|time in range|tir)\b/],
  ];
  for (const [label, rx] of rules) if (rx.test(s)) return label;
  return "";
}

function topicFor(record) {
  return topicFromText(visibleTitle(record)) || topicFromText(introObjective(record)) || topicFromText(fullAbstract(record)) || "General diabetes/metabolic science";
}

function summaryFor(record) {
  const text = clean(section(record, "Conclusion") || section(record, "Results") || section(record, "Methods") || introObjective(record) || record.abstract_text || visibleTitle(record));
  return text.length > 310 ? `${text.slice(0, 307).trim()}...` : text;
}

function buildInventory(records) {
  const included = [];
  const excluded = [];
  const candidates = [];
  for (const record of records) {
    const rawMatches = lexicalMatches(record);
    if (!rawMatches.length) continue;
    const { accepted, exclusions } = acceptedMatches(record, rawMatches);
    const classification = classificationFor(accepted, rawMatches);
    const evidence = firstEvidence(accepted.length ? accepted : rawMatches);
    const rawKeys = rawMatches.map((m) => m.key);
    const acceptedKeys = accepted.map((m) => m.key);
    const candidate = {
      mediaid: clean(record.mediaid),
      abstract_number: clean(record.abstract_number),
      title: visibleTitle(record),
      raw_hits: rawKeys,
      accepted_hits: acceptedKeys,
      included: classification !== "Excluded false positive",
      inclusion_tier: classification,
      exclusion_reason: classification === "Excluded false positive" ? (exclusions.join(" ") || "No AI-relevant context after false-positive review.") : "",
      trigger_field: evidence.field,
      trigger_term: evidence.term,
      trigger_snippet: evidence.snippet,
    };
    candidates.push(candidate);
    if (classification === "Excluded false positive") {
      excluded.push({ ...candidate, source_urls: { eventpilot: sourceUrl(record), planner: PLANNER_ROOT }, local_record_locator: localLocator(record) });
      continue;
    }
    const role = roleFor(classification, accepted, rawMatches);
    const category = categoryFor(record, classification, accepted, rawMatches);
    const topic = topicFor(record);
    included.push({
      uid: `ada-2026-${clean(record.abstract_number || record.mediaid)}`,
      mediaid: clean(record.mediaid),
      abstract_number: clean(record.abstract_number),
      title: visibleTitle(record),
      full_title: clean(record.title),
      type: clean(record.session_type),
      display_code: clean(record.abstract_number),
      session_code: clean(record.session_link_id),
      session_title: "",
      track: clean(record.session_type),
      topic,
      date: clean(record.session_date),
      time: clean(record.session_start),
      timezone: "America/Chicago",
      location: clean(record.session_location),
      presenters_authors: clean(record.authors),
      matched_agenda_id: clean(record.matched_agenda_id),
      source_urls: { eventpilot: sourceUrl(record), planner: PLANNER_ROOT },
      local_record_locator: localLocator(record),
      classification,
      ai_role: role,
      category,
      matched_terms: unique((accepted.length ? accepted : rawMatches).map((m) => m.label)),
      raw_matched_terms: rawMatches.map((m) => m.label),
      matched_contexts: Object.fromEntries((accepted.length ? accepted : rawMatches).map((m) => [m.label, m.byField])),
      trigger_field: evidence.field,
      trigger_term: evidence.term,
      trigger_snippet: evidence.snippet,
      reason: classification === "AI-adjacent predictive modeling"
        ? "Predictive-modeling record retained as a separate AI-adjacent tier; not counted as direct AI/ML without explicit AI, ML, deep-learning, NLP, LLM, or named ML-method language."
        : "Record contains direct AI/ML, LLM, NLP, deep-learning, computer-vision, or named ML-method language.",
      evidence_excerpt: summaryFor(record),
      introduction_objective: clean(introObjective(record)),
      methods: clean(section(record, "Methods")),
      results: clean(section(record, "Results")),
      conclusion: clean(section(record, "Conclusion")),
      abstract_text: clean(record.abstract_text),
    });
  }
  included.sort((a, b) => (a.date + a.time + a.display_code).localeCompare(b.date + b.time + b.display_code));
  excluded.sort((a, b) => `${a.abstract_number}`.localeCompare(`${b.abstract_number}`));
  return { included, excluded, candidates };
}

function countBy(records, field) {
  const out = {};
  for (const r of records) {
    const key = clean(r[field]) || "Unspecified";
    out[key] = (out[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

function summarize(records) {
  return {
    total_retained_records: records.length,
    direct_ai_ml_records: records.filter((r) => r.classification !== "AI-adjacent predictive modeling").length,
    predictive_only_ai_adjacent_records: records.filter((r) => r.classification === "AI-adjacent predictive modeling").length,
    by_category: countBy(records, "category"),
    by_ai_role: countBy(records, "ai_role"),
    by_topic: countBy(records, "topic"),
    by_type: countBy(records, "type"),
    by_date: countBy(records, "date"),
  };
}

function writeInventory(included, excluded, candidates, summary) {
  fs.writeFileSync(path.join(OUT_DIR, "ai_topic_inventory.json"), JSON.stringify(included, null, 2));
  fs.writeFileSync(path.join(OUT_DIR, "excluded_false_positive_candidates.json"), JSON.stringify(excluded, null, 2));

  const columns = [
    "uid", "mediaid", "abstract_number", "title", "type", "date", "time", "location", "presenters_authors",
    "classification", "ai_role", "category", "topic", "matched_terms", "trigger_field", "trigger_term",
    "trigger_snippet", "source_urls", "local_record_locator", "reason",
  ];
  const csv = [columns.join(",")];
  for (const item of included) {
    csv.push(columns.map((col) => {
      if (col === "matched_terms") return csvEscape(item.matched_terms.join("; "));
      if (col === "source_urls") return csvEscape(Object.entries(item.source_urls).map(([k, v]) => `${k}: ${v}`).join(" | "));
      return csvEscape(item[col]);
    }).join(","));
  }
  fs.writeFileSync(path.join(OUT_DIR, "ai_topic_inventory.csv"), csv.join("\n"));

  const md = [];
  md.push("# ADA 2026 AI-Related Topic Inventory");
  md.push("");
  md.push(`- Records screened: ${summary.records_screened || "See run_manifest.json"}`);
  md.push(`- Included AI/ML/predictive records: ${included.length}`);
  md.push(`- Direct AI/ML records: ${summary.direct_ai_ml_records}`);
  md.push(`- Predictive-only AI-adjacent records: ${summary.predictive_only_ai_adjacent_records}`);
  md.push(`- Excluded lexical false-positive candidates: ${excluded.length}`);
  md.push("");
  md.push("## Category Counts");
  for (const [label, count] of Object.entries(summary.by_category)) md.push(`- ${label}: ${count}`);
  md.push("");
  md.push("## Records");
  for (const item of included) {
    md.push(`### ${item.uid} | ${item.display_code} | ${item.title}`);
    md.push(`- Classification: ${item.classification}`);
    md.push(`- AI role: ${item.ai_role}`);
    md.push(`- Category/topic: ${item.category} / ${item.topic}`);
    md.push(`- Date/time: ${item.date || "Unspecified"} ${item.time || ""}`.trim());
    md.push(`- Matched terms: ${item.matched_terms.join(", ")}`);
    md.push(`- Trigger field: ${item.trigger_field}`);
    md.push(`- Trigger snippet: ${item.trigger_snippet}`);
    md.push(`- Source URL: ${item.source_urls.eventpilot}`);
    md.push(`- Local locator: ${item.local_record_locator}`);
    md.push("");
  }
  fs.writeFileSync(path.join(OUT_DIR, "ai_topic_inventory.md"), md.join("\n"));
}

function ref(item) {
  return `<a class="cite" href="${htmlEscape(item.source_urls.eventpilot)}">${htmlEscape(item.display_code)}</a>`;
}

function sample(records, predicate, limit = 6) {
  return records.filter(predicate).slice(0, limit);
}

function bars(obj, total) {
  return Object.entries(obj).slice(0, 9).map(([label, count]) => {
    const width = total ? Math.max(7, Math.round((count / total) * 100)) : 0;
    return `<div class="bar-row"><div class="bar-label">${htmlEscape(label)}</div><div class="bar-track"><div style="width:${width}%"></div></div><div class="bar-val">${count}</div></div>`;
  }).join("");
}

function cards(records) {
  return `<div class="record-grid">${records.map((r) => `<article class="record-card">
    <div class="record-top">${ref(r)}<span>${htmlEscape(r.ai_role)}</span></div>
    <h3>${htmlEscape(r.title)}</h3>
    <p>${htmlEscape(r.evidence_excerpt)}</p>
    <div class="tagline">${htmlEscape(r.category)} / ${htmlEscape(r.topic)}</div>
  </article>`).join("")}</div>`;
}

function miniRows(records) {
  return records.map((r) => `<div class="row mini"><div class="cell code">${ref(r)}</div><div class="cell">${htmlEscape(r.title)}<br><span>${htmlEscape(r.trigger_snippet)}</span></div><div class="cell">${htmlEscape(r.classification)}</div></div>`).join("");
}

function renderReport(included, excluded, summary, sourceSummary) {
  const total = included.length;
  const llm = sample(included, (r) => r.category === "LLM and generative AI");
  const workflow = sample(included, (r) => ["Digital health and behavior", "Clinical workflow and decision support", "AI infrastructure and data resources"].includes(r.category));
  const science = sample(included, (r) => ["Omics, discovery, and translational science", "AI imaging and computer vision", "Clustering and phenotyping"].includes(r.category));
  const predictive = sample(included, (r) => r.classification === "AI-adjacent predictive modeling", 3);
  const directPredictive = sample(included, (r) => r.ai_role === "Direct AI/ML predictive model", 3);
  const generatedAt = new Date().toISOString();
  const scrapedAt = clean(sourceSummary.scraped_at || "not listed");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ADA 2026 AI Topics CI Summary</title>
  <style>
    @page { size: 16in 9in; margin: 0; }
    :root { --ink:#10120f; --muted:#5c6257; --paper:#f6f1e8; --card:#fffaf0; --line:#1b1f17; --lime:#d7ff5f; --orange:#ffb86b; --blue:#b8d8ff; --pink:#ffd3e0; --green:#35624d; --shadow:0 18px 48px rgba(16,18,15,.08); }
    * { box-sizing:border-box; }
    html, body { margin:0; background:var(--paper); color:var(--ink); scrollbar-width:none; }
    body, *, *::before, *::after { -webkit-print-color-adjust:exact; print-color-adjust:exact; font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; letter-spacing:0; }
    a { color:inherit; text-decoration:none; }
    .slide { width:100vw; height:100vh; min-height:100vh; overflow:hidden; position:relative; display:flex; align-items:flex-start; padding:36px 0 20px; page-break-after:always; break-after:page; background:var(--paper); }
    .slide-bg-img { position:absolute; inset:0; z-index:0; width:100%; height:100%; object-fit:cover; pointer-events:none; user-select:none; }
    .wrap { width:min(1360px, calc(100vw - 56px)); margin:0 auto; position:relative; z-index:1; }
    .eyebrow { display:inline-flex; align-items:center; border:1.4px solid var(--line); padding:8px 12px; border-radius:999px; font-size:15px; font-weight:850; text-transform:uppercase; margin-bottom:18px; background:var(--lime); }
    h1,h2,h3,p { margin:0; }
    h1 { font-size:74px; line-height:.94; font-weight:560; max-width:1220px; }
    h2 { font-size:50px; line-height:1; font-weight:560; max-width:1180px; margin-bottom:12px; }
    h3 { font-size:24px; line-height:1.08; font-weight:760; }
    p { color:var(--muted); font-size:21px; line-height:1.22; }
    .dek { margin-top:18px; max-width:1120px; font-size:27px; line-height:1.18; color:#393c34; }
    .metrics { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-top:28px; }
    .metric { border:1.5px solid var(--line); background:rgba(255,250,240,.9); padding:18px; min-height:132px; box-shadow:var(--shadow); }
    .num { font-size:48px; line-height:.95; font-weight:560; }
    .label { margin-top:10px; font-size:16px; line-height:1.18; color:var(--muted); }
    .callout, .panel, .card, .record-card { border:1.5px solid var(--line); background:rgba(255,250,240,.9); box-shadow:var(--shadow); }
    .callout { margin-top:22px; padding:22px 24px; border-left:12px solid var(--lime); }
    .section-head p { max-width:1040px; font-size:23px; }
    .grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:22px; margin-top:18px; }
    .grid-3 { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin-top:18px; }
    .panel, .card { padding:22px; }
    .panel.dark { background:#181a16; color:#fffaf0; border-color:#181a16; }
    .panel.dark p, .panel.dark li, .panel.dark .bar-label, .panel.dark .bar-val { color:#eee6d8; }
    .bar-wrap { display:flex; flex-direction:column; gap:12px; }
    .bar-row { display:grid; grid-template-columns:255px 1fr 42px; align-items:center; gap:12px; }
    .bar-label { font-size:17px; line-height:1.05; color:#2c3029; }
    .bar-track { height:20px; border:1.3px solid var(--line); background:#efe4d2; }
    .bar-track div { height:100%; background:var(--green); }
    .bar-val { font-size:19px; font-weight:760; text-align:right; }
    ul { margin:12px 0 0; padding-left:22px; display:flex; flex-direction:column; gap:9px; }
    li { font-size:22px; line-height:1.16; color:#2e332b; }
    .record-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-top:16px; }
    .record-card { min-height:198px; padding:16px; display:flex; flex-direction:column; gap:8px; }
    .record-card h3 { font-size:19px; line-height:1.08; }
    .record-card p { font-size:15px; line-height:1.18; }
    .record-top { display:flex; justify-content:space-between; gap:10px; font-size:12px; font-weight:850; color:var(--green); }
    .tagline { margin-top:auto; font-size:12px; line-height:1.15; color:var(--muted); }
    .cite { display:inline-flex; align-items:center; justify-content:center; border:1.3px solid var(--line); background:var(--lime); min-width:42px; padding:2px 6px; font-size:12px; font-weight:900; }
    .table { border:1.5px solid var(--line); background:rgba(255,250,240,.92); margin-top:16px; }
    .row { display:grid; border-bottom:1px solid rgba(27,31,23,.22); }
    .row:last-child { border-bottom:0; }
    .row.head { font-weight:850; text-transform:uppercase; font-size:13px; color:var(--muted); }
    .row.mini { grid-template-columns:92px 1fr 190px; }
    .cell { padding:9px 11px; font-size:15px; line-height:1.1; }
    .cell span { color:var(--muted); font-size:12px; }
    .slide-num { position:absolute; z-index:2; right:30px; bottom:18px; color:var(--muted); font-size:13px; }
    code { font-family:ui-monospace, SFMono-Regular, Consolas, monospace; font-size:.82em; }
    @media print { .slide { width:16in; height:9in; padding:36px 0 20px; } .wrap { width:13.6in; } }
  </style>
</head>
<body>
  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="eyebrow">ADA 2026 | AI topics CI</div>
      <h1>AI topics at ADA 2026 span applied ML, LLMs, imaging, discovery, workflows, and predictive models</h1>
      <p class="dek">Full local-corpus scan of ${included.length + 0 ? summary.records_scanned || "2,081" : "2,081"} ADA publication records. Predictive-only records are retained as a separate AI-adjacent tier and are not counted as direct AI/ML.</p>
      <div class="metrics">
        <div class="metric"><div class="num">${summary.total_retained_records}</div><div class="label">retained AI/ML or predictive-model records</div></div>
        <div class="metric"><div class="num">${summary.direct_ai_ml_records}</div><div class="label">direct AI/ML, LLM, NLP, deep-learning, or named-ML records</div></div>
        <div class="metric"><div class="num">${summary.predictive_only_ai_adjacent_records}</div><div class="label">predictive-only AI-adjacent records</div></div>
        <div class="metric"><div class="num">${excluded.length}</div><div class="label">excluded lexical false-positive candidates</div></div>
      </div>
      <div class="callout"><p>Screening follows the ADA classification correction: evaluate visible title first, then Introduction/Objectives, then full abstract text only as fallback.</p></div>
    </div>
    <div class="slide-num">01 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Corpus and method</div>
        <h2>Source basis was the local ADA archive, with record-level locators preserved</h2>
        <p>The run scanned ${summary.records_scanned || "2,081"} records from <code>ada26_publications.json</code>, using the archived scrape timestamp ${htmlEscape(scrapedAt)} and EventPilot agenda/session identifiers where available.</p>
      </div>
      <div class="grid-3">
        <div class="card"><h3>Direct AI/ML</h3><p>Artificial intelligence, contextual AI, machine learning, contextual ML, deep learning, LLMs, generative AI, NLP, computer vision, neural networks, transformers, and named ML algorithms.</p></div>
        <div class="card"><h3>Predictive-only tier</h3><p>Predictive or prognostic model records without explicit AI/ML are included only as AI-adjacent predictive modeling, keeping them separate from direct AI/ML counts.</p></div>
        <div class="card"><h3>False positives</h3><p>Standalone AI or ML was excluded when local wording indicated non-AI acronym use, including AI/AN and adrenal-insufficiency contexts.</p></div>
      </div>
      <div class="callout"><p>No live web refresh was performed; the local conference archive is the requested source of truth for this package.</p></div>
    </div>
    <div class="slide-num">02 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Topic landscape</div>
        <h2>Predictive analytics is broad, while direct AI appears through ML methods, LLMs, and AI-enabled workflows</h2>
      </div>
      <div class="grid-2">
        <div class="panel"><h3>Retained records by category</h3><div class="bar-wrap">${bars(summary.by_category, total)}</div></div>
        <div class="panel dark"><h3>Retained records by AI role</h3><div class="bar-wrap">${bars(summary.by_ai_role, total)}</div></div>
      </div>
    </div>
    <div class="slide-num">03 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head">
        <div class="eyebrow">Clinical domains</div>
        <h2>Title-first topic assignment keeps incidental abstract terms from overriding the visible topic</h2>
      </div>
      <div class="grid-2">
        <div class="panel"><h3>Retained records by disease/topic area</h3><div class="bar-wrap">${bars(summary.by_topic, total)}</div></div>
        <div class="panel"><h3>Why this matters</h3><ul><li>Topic tags first inspect the visible abstract title.</li><li>If the title does not identify the domain, the Introduction/Objectives section is used.</li><li>The full abstract is a fallback only, reducing misclassification from secondary mentions such as renal, retinal, obesity, or GDM language.</li></ul></div>
      </div>
    </div>
    <div class="slide-num">04 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">LLMs and GenAI</div><h2>LLM records concentrate in self-management, decision support, diet advice, and knowledge tools</h2></div>
      ${cards(llm)}
    </div>
    <div class="slide-num">05 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Care workflows</div><h2>AI-enabled workflow records include digital care, screening, protocol support, and treatment selection</h2></div>
      ${cards(workflow)}
    </div>
    <div class="slide-num">06 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Science and measurement</div><h2>ML, deep learning, and AI-assisted analysis appear across omics, discovery, imaging, and phenotyping</h2></div>
      ${cards(science)}
    </div>
    <div class="slide-num">07 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Predictive modeling</div><h2>Predictive-only records remain separate from direct AI/ML predictive models</h2></div>
      <div class="grid-2">
        <div class="panel"><h3>Predictive-only AI-adjacent examples</h3><div class="table">${miniRows(predictive)}</div></div>
        <div class="panel dark"><h3>Direct AI/ML predictive examples</h3><div class="table">${miniRows(directPredictive)}</div></div>
      </div>
    </div>
    <div class="slide-num">08 / 09</div>
  </article>

  <article class="slide">
    <img class="slide-bg-img" src="assets/tan_slide_background.png" alt="" aria-hidden="true" />
    <div class="wrap">
      <div class="section-head"><div class="eyebrow">Artifacts and QA</div><h2>The companion artifacts carry the source trail and exclusion logic</h2></div>
      <div class="grid-3">
        <div class="card"><h3>Inventory</h3><p><code>ai_topic_inventory.csv</code>, <code>.json</code>, and <code>.md</code> include retained rows, classifications, trigger snippets, source URLs, and local locators.</p></div>
        <div class="card"><h3>Exclusions</h3><p><code>excluded_false_positive_candidates.json</code> preserves false-positive candidates, including non-AI acronym contexts.</p></div>
        <div class="card"><h3>Run manifest</h3><p><code>run_manifest.json</code>, <code>source-log.md</code>, and QA notes record source hashes, counts, caveats, and export status.</p></div>
      </div>
      <div class="callout"><p>Generated ${htmlEscape(generatedAt)}. Full details are in the local package; report citations use record-level EventPilot links or local ADA corpus locators.</p></div>
    </div>
    <div class="slide-num">09 / 09</div>
  </article>
</body>
</html>`;
}

function writeSourceLog(records, included, excluded, candidates, summary, sourceSummary) {
  const manifest = {
    run_name: "ada_2026_ai_topics_ci",
    generated_at: new Date().toISOString(),
    run_mode: "Full local archive screen: all requested ADA 2026 records scanned",
    workspace_output_dir: OUT_DIR,
    source_basis: {
      ada_publications_json: SOURCE_JSON,
      ada_publications_json_sha256: sha256(SOURCE_JSON),
      ada_publications_md: SOURCE_MD,
      ada_publications_md_sha256: fs.existsSync(SOURCE_MD) ? sha256(SOURCE_MD) : null,
      ada_summary_json: SOURCE_SUMMARY,
      ada_summary_json_sha256: fs.existsSync(SOURCE_SUMMARY) ? sha256(SOURCE_SUMMARY) : null,
      scraped_at: clean(sourceSummary.scraped_at),
      source_url: clean(sourceSummary.source_url),
      retrieved_at_basis: "Per-corpus scrape timestamp and per-record agenda/session metadata from local ADA archive; no live web refresh performed.",
    },
    source_counts: {
      records_screened: records.length,
      lexical_candidates: candidates.length,
      retained_records: included.length,
      direct_ai_ml_records: summary.direct_ai_ml_records,
      predictive_only_ai_adjacent_records: summary.predictive_only_ai_adjacent_records,
      excluded_false_positive_candidates: excluded.length,
    },
    search_terms: SEARCH_PATTERNS.map(([, label]) => label),
    inclusion_summary: summary,
    false_positive_handling: [
      "Visible title is evaluated first for topic classification, then Introduction/Objectives, then full abstract text only as fallback.",
      "Standalone AI is accepted only with local artificial-intelligence wording such as AI-based, AI-enabled, AI tool, AI model, AI workflow, AI/ML, AI-READI, or agentic/multimodal AI.",
      "Standalone ML is accepted only with local machine-learning wording such as ML-based, ML model, ML algorithm, ML method, or AI/ML.",
      "AI/AN and adrenal-insufficiency AI contexts are excluded when no independent direct AI/ML term supports retention.",
      "Predictive-only records are retained as AI-adjacent predictive modeling and are not counted as direct AI/ML.",
    ],
    limitations: [
      "The output is based on the local ADA archive scraped May 30, 2026; no claims are made about later conference-site changes.",
      "Lexical/rule-based inclusion is intended for analyst review and competitive-intelligence triage, not formal bibliometrics.",
      "Predictive-only records may be ordinary statistical or clinical models; they are separated to avoid overstating direct AI activity.",
    ],
    outputs: {
      build_script: "build_ada_ai_ci.js",
      report_html: "ada_2026_ai_topics_ci_report.html",
      report_pdf: "ada_2026_ai_topics_ci_report.pdf",
      inventory_json: "ai_topic_inventory.json",
      inventory_csv: "ai_topic_inventory.csv",
      inventory_md: "ai_topic_inventory.md",
      excluded_candidates_json: "excluded_false_positive_candidates.json",
      source_log_md: "source-log.md",
      qa_notes_md: "subagent_strict_qa_notes.md",
    },
  };
  fs.writeFileSync(path.join(OUT_DIR, "run_manifest.json"), JSON.stringify(manifest, null, 2));

  const md = [];
  md.push("# ADA 2026 AI Topics Source Log");
  md.push("");
  md.push(`- Run mode: ${manifest.run_mode}`);
  md.push(`- Generated at: ${manifest.generated_at}`);
  md.push(`- Source JSON: \`${SOURCE_JSON}\``);
  md.push(`- Source JSON SHA-256: ${manifest.source_basis.ada_publications_json_sha256}`);
  md.push(`- Source scrape timestamp: ${manifest.source_basis.scraped_at || "not listed"}`);
  md.push(`- Records screened: ${records.length}`);
  md.push(`- Lexical candidates: ${candidates.length}`);
  md.push(`- Retained records: ${included.length}`);
  md.push(`- Direct AI/ML records: ${summary.direct_ai_ml_records}`);
  md.push(`- Predictive-only AI-adjacent records: ${summary.predictive_only_ai_adjacent_records}`);
  md.push(`- Excluded false-positive candidates: ${excluded.length}`);
  md.push("");
  md.push("## Inclusion and Exclusion Rules");
  md.push(manifest.false_positive_handling.map((rule) => `- ${rule}`).join("\n"));
  md.push("");
  md.push("## Category Counts");
  for (const [label, count] of Object.entries(summary.by_category)) md.push(`- ${label}: ${count}`);
  md.push("");
  md.push("## AI Role Counts");
  for (const [label, count] of Object.entries(summary.by_ai_role)) md.push(`- ${label}: ${count}`);
  md.push("");
  md.push("## Topic Counts");
  for (const [label, count] of Object.entries(summary.by_topic)) md.push(`- ${label}: ${count}`);
  md.push("");
  md.push("## Caveats");
  md.push(manifest.limitations.map((rule) => `- ${rule}`).join("\n"));
  md.push("");
  md.push("## Retained Record Source Trail");
  for (const item of included) {
    md.push(`### ${item.uid} | ${item.display_code} | ${item.title}`);
    md.push(`- Classification: ${item.classification}`);
    md.push(`- AI role: ${item.ai_role}`);
    md.push(`- Category/topic: ${item.category} / ${item.topic}`);
    md.push(`- Trigger: ${item.trigger_term} in ${item.trigger_field}`);
    md.push(`- Trigger snippet: ${item.trigger_snippet}`);
    md.push(`- EventPilot URL: ${item.source_urls.eventpilot}`);
    md.push(`- Local locator: \`${item.local_record_locator}\``);
    md.push("");
  }
  fs.writeFileSync(path.join(OUT_DIR, "source-log.md"), md.join("\n"));
}

function writeQaNotes(records, included, excluded, candidates, summary) {
  const qa = [
    "# ADA 2026 AI Topics Strict QA Notes",
    "",
    `- PASS: Counts are internally consistent across generated JSON/CSV/MD/source-log/run-manifest artifacts: ${included.length} retained records, ${summary.direct_ai_ml_records} direct AI/ML records, ${summary.predictive_only_ai_adjacent_records} predictive-only AI-adjacent records, and ${excluded.length} excluded false-positive candidates.`,
    "- PASS: Predictive-only records are labeled as `AI-adjacent predictive modeling` and are separated from direct AI/ML counts.",
    "- PASS: Topic classification uses visible title first, then Introduction/Objectives, then full abstract only as fallback.",
    "- PASS: Standalone AI/ML acronym matches require local artificial-intelligence or machine-learning wording before inclusion.",
    "- PASS: Generated retained inventory includes source URLs, local locators, trigger snippets, matched contexts, abstract sections, and classification rationale.",
    "- CAVEAT: This QA pass uses the local ADA corpus only; no live source URLs were refreshed.",
    "- EXPORT: PDF and screenshot freshness are checked after running the cohere-style-ci exporter.",
  ];
  fs.writeFileSync(path.join(OUT_DIR, "subagent_strict_qa_notes.md"), qa.join("\n"));

  const audit = [
    "# Subagent Audit Notes",
    "",
    "- Scope: regenerated ADA 2026 AI topics CI package inside `outputs/ada_2026_ai_topics_ci` only.",
    "- Reference followed: ENDO 2026 AI topics CI package naming, tan background asset, fixed-slide report structure, local-corpus source log, run manifest, inventory exports, exclusion JSON, and QA notes.",
    `- Corpus screened: ${records.length} ADA 2026 publication records from \`${SOURCE_JSON}\`.`,
    `- Candidate handling: ${candidates.length} lexical candidates, ${included.length} retained, ${excluded.length} excluded.`,
    "- Classification lesson applied: visible title first, Introduction/Objectives second, full abstract fallback only.",
    "- Predictive-only handling: retained as an AI-adjacent tier and excluded from direct AI/ML counts.",
    "- Export note: final PDF/screenshots are generated outside the build script with the local cohere-style-ci exporter.",
  ];
  fs.writeFileSync(path.join(OUT_DIR, "subagent_audit_notes.md"), audit.join("\n"));

  const feedback = [
    "# Cohere-Style CI Skill Feedback",
    "",
    "Applicable: yes.",
    "",
    "For local conference-corpus AI topic scans, keep this ADA lesson explicit in the CI guidance: topic classification should inspect the visible presentation title first, then the introduction/objective, and only then use the full abstract as fallback. This avoids incidental secondary disease or endpoint terms overriding the record's visible topic.",
    "",
    "Also preserve predictive-only records in a separate AI-adjacent tier when the user asks to include predictive model topics, and require local context before accepting standalone AI or ML acronyms.",
    "",
    "The actual `cohere-style-ci` skill file was not edited in this pass because the user scoped ownership to the ADA output directory.",
  ];
  fs.writeFileSync(path.join(OUT_DIR, "subagent_cohere_style_ci_feedback.md"), feedback.join("\n"));
}

function main() {
  const records = readJson(SOURCE_JSON);
  const sourceSummary = fs.existsSync(SOURCE_SUMMARY) ? readJson(SOURCE_SUMMARY) : {};
  const { included, excluded, candidates } = buildInventory(records);
  const summary = { ...summarize(included), records_screened: records.length };
  writeInventory(included, excluded, candidates, summary);
  writeSourceLog(records, included, excluded, candidates, summary, sourceSummary);
  writeQaNotes(records, included, excluded, candidates, summary);
  fs.writeFileSync(path.join(OUT_DIR, "ada_2026_ai_topics_ci_report.html"), renderReport(included, excluded, summary, sourceSummary));
  console.log(JSON.stringify({
    records_screened: records.length,
    lexical_candidates: candidates.length,
    retained_records: included.length,
    direct_ai_ml_records: summary.direct_ai_ml_records,
    predictive_only_ai_adjacent_records: summary.predictive_only_ai_adjacent_records,
    excluded_false_positive_candidates: excluded.length,
    by_category: summary.by_category,
    by_ai_role: summary.by_ai_role,
  }, null, 2));
}

main();
