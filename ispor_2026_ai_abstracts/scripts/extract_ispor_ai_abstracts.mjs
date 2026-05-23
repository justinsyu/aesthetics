import fs from "node:fs/promises";
import path from "node:path";

const root = path.resolve("/Users/justinyu/Desktop/linkedin-posts/ispor_2026_ai_abstracts");
const dataDir = path.join(root, "data");
const jsonDir = path.join(dataDir, "per_abstract_json");
const mdDir = path.join(dataDir, "per_abstract_md");

const searchUrl =
  "https://www.ispor.org/heor-resources/presentations-database/results?filter=%28events%253A%25222026-05%252C%2520ISPOR%25202026%252C%2520Philadelphia%252C%2520PA%252C%2520USA%2522%29%257C%28citable%253A%2522True%2522%29%257C%28categories%253A%2522Methodological%2520%2526%2520Statistical%2520Research%255EArtificial%2520Intelligence%252C%2520Machine%2520Learning%252C%2520Predictive%2520Analytics%2522%29&resultsPage=1";

const filters = [
  '(events:"2026-05, ISPOR 2026, Philadelphia, PA, USA")',
  '(citable:"True")',
  '(categories:"Methodological & Statistical Research^Artificial Intelligence, Machine Learning, Predictive Analytics")',
];

const facets = ["citable", "categories", "areaofstudy", "disease", "events"];

function csvEscape(value) {
  if (value == null) return "";
  const text = String(value);
  return /[",\n\r]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function stripHtml(value) {
  return String(value || "")
    .replaceAll("&amp;", "&")
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">")
    .replaceAll("&quot;", '"')
    .replaceAll("&#39;", "'")
    .replace(/<[^>]+>/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function slugify(value) {
  return stripHtml(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 90);
}

function parseSections(description) {
  const labels = ["OBJECTIVES", "METHODS", "RESULTS", "CONCLUSIONS"];
  const sections = {};
  const text = stripHtml(description);
  for (let i = 0; i < labels.length; i += 1) {
    const label = labels[i];
    const next = labels[i + 1];
    const pattern = next
      ? new RegExp(`${label}:\\s*([\\s\\S]*?)\\s*${next}:`, "i")
      : new RegExp(`${label}:\\s*([\\s\\S]*)$`, "i");
    const match = text.match(pattern);
    sections[label.toLowerCase()] = match ? match[1].trim() : "";
  }
  return sections;
}

function normalizeRecord(record, index) {
  const sections = parseSections(record.description);
  return {
    index,
    uid: record.uid,
    session_code: record.sessioncode || "",
    title: stripHtml(record.fulltitle || record.title),
    authors: stripHtml(record.authors),
    journal_information: stripHtml(record.journalinformation),
    event: stripHtml(record.events),
    parent_title: stripHtml(record.ParentTitle),
    disease: stripHtml(record.disease),
    area_of_study: stripHtml(record.areaofstudy),
    categories: stripHtml(record.categories),
    citable: stripHtml(record.citable || record.citeable),
    published: record.published || "",
    last_modified: record.lastmodified || "",
    url: record.url || record.location || record.ParentLink || "",
    abstract: stripHtml(record.description),
    objectives: sections.objectives,
    methods: sections.methods,
    results: sections.results,
    conclusions: sections.conclusions,
    raw: record,
  };
}

function markdownFor(record) {
  return `# ${record.index}. ${record.title}

- Session code: ${record.session_code}
- Authors: ${record.authors}
- Disease: ${record.disease || "Not specified"}
- Categories: ${record.categories}
- Journal: ${record.journal_information}
- Published: ${record.published}
- URL: ${record.url}

## Objectives

${record.objectives || "Not separately identified"}

## Methods

${record.methods || "Not separately identified"}

## Results

${record.results || "Not separately identified"}

## Conclusions

${record.conclusions || "Not separately identified"}
`;
}

async function fetchPage(page, pageSize = 200) {
  const params = new URLSearchParams();
  params.set("query", "*");
  params.set("default", "AND");
  params.set("xsl", "json");
  params.set("facet", "true");
  params.set("tune", "false");
  params.set("col", "2");
  params.set("pagesize", String(pageSize));
  params.set("filter", filters.join(" AND "));
  params.set("page", String(page));
  params.set("sort", "relevance");
  for (const facet of facets) {
    params.append("facet.field", facet);
    params.append(`f.${facet}.size`, "1000");
  }
  const apiUrl = `https://isporsearch303.aws.mtxgp.net/rest/v2/api/search?${params}`;
  const response = await fetch(apiUrl, {
    headers: {
      accept: "application/json",
      "user-agent": "Mozilla/5.0 ISPOR abstract extraction for local research archive",
    },
  });
  if (!response.ok) {
    throw new Error(`SearchBlox request failed: ${response.status} ${response.statusText}`);
  }
  return { apiUrl, body: await response.json() };
}

async function main() {
  await fs.mkdir(jsonDir, { recursive: true });
  await fs.mkdir(mdDir, { recursive: true });

  const first = await fetchPage(1, 200);
  const records = (first.body.result || []).map((record, i) => normalizeRecord(record, i + 1));

  await fs.writeFile(
    path.join(dataDir, "query_metadata.json"),
    JSON.stringify(
      {
        extracted_at: new Date().toISOString(),
        user_url: searchUrl,
        api_url: first.apiUrl,
        requested_count_from_user: 148,
        api_hits: Number(first.body.hits || records.length),
        api_last_page: Number(first.body.lastPage || 1),
        api_start: first.body.start,
        api_end: first.body.end,
        filter_returned_by_api: first.body.filter,
      },
      null,
      2,
    ),
  );
  await fs.writeFile(path.join(dataDir, "raw_searchblox_response.json"), JSON.stringify(first.body, null, 2));
  await fs.writeFile(path.join(dataDir, "abstracts.json"), JSON.stringify(records, null, 2));

  const csvColumns = [
    "index",
    "session_code",
    "title",
    "authors",
    "disease",
    "area_of_study",
    "categories",
    "journal_information",
    "published",
    "url",
    "objectives",
    "methods",
    "results",
    "conclusions",
  ];
  const csv = [
    csvColumns.join(","),
    ...records.map((record) => csvColumns.map((column) => csvEscape(record[column])).join(",")),
  ].join("\n");
  await fs.writeFile(path.join(dataDir, "abstracts.csv"), `${csv}\n`);
  await fs.writeFile(path.join(dataDir, "abstracts.md"), records.map(markdownFor).join("\n---\n\n"));

  for (const record of records) {
    const prefix = `${String(record.index).padStart(3, "0")}-${slugify(record.session_code || record.title)}`;
    await fs.writeFile(path.join(jsonDir, `${prefix}.json`), JSON.stringify(record, null, 2));
    await fs.writeFile(path.join(mdDir, `${prefix}.md`), markdownFor(record));
  }

  console.log(JSON.stringify({ count: records.length, hits: first.body.hits, output: dataDir }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
