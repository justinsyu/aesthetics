import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const packetsDir = path.join(root, "research", "packets");
const launchDir = path.join(root, "research", "launch-timeline");
const allowedBuckets = ["0-12 months", "12-24 months", "24-36 months", "36+ months"];

await fs.mkdir(launchDir, { recursive: true });

const files = (await fs.readdir(launchDir)).filter((file) => file.endsWith(".json"));
for (const file of files) {
  const launchPath = path.join(launchDir, file);
  const launch = JSON.parse(await fs.readFile(launchPath, "utf8"));
  const assetId = launch.asset_id || path.basename(file, ".json");
  const packetPath = path.join(packetsDir, `${assetId}.json`);
  const packet = JSON.parse(await fs.readFile(packetPath, "utf8"));
  const bucket = normalizeBucket(launch.launch_timeline_bucket, launch.launch_timeline_display || launch.estimated_launch_date_range);

  packet.launch_timeline_bucket = bucket;
  packet.launch_timeline_display = launch.launch_timeline_display || packet.expected_launch_window || bucket;
  packet.estimated_launch_date_range = normalizeDateRange(launch.estimated_launch_date_range);
  packet.launch_timeline_confidence = launch.launch_timeline_confidence || "Medium";
  packet.rationale = packet.rationale || {};
  packet.rationale.launch_timeline = normalizeRationale(launch, bucket, packet.launch_timeline_display);
  packet.sources = mergeSources(packet.sources || [], normalizeSources(launch.sources || []));

  await fs.writeFile(packetPath, `${JSON.stringify(packet, null, 2)}\n`);
  console.log(`Applied launch timeline packet for ${assetId}: ${bucket}`);
}

function normalizeBucket(value, display = "") {
  if (allowedBuckets.includes(value)) return value;
  const text = `${value || ""} ${display || ""}`;
  if (/marketed|launched/i.test(text)) return "0-12 months";
  const yearMatch = text.match(/\b(20\d{2})(?:[-/](\d{1,2})(?:[-/](\d{1,2}))?)?\b/);
  if (!yearMatch) return "36+ months";
  const year = Number(yearMatch[1]);
  const quarter = Number(text.match(/\bQ([1-4])\b/i)?.[1]);
  const month = Number(yearMatch[2] || (quarter ? quarter * 3 - 1 : 7));
  const estimate = new Date(Date.UTC(year, Math.max(0, month - 1), Number(yearMatch[3] || 1)));
  const months = (estimate - new Date("2026-05-28T00:00:00Z")) / (1000 * 60 * 60 * 24 * 30.44);
  if (months <= 12) return "0-12 months";
  if (months <= 24) return "12-24 months";
  if (months <= 36) return "24-36 months";
  return "36+ months";
}

function normalizeDateRange(value) {
  if (!value) return null;
  if (typeof value === "object") return value;
  const text = String(value);
  const dates = text.match(/\b20\d{2}(?:-\d{2}(?:-\d{2})?)?\b/g) || [];
  if (dates.length >= 2) return { start: expandDate(dates[0], false), end: expandDate(dates[1], true), label: text };
  if (dates.length === 1) return { start: expandDate(dates[0], false), end: null, label: text };
  return { start: null, end: null, label: text };
}

function expandDate(value, end) {
  if (/^\d{4}$/.test(value)) return `${value}-${end ? "12-31" : "01-01"}`;
  if (/^\d{4}-\d{2}$/.test(value)) return `${value}-${end ? "28" : "01"}`;
  return value;
}

function normalizeRationale(launch, bucket, display) {
  const base = typeof launch.launch_timeline_rationale === "string"
    ? { explanation: launch.launch_timeline_rationale }
    : (launch.launch_timeline_rationale || {});
  return {
    value: bucket,
    basis_type: base.basis_type || "source_derived",
    method: base.method || "Source-backed asset-level launch timeline assessment",
    explanation: base.explanation || String(launch.launch_timeline_rationale || ""),
    source_refs: base.source_refs || inferRefs(launch.sources || []),
    source_fields: {
      ...(base.source_fields || {}),
      launch_timeline_bucket: bucket,
      launch_timeline_display: display,
      estimated_launch_date_range: normalizeDateRange(launch.estimated_launch_date_range),
      launch_timeline_confidence: launch.launch_timeline_confidence || "Medium"
    }
  };
}

function normalizeSources(sources) {
  return sources.map((source, index) => ({
    source_id: source.source_id || inferSourceId(source, index),
    title: source.title || source.name || source.url || `Launch timeline source ${index + 1}`,
    type: source.type || "Launch timeline source",
    url: source.url,
    date: source.date || "2026-05-28",
    supports: Array.isArray(source.supports) ? source.supports : [source.supports || source.evidence || "Supports launch timeline assessment"]
  })).filter((source) => source.url);
}

function inferRefs(sources) {
  return normalizeSources(sources).map((source) => source.source_id).filter(Boolean);
}

function inferSourceId(source, index) {
  const nct = `${source.url || ""} ${source.title || ""} ${source.name || ""}`.match(/NCT\d{8}/i)?.[0];
  if (nct) return `ctgov:${nct.toUpperCase()}`;
  const host = source.url ? new URL(source.url).hostname.replace(/^www\./, "").split(".")[0] : "source";
  return `launch:${host}:${index + 1}`;
}

function mergeSources(left, right) {
  const seen = new Set();
  const merged = [];
  for (const source of [...left, ...right]) {
    const key = source.url || source.source_id || source.title;
    if (seen.has(key)) continue;
    seen.add(key);
    merged.push(source);
  }
  return merged;
}
