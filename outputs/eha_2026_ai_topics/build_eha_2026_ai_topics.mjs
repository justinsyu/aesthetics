#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";

const OUT_DIR = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1"));
const DATA_DIR = "C:\\Users\\Justin\\Desktop\\eha-2026\\data";
const JSONL_PATH = path.join(DATA_DIR, "eha_2026_abstracts.jsonl");
const SUMMARY_PATH = path.join(DATA_DIR, "summary.json");

const corpusSummary = JSON.parse(fs.readFileSync(SUMMARY_PATH, "utf8"));

const termRules = [
  ["artificial intelligence", /\bartificial intelligence\b/i],
  ["AI", /\bAI\b/],
  ["machine learning", /\bmachine learning\b/i],
  ["deep learning", /\bdeep learning\b/i],
  ["neural network", /\bneural networks?\b/i],
  ["foundation model", /\bfoundation models?\b/i],
  ["large language model", /\blarge language models?\b|\bLLMs?\b/i],
  ["NLP", /\bnatural language processing\b|\bNLP\b/i],
  ["radiomics", /\bradiomics?\b/i],
  ["computer vision", /\bcomputer vision\b/i],
  ["digital pathology", /\bdigital pathology\b/i],
  ["image analysis", /\bimage analysis\b|\bimage-based\b|\bautomated image\b/i],
  ["classifier", /\bclassifiers?\b|\bclassification model\b/i],
  ["random forest", /\brandom forests?\b/i],
  ["gradient boosting", /\bgradient boosting\b|\bXGBoost\b/i],
  ["support vector machine", /\bsupport vector machines?\b|\bSVM\b/i],
  ["computational model", /\bcomputational model(?:ing)?\b|\bcomputational approach\b/i],
  ["predictive model", /\bpredictive models?\b|\bprediction models?\b/i],
  ["algorithmic prediction", /\balgorithm(?:ic)?\b.{0,80}\b(predict|classif|diagnos|risk|prognos|detect)/i],
  ["automated diagnosis", /\bautomated\b.{0,80}\b(diagnos|detect|classif)/i],
];

const antiRules = [
  /\bregression model\b/i,
  /\bcox model\b/i,
  /\blogistic regression\b/i,
  /\blinear regression\b/i,
];

function textOf(record) {
  return [
    record.title,
    record.topic_name,
    record.keywords,
    record.background,
    record.aims,
    record.methods,
    record.results,
    record.summary_conclusion,
    record.abstract_text,
    record.description_text,
  ].filter(Boolean).join("\n");
}

function matchedTerms(text) {
  const terms = termRules.filter(([, rx]) => rx.test(text)).map(([label]) => label);
  if (!terms.length) return [];
  const weakOnlyTerms = new Set(["classifier", "computational model", "predictive model", "algorithmic prediction"]);
  if (terms.every((term) => weakOnlyTerms.has(term))) return [];
  const onlyOrdinaryStats = terms.every((term) => term === "predictive model" || term === "algorithmic prediction")
    && antiRules.some((rx) => rx.test(text))
    && !/\b(machine learning|artificial intelligence|deep learning|neural|random forest|gradient boosting|XGBoost|SVM|radiomic|NLP|LLM|digital pathology|computer vision)\b/i.test(text);
  return onlyOrdinaryStats ? [] : terms;
}

function firstMatch(text, rules, fallback) {
  const hit = rules.find(([, rx]) => rx.test(text));
  return hit ? hit[0] : fallback;
}

function diseaseArea(record, text) {
  const haystack = `${record.title || ""}\n${record.keywords || ""}\n${record.topic_name || ""}\n${text}`;
  if (/\bAML\b/.test(haystack) || /acute myeloid leukemia/i.test(haystack)) return "Acute myeloid leukemia";
  if (/\bALL\b/.test(haystack) || /acute lymphoblastic leukemia/i.test(haystack)) return "Acute lymphoblastic leukemia";
  if (/\bMDS\b/.test(haystack) || /myelodysplastic/i.test(haystack)) return "Myelodysplastic syndromes";
  if (/\bMPN\b/.test(haystack) || /myeloproliferative|myelofibrosis|polycythemia|essential thrombocyth/i.test(haystack)) return "Myeloproliferative neoplasms";
  if (/\bMM\b/.test(haystack) || /multiple myeloma|plasma cell/i.test(haystack)) return "Multiple myeloma";
  if (/lymphoma|DLBCL|Hodgkin|mantle cell|follicular/i.test(haystack)) return "Lymphoma";
  if (/\bCLL\b/.test(haystack) || /chronic lymphocytic leukemia/i.test(haystack)) return "CLL";
  if (/\bCAR[- ]?T\b/i.test(haystack) || /cell therapy|cellular therapy/i.test(haystack)) return "CAR-T / cell therapy";
  if (/transplant|HSCT|stem cell transplant/i.test(haystack)) return "Transplantation";
  if (/sickle cell|thalassemia|hemoglobinopath/i.test(haystack)) return "Hemoglobinopathies";
  if (/thrombo|hemostasis|haemostasis|coagulation|bleeding/i.test(haystack)) return "Thrombosis / hemostasis";
  if (/anemia|anaemia|erythro|red blood cell/i.test(haystack)) return "Anemia / red cells";
  return record.topic_name ? record.topic_name.replace(/^\d+\.\s*/, "").split(" - ")[0] : "Other hematology";
}

function clusterFor(text) {
  return firstMatch(text, [
    ["Digital pathology, imaging, and morphology", /digital pathology|image analysis|image-based|computer vision|radiomics|morpholog|microscop|smear|segmentation/i],
    ["Clinical prediction and risk stratification", /predict|prediction|prognos|risk strat|survival|relapse|mortality|outcome/i],
    ["Diagnosis and classification", /diagnos|classif|detect|screening|differenti/i],
    ["Treatment response and precision therapy", /response|therapy|treatment|personaliz|precision|drug|resistance/i],
    ["Genomics, multi-omics, and biomarker discovery", /genomic|transcriptomic|proteomic|multi-omic|single-cell|biomarker|mutation|sequencing/i],
    ["NLP, LLMs, and text/data extraction", /natural language processing|NLP|large language model|LLM|text mining|language model/i],
    ["Operational workflow and digital tools", /workflow|remote|digital|app|electronic|automation|triage|decision support/i],
  ], "Other AI / computational methods");
}

function useCaseFor(text) {
  return firstMatch(text, [
    ["Prognosis / risk stratification", /prognos|risk strat|survival|relapse|mortality|outcome|predict/i],
    ["Diagnosis / classification", /diagnos|classif|detect|screen/i],
    ["Treatment response / therapy selection", /response|treatment|therapy|drug|resistance|personaliz/i],
    ["Image, pathology, or morphology analysis", /image|pathology|morpholog|radiomic|microscop|smear|segmentation/i],
    ["Biomarker or omics discovery", /biomarker|genomic|transcriptomic|proteomic|multi-omic|single-cell|sequencing/i],
    ["Text extraction / NLP", /natural language processing|NLP|large language model|LLM|text/i],
  ], "Other AI use case");
}

function methodTypeFor(text) {
  return firstMatch(text, [
    ["Deep learning / neural networks", /deep learning|neural network|transformer|foundation model/i],
    ["NLP / large language model", /natural language processing|NLP|large language model|LLM/i],
    ["Radiomics / image analysis", /radiomic|image analysis|computer vision|digital pathology|segmentation/i],
    ["Tree-based ML", /random forest|gradient boosting|XGBoost/i],
    ["Classical machine learning", /machine learning|support vector machine|SVM|classifier/i],
    ["Computational / predictive model", /computational model|predictive model|prediction model|algorithm/i],
  ], "AI / ML method not specified");
}

function csvEscape(value) {
  const s = String(value ?? "");
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function countBy(records, key) {
  const counts = new Map();
  for (const rec of records) counts.set(rec[key] || "Unspecified", (counts.get(rec[key] || "Unspecified") || 0) + 1);
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

function pct(n, d) {
  return `${((n / d) * 100).toFixed(1)}%`;
}

async function loadRecords() {
  const records = [];
  const rl = readline.createInterface({
    input: fs.createReadStream(JSONL_PATH, { encoding: "utf8" }),
    crlfDelay: Infinity,
  });
  for await (const line of rl) {
    if (!line.trim()) continue;
    const record = JSON.parse(line);
    const text = textOf(record);
    const terms = matchedTerms(text);
    if (!terms.length) continue;
    const normalized = {
      record_ref: record.abstract_number || record.eha_abstract_id || String(record.content_id),
      content_id: record.content_id,
      abstract_number: record.abstract_number || "",
      eha_abstract_id: record.eha_abstract_id || "",
      title: record.title || "",
      presentation_type: record.presentation_type || record.marker_name || "",
      session_title: record.session_title || "",
      topic_name: record.topic_name || "",
      date: record.date || "",
      authors: Array.isArray(record.authors) ? record.authors.join("; ") : (record.authors || ""),
      keywords: record.keywords || "",
      href: record.href || "",
      matched_terms: terms.join("; "),
      ai_cluster: clusterFor(text),
      disease_area: diseaseArea(record, text),
      use_case: useCaseFor(text),
      method_type: methodTypeFor(text),
      evidence_excerpt: [record.methods, record.results, record.summary_conclusion, record.background]
        .filter(Boolean)
        .join(" ")
        .replace(/\s+/g, " ")
        .slice(0, 520),
    };
    records.push(normalized);
  }
  records.sort((a, b) => a.ai_cluster.localeCompare(b.ai_cluster) || a.disease_area.localeCompare(b.disease_area) || a.record_ref.localeCompare(b.record_ref));
  return records;
}

function topRows(counts, limit = 7) {
  const max = counts[0]?.[1] || 1;
  return counts.slice(0, limit).map(([label, value]) => `
    <div class="bar-row">
      <div class="bar-label">${esc(label)}</div>
      <div class="bar-track"><span style="width:${Math.max(8, (value / max) * 100).toFixed(1)}%"></span></div>
      <div class="bar-count">${value}</div>
    </div>`).join("");
}

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function clip(value, max) {
  const s = String(value ?? "");
  return s.length > max ? `${s.slice(0, Math.max(0, max - 1))}...` : s;
}

function cite(ref) {
  return `<a class="cite" href="${esc(ref.href || "#")}" title="${esc(ref.label)}">${ref.n}</a>`;
}

function makeRefs(records) {
  const refs = [{
    n: 1,
    label: "EHA 2026 local abstract corpus summary",
    source: "EHA Library scrape summary",
    date: corpusSummary.scraped_at,
    href: corpusSummary.source_url,
    evidence: `${corpusSummary.detail_rows} detail rows; ${corpusSummary.listing_rows} listing rows; ${corpusSummary.detail_errors} detail errors.`,
  }];
  const picked = [
    ...records.slice(0, 2),
    ...countBy(records, "ai_cluster").slice(0, 6).map(([cluster]) => records.find((r) => r.ai_cluster === cluster)).filter(Boolean),
    ...countBy(records, "disease_area").slice(0, 4).map(([area]) => records.find((r) => r.disease_area === area)).filter(Boolean),
  ];
  const seen = new Set();
  for (const rec of picked) {
    const id = rec.content_id || rec.record_ref;
    if (seen.has(id)) continue;
    seen.add(id);
    refs.push({
      n: refs.length + 1,
      label: `${rec.record_ref} ${rec.eha_abstract_id}`.trim(),
      source: rec.title,
      date: rec.date || rec.presentation_type,
      href: rec.href,
      evidence: `${rec.ai_cluster}; ${rec.disease_area}; matched terms: ${rec.matched_terms}.`,
      rec,
    });
    if (refs.length >= 16) break;
  }
  return refs;
}

function exampleRecords(records, limit = 9) {
  const clusters = countBy(records, "ai_cluster").map(([cluster]) => cluster);
  const picked = [];
  const seen = new Set();
  for (const cluster of clusters) {
    for (const rec of records.filter((r) => r.ai_cluster === cluster).slice(0, 2)) {
      if (seen.has(rec.content_id)) continue;
      picked.push(rec);
      seen.add(rec.content_id);
      if (picked.length >= limit) return picked;
    }
  }
  for (const rec of records) {
    if (seen.has(rec.content_id)) continue;
    picked.push(rec);
    seen.add(rec.content_id);
    if (picked.length >= limit) break;
  }
  return picked;
}

function exampleTable(records, refsById) {
  return exampleRecords(records).map((rec) => {
    const ref = refsById.get(rec.content_id) || refsById.get(rec.record_ref);
    return `<tr>
      <td>${esc(rec.record_ref)}</td>
      <td>${esc(rec.disease_area)}</td>
      <td>${esc(rec.ai_cluster)}${ref ? cite(ref) : ""}</td>
      <td>${esc(rec.method_type)}</td>
    </tr>`;
  }).join("");
}

function htmlDeck(records) {
  const clusterCounts = countBy(records, "ai_cluster");
  const diseaseCounts = countBy(records, "disease_area");
  const useCaseCounts = countBy(records, "use_case");
  const methodCounts = countBy(records, "method_type");
  const presentationCounts = countBy(records, "presentation_type");
  const refs = makeRefs(records);
  const refsById = new Map(refs.filter((r) => r.rec).flatMap((r) => [[r.rec.content_id, r], [r.rec.record_ref, r]]));
  const corpusRef = refs[0];
  const total = corpusSummary.detail_rows;
  const aiCount = records.length;
  const topClusterRef = refs.find((r) => r.rec?.ai_cluster === clusterCounts[0]?.[0]) || refs[1] || corpusRef;
  const topDiseaseRef = refs.find((r) => r.rec?.disease_area === diseaseCounts[0]?.[0]) || refs[1] || corpusRef;
  const slides = 8;

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1600">
<title>EHA 2026 AI-related abstract topics</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root{--ink:#10120f;--muted:#5c6257;--paper:#f6f1e8;--paper2:#ebe4d6;--card:#fffaf0;--line:#1b1f17;--lime:#d7ff5f;--orange:#ffb86b;--blue:#b8d8ff;--pink:#ffd3e0;--gray:#d6d0c2;--red:#ff8a76;--shadow:0 18px 48px rgba(16,18,15,.08);--radius:24px}
*{box-sizing:border-box}html,body{margin:0;font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:var(--ink);background:#15150f}.slide{width:1600px;height:900px;position:relative;overflow:hidden;background:var(--paper);padding:36px 0 20px}.slide:before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 16px 16px,rgba(16,18,15,.09) 1.2px,transparent 1.3px);background-size:28px 28px;opacity:.34}.slide.dark{background:#11130f;color:var(--paper)}.slide.dark:before{background:radial-gradient(circle at 16px 16px,rgba(215,255,95,.18) 1.2px,transparent 1.3px);background-size:30px 30px;opacity:.25}.wrap{position:relative;z-index:1;width:min(1360px,calc(100vw - 56px));height:100%;margin:0 auto}.eyebrow{display:inline-flex;align-items:center;gap:10px;border:1.5px solid var(--line);background:var(--lime);border-radius:999px;padding:8px 12px;text-transform:uppercase;font-size:15px;font-weight:800;letter-spacing:.02em;margin-bottom:22px}.dark .eyebrow{color:var(--ink)}h1,h2,h3{font-family:"Space Grotesk",Inter,sans-serif;margin:0}h1{font-size:72px;line-height:.94;font-weight:650;max-width:1240px}h2{font-size:56px;line-height:.98;font-weight:650;margin-bottom:22px}.dek{font-size:24px;line-height:1.22;max-width:1180px;color:var(--muted);margin:20px 0}.dark .dek{color:rgba(246,241,232,.82)}.grid{display:grid;gap:20px}.cols-3{grid-template-columns:repeat(3,1fr)}.cols-2{grid-template-columns:repeat(2,1fr)}.card{background:rgba(255,250,240,.9);border:1.5px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:24px}.dark .card{background:#1a1d17;border-color:rgba(246,241,232,.45);box-shadow:none}.metric{padding:20px 22px}.metric .num{font-family:"Space Grotesk";font-size:58px;line-height:1;font-weight:650}.metric .label{font-size:16px;color:var(--muted);margin-top:7px}.dark .metric .label{color:rgba(246,241,232,.68)}.summary{background:#11130f;color:var(--paper);padding:22px 28px;border-radius:var(--radius);border:1.5px solid var(--line);margin-top:20px}.summary h3{font-size:26px;margin-bottom:10px}.summary li,.bullets li{list-style:none;position:relative;margin:0 0 10px 0;padding-left:22px;font-size:21px;line-height:1.22}.summary li{font-size:19px;margin-bottom:8px}.summary li:before,.bullets li:before{content:"";width:9px;height:9px;border-radius:50%;background:var(--lime);position:absolute;left:0;top:.55em}.bar-row{display:grid;grid-template-columns:310px 1fr 52px;gap:14px;align-items:center;margin:12px 0}.bar-label{font-size:19px;line-height:1.15}.bar-track{height:20px;border:1.5px solid var(--line);border-radius:999px;background:rgba(255,250,240,.6);overflow:hidden}.bar-track span{display:block;height:100%;background:linear-gradient(90deg,var(--lime),var(--orange))}.bar-count{font-weight:800;text-align:right}.table{width:100%;border-collapse:separate;border-spacing:0;font-size:16px;line-height:1.2;overflow:hidden;border:1.5px solid var(--line);border-radius:18px;background:rgba(255,250,240,.92)}.table th,.table td{padding:12px 14px;border-bottom:1px solid rgba(27,31,23,.22);vertical-align:top}.table th{text-align:left;background:#11130f;color:var(--paper);font-weight:700}.table tr:last-child td{border-bottom:0}.cite{font-size:.58em;vertical-align:super;margin-left:2px;font-weight:900;color:inherit;text-decoration:none}.refs{font-size:14px}.refs td:nth-child(2){font-weight:650}.slide-num{position:absolute;z-index:2;right:42px;bottom:26px;font-size:12px;text-transform:uppercase;color:rgba(16,18,15,.5);font-weight:800}.dark .slide-num{color:rgba(246,241,232,.55)}.note{font-size:16px;line-height:1.3;color:var(--muted);margin-top:16px}.dark .note{color:rgba(246,241,232,.68)}.split{display:grid;grid-template-columns:1.04fr .96fr;gap:26px;align-items:start}.tag{display:inline-block;border:1.2px solid var(--line);border-radius:999px;background:var(--blue);font-weight:800;font-size:13px;text-transform:uppercase;padding:6px 9px;margin:0 6px 6px 0}.small{font-size:18px;line-height:1.28}.examples td:nth-child(3){font-weight:650}@media screen{body{display:flex;flex-direction:column;align-items:center;gap:34px;padding:36px 0}.slide{max-width:100vw;max-height:100vh;box-shadow:0 24px 80px rgba(0,0,0,.45)}}@media print{@page{size:1600px 900px;margin:0}body{background:#fff}.slide{page-break-after:always}.slide:last-child{page-break-after:auto}}
</style>
</head>
<body>
<article class="slide">
  <div class="wrap">
    <div class="eyebrow">EHA 2026 | AI-related abstracts and posters</div>
    <h1>AI activity appears as a focused cross-cutting layer within the EHA abstract corpus</h1>
    <p class="dek">A local full-corpus screen identified ${aiCount} AI-related records among ${total} EHA 2026 detail records (${pct(aiCount, total)}), using explicit AI, machine-learning, language-model, radiomics, image-analysis, and related method terms.${cite(corpusRef)}</p>
    <div class="grid cols-3">
      <div class="card metric"><div class="num">${total.toLocaleString()}</div><div class="label">Local EHA detail records screened${cite(corpusRef)}</div></div>
      <div class="card metric"><div class="num">${aiCount}</div><div class="label">AI-related records retained${cite(corpusRef)}</div></div>
      <div class="card metric"><div class="num">${clusterCounts.length}</div><div class="label">Topic clusters assigned from retained records${cite(corpusRef)}</div></div>
    </div>
    <div class="summary"><h3>Executive summary</h3><ul>
      <li>The largest cluster is ${esc(clusterCounts[0][0])}, with ${clusterCounts[0][1]} retained records.${cite(topClusterRef)}</li>
      <li>The most frequent disease area among retained records is ${esc(diseaseCounts[0][0])}, with ${diseaseCounts[0][1]} records.${cite(topDiseaseRef)}</li>
      <li>Record-level exports preserve EHA abstract IDs, abstract numbers, source URLs, matched terms, and derived classifications for review.${cite(corpusRef)}</li>
    </ul></div>
  </div><div class="slide-num">01 / ${slides}</div>
</article>

<article class="slide dark">
  <div class="wrap">
    <div class="eyebrow">Methods | Local corpus</div>
    <h2>Screening used explicit AI-method language and retained auditable record references</h2>
    <div class="grid cols-2">
      <div class="card"><h3>Inclusion logic</h3><ul class="bullets">
        <li>Records were retained when titles, metadata, or abstract sections matched terms for AI, ML, deep learning, neural networks, NLP, LLMs, radiomics, image analysis, digital pathology, classifiers, or AI-framed prediction.</li>
        <li>Ordinary regression, Cox models, or statistical modeling were excluded when no AI or machine-learning framing appeared in the source record.</li>
        <li>Derived cluster labels are analytic classifications for review, while record metadata and source URLs remain preserved.</li>
      </ul></div>
      <div class="card"><h3>Corpus reconciliation</h3><ul class="bullets">
        <li>The local summary file lists ${corpusSummary.listing_rows} listing rows, ${corpusSummary.detail_rows} detail rows, and ${corpusSummary.detail_errors} detail errors.${cite(corpusRef)}</li>
        <li>The retained AI set equals ${pct(aiCount, total)} of local detail records.${cite(corpusRef)}</li>
        <li>Companion CSV and JSON files contain normalized records for downstream filtering and manual validation.${cite(corpusRef)}</li>
      </ul></div>
    </div>
    <p class="note">Source basis: local EHA 2026 scrape artifacts in <code>C:\\Users\\Justin\\Desktop\\eha-2026\\data</code>. External source URLs are preserved where supplied by the local records.</p>
  </div><div class="slide-num">02 / ${slides}</div>
</article>

<article class="slide">
  <div class="wrap">
    <div class="eyebrow">Topic clusters | Retained AI set</div>
    <h2>Clinical prediction and image-oriented methods form the visible center of AI activity</h2>
    <div class="split">
      <div class="card">${topRows(clusterCounts, 8)}</div>
      <div class="card"><h3>Reading the clusters</h3><ul class="bullets">
        <li>Cluster assignment is based on source language and is intended for review triage, not a formal taxonomy.${cite(corpusRef)}</li>
        <li>Examples retain their original EHA IDs and URLs so cluster assignments can be checked against source text.${cite(topClusterRef)}</li>
        <li>Counts reflect local corpus screening, not live EHA website recrawling.${cite(corpusRef)}</li>
      </ul></div>
    </div>
  </div><div class="slide-num">03 / ${slides}</div>
</article>

<article class="slide">
  <div class="wrap">
    <div class="eyebrow">Disease areas | Retained AI set</div>
    <h2>AI-related work spans malignant and non-malignant hematology categories</h2>
    <div class="grid cols-2">
      <div class="card"><h3>Disease area distribution</h3>${topRows(diseaseCounts, 8)}</div>
      <div class="card"><h3>Presentation type distribution</h3>${topRows(presentationCounts, 8)}<p class="note">Distribution labels are taken from EHA record metadata when available.${cite(corpusRef)}</p></div>
    </div>
  </div><div class="slide-num">04 / ${slides}</div>
</article>

<article class="slide dark">
  <div class="wrap">
    <div class="eyebrow">Use cases and methods | Retained AI set</div>
    <h2>Most retained records frame AI around prediction, diagnosis/classification, image analysis, or biomarker discovery</h2>
    <div class="grid cols-2">
      <div class="card"><h3>Use-case distribution</h3>${topRows(useCaseCounts, 7)}</div>
      <div class="card"><h3>Method-type distribution</h3>${topRows(methodCounts, 7)}</div>
    </div>
  </div><div class="slide-num">05 / ${slides}</div>
</article>

<article class="slide">
  <div class="wrap">
    <div class="eyebrow">Examples | Record-level traceability</div>
    <h2>Representative records show how the retained set maps into reviewable evidence rows</h2>
    <table class="table examples">
      <thead><tr><th>Record</th><th>Disease area</th><th>Assigned AI topic</th><th>Method type</th></tr></thead>
      <tbody>${exampleTable(records, refsById)}</tbody>
    </table>
    <p class="note">The table displays a sample of retained records. Full retained records are available in the companion CSV and JSON exports.${cite(corpusRef)}</p>
  </div><div class="slide-num">06 / ${slides}</div>
</article>

<article class="slide">
  <div class="wrap">
    <div class="eyebrow">Limitations | Classification scope</div>
    <h2>The analysis is a local-corpus screen and should be treated as an auditable topic inventory</h2>
    <div class="grid cols-2">
      <div class="card"><h3>What is source-backed</h3><ul class="bullets">
        <li>Corpus size, retained record count, original titles, EHA IDs, abstract numbers, presentation metadata, and URLs come from local source records.${cite(corpusRef)}</li>
        <li>Matched AI terms are deterministic lexical matches stored per record in the companion exports.${cite(corpusRef)}</li>
      </ul></div>
      <div class="card"><h3>What is analyst-derived</h3><ul class="bullets">
        <li>Topic cluster, disease area, use-case, and method-type labels are rule-based classifications for review.</li>
        <li>Records without explicit AI/ML framing may be excluded even if they used advanced statistics.</li>
        <li>Live-posting changes after the local scrape timestamp were not evaluated in this run.${cite(corpusRef)}</li>
      </ul></div>
    </div>
  </div><div class="slide-num">07 / ${slides}</div>
</article>

<article class="slide">
  <div class="wrap">
    <div class="eyebrow">References 1-${refs.length}</div>
    <h2>References</h2>
    <table class="table refs">
      <thead><tr><th>Ref</th><th>Source</th><th>Date / Status / Source Owner</th><th>Evidence Used in Report</th></tr></thead>
      <tbody>${refs.map((r) => `<tr><td>${r.n}</td><td><a href="${esc(r.href)}">${esc(clip(r.source, 108))}</a></td><td>${esc(r.date || "Local record")}</td><td>${esc(clip(r.evidence, 132))}</td></tr>`).join("")}</tbody>
    </table>
  </div><div class="slide-num">08 / ${slides}</div>
</article>
</body>
</html>`;
}

function writeArtifacts(records) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const jsonPath = path.join(OUT_DIR, "ai_related_records.json");
  const csvPath = path.join(OUT_DIR, "ai_related_records.csv");
  const htmlPath = path.join(OUT_DIR, "eha_2026_ai_topics_cohere_ci.html");
  const notesPath = path.join(OUT_DIR, "method_notes.md");

  fs.writeFileSync(jsonPath, JSON.stringify({
    generated_at: new Date().toISOString(),
    source_corpus: JSONL_PATH,
    corpus_summary: corpusSummary,
    total_detail_records: corpusSummary.detail_rows,
    ai_related_records: records.length,
    records,
    counts: {
      by_cluster: Object.fromEntries(countBy(records, "ai_cluster")),
      by_disease_area: Object.fromEntries(countBy(records, "disease_area")),
      by_use_case: Object.fromEntries(countBy(records, "use_case")),
      by_method_type: Object.fromEntries(countBy(records, "method_type")),
      by_presentation_type: Object.fromEntries(countBy(records, "presentation_type")),
    },
  }, null, 2));

  const cols = ["record_ref", "content_id", "abstract_number", "eha_abstract_id", "title", "presentation_type", "session_title", "topic_name", "date", "authors", "keywords", "href", "matched_terms", "ai_cluster", "disease_area", "use_case", "method_type", "evidence_excerpt"];
  const csv = [cols.join(","), ...records.map((rec) => cols.map((c) => csvEscape(rec[c])).join(","))].join("\n") + "\n";
  fs.writeFileSync(csvPath, csv);
  fs.writeFileSync(htmlPath, htmlDeck(records));

  const clusterLines = countBy(records, "ai_cluster").map(([k, v]) => `- ${k}: ${v}`).join("\n");
  const diseaseLines = countBy(records, "disease_area").slice(0, 10).map(([k, v]) => `- ${k}: ${v}`).join("\n");
  const terms = termRules.map(([label]) => label).join(", ");
  const notes = `# EHA 2026 AI-related abstract/poster scan

Generated: ${new Date().toISOString()}

## Source corpus

- Local JSONL: \`${JSONL_PATH}\`
- Local summary: \`${SUMMARY_PATH}\`
- EHA source URL recorded in summary: ${corpusSummary.source_url}
- Listing rows: ${corpusSummary.listing_rows}
- Detail rows screened: ${corpusSummary.detail_rows}
- Detail errors recorded by scrape summary: ${corpusSummary.detail_errors}

## Inclusion and exclusion logic

Records were retained when source text matched one or more AI-related method terms across title, topic, keywords, abstract sections, or description text. Terms screened: ${terms}.

Records were excluded when they only appeared to describe ordinary statistical models, regression, Cox models, or logistic/linear regression without explicit AI, machine-learning, deep-learning, NLP, radiomics, image-analysis, classifier, or comparable AI-method framing.

## Results

- Retained AI-related records: ${records.length}
- Share of local detail corpus: ${pct(records.length, corpusSummary.detail_rows)}

## Topic clusters

${clusterLines}

## Top disease areas

${diseaseLines}

## Limitations

- This is a deterministic local-corpus screen, not a live recrawl of EHA pages.
- Topic clusters, disease areas, use cases, and method types are rule-based analyst classifications for review.
- Records using advanced statistics but no explicit AI/ML framing may be excluded by design.
- Some abstracts may have embargoed or empty abstract sections in the local scrape; available metadata was still screened.

## Output files

- \`ai_related_records.csv\`
- \`ai_related_records.json\`
- \`eha_2026_ai_topics_cohere_ci.html\`
- \`eha_2026_ai_topics_cohere_ci.pdf\` after the export step succeeds.
`;
  fs.writeFileSync(notesPath, notes);
  return { jsonPath, csvPath, htmlPath, notesPath };
}

const records = await loadRecords();
const outputs = writeArtifacts(records);
console.log(JSON.stringify({
  total_detail_records: corpusSummary.detail_rows,
  ai_related_records: records.length,
  top_clusters: countBy(records, "ai_cluster").slice(0, 5),
  outputs,
}, null, 2));
