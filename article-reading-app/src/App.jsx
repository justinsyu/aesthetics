import {
  Bookmark,
  Brain,
  Check,
  ChevronDown,
  Copy,
  Download,
  ExternalLink,
  FileText,
  Highlighter,
  Library,
  ListFilter,
  MoreHorizontal,
  Search,
} from "lucide-react";
import React from "react";
import { useMemo, useState } from "react";
import { samplePaper } from "./data/samplePaper";

const navItems = ["Reader", "Evidence Map", "Recall", "Export"];

const roleMeta = {
  claim: { label: "Claim", color: "teal" },
  evidence: { label: "Evidence", color: "blue" },
  method: { label: "Method", color: "purple" },
  limitation: { label: "Limitation", color: "pink" },
  question: { label: "Question", color: "amber" },
};

function normalize(text) {
  return text.toLowerCase().trim();
}

function App() {
  const [activeView, setActiveView] = useState("Reader");
  const [selectedSection, setSelectedSection] = useState("results");
  const [selectedRoles, setSelectedRoles] = useState(() => new Set(Object.keys(roleMeta)));
  const [query, setQuery] = useState("");
  const [readingPlan, setReadingPlan] = useState(samplePaper.readingPlan);
  const [openAnswers, setOpenAnswers] = useState(() => new Set(["recall-1"]));
  const [copied, setCopied] = useState(false);

  const selectedSectionData = samplePaper.sections.find((section) => section.id === selectedSection);

  const filteredAnnotations = useMemo(() => {
    const q = normalize(query);
    return samplePaper.annotations.filter((annotation) => {
      const sectionMatch = activeView === "Evidence Map" || annotation.sectionId === selectedSection;
      const roleMatch = selectedRoles.has(annotation.type);
      const queryMatch =
        !q ||
        normalize(annotation.text).includes(q) ||
        normalize(roleMeta[annotation.type].label).includes(q) ||
        normalize(annotation.page).includes(q);
      return sectionMatch && roleMatch && queryMatch;
    });
  }, [activeView, query, selectedRoles, selectedSection]);

  const exportText = useMemo(() => {
    const evidenceLines = samplePaper.annotations
      .map((annotation) => {
        const section = samplePaper.sections.find((item) => item.id === annotation.sectionId);
        return `- [${roleMeta[annotation.type].label}] ${section?.label ?? "Section"} p.${annotation.page}: ${annotation.text}`;
      })
      .join("\n");

    return `${samplePaper.metadata.title}
${samplePaper.metadata.citation}

Main claim:
${samplePaper.metadata.keyClaim}

Evidence map:
${evidenceLines}

Recall focus:
${samplePaper.recallPrompts.map((prompt) => `- ${prompt.text}`).join("\n")}`;
  }, []);

  function toggleRole(role) {
    setSelectedRoles((current) => {
      const next = new Set(current);
      if (next.has(role)) {
        next.delete(role);
      } else {
        next.add(role);
      }
      return next;
    });
  }

  function togglePlanItem(id) {
    setReadingPlan((items) =>
      items.map((item) => (item.id === id ? { ...item, done: !item.done } : item)),
    );
  }

  function toggleAnswer(id) {
    setOpenAnswers((current) => {
      const next = new Set(current);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  async function copyExport() {
    try {
      await navigator.clipboard.writeText(exportText);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <a className="brand" href="#top" aria-label="PaperPath home">
          PaperPath
        </a>
        <nav aria-label="Primary navigation">
          {navItems.map((item) => (
            <button
              key={item}
              className="nav-link"
              type="button"
              aria-current={activeView === item ? "page" : undefined}
              onClick={() => setActiveView(item)}
            >
              {item}
            </button>
          ))}
        </nav>
        <div className="header-tools">
          <label className="search-control">
            <Search size={16} aria-hidden="true" />
            <input
              type="search"
              value={query}
              placeholder="Search"
              aria-label="Search annotations"
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>
          <button className="icon-button" type="button" aria-label="Library">
            <Library size={17} aria-hidden="true" />
          </button>
          <button className="avatar-button" type="button" aria-label="Account menu">
            JS
            <ChevronDown size={14} aria-hidden="true" />
          </button>
        </div>
      </header>

      <main className="dashboard-shell" id="top">
        <section className="masthead" aria-labelledby="paper-title">
          <div>
            <h1 id="paper-title">{samplePaper.metadata.shortTitle}</h1>
            <p>
              {samplePaper.metadata.authors.slice(0, 3).join(", ")} et al. /{" "}
              {samplePaper.metadata.citation} / {samplePaper.metadata.articleType}
            </p>
          </div>
          <div className="masthead-actions" aria-label="Document actions">
            <button className="text-button" type="button">
              <Bookmark size={16} aria-hidden="true" />
              Save
            </button>
            <button className="text-button" type="button" onClick={() => setActiveView("Export")}>
              <Copy size={16} aria-hidden="true" />
              Brief
            </button>
            <a className="text-button" href={samplePaper.metadata.pdfUrl} target="_blank">
              <Download size={16} aria-hidden="true" />
              PDF
            </a>
          </div>
        </section>

        <section className="kpi-grid" aria-label="Key paper metrics">
          {samplePaper.metrics.map((metric) => (
            <button
              className="kpi"
              key={metric.id}
              type="button"
              onClick={() => setQuery(metric.value)}
              title={metric.text}
            >
              <span className="dot cyan" aria-hidden="true" />
              <span className="label">{metric.label}</span>
              <span className="num">{metric.value}</span>
              <span className="detail">{metric.text}</span>
            </button>
          ))}
        </section>

        <RoleToolbar selectedRoles={selectedRoles} onToggle={toggleRole} />

        {activeView === "Reader" && (
          <ReaderView
            selectedSection={selectedSection}
            selectedSectionData={selectedSectionData}
            setSelectedSection={setSelectedSection}
            annotations={filteredAnnotations}
            readingPlan={readingPlan}
            togglePlanItem={togglePlanItem}
          />
        )}

        {activeView === "Evidence Map" && (
          <EvidenceMap annotations={filteredAnnotations} setSelectedSection={setSelectedSection} />
        )}

        {activeView === "Recall" && (
          <RecallView openAnswers={openAnswers} toggleAnswer={toggleAnswer} />
        )}

        {activeView === "Export" && (
          <ExportView exportText={exportText} onCopy={copyExport} copied={copied} />
        )}
      </main>

      <footer className="site-footer">
        <p>{samplePaper.metadata.note}</p>
      </footer>
    </div>
  );
}

function RoleToolbar({ selectedRoles, onToggle }) {
  return (
    <section className="role-toolbar" aria-label="Highlight role filters">
      <div className="toolbar-title">
        <Highlighter size={16} aria-hidden="true" />
        <span>Highlight roles</span>
      </div>
      <div className="role-buttons">
        {Object.entries(roleMeta).map(([role, meta]) => (
          <button
            key={role}
            className={`role-filter ${selectedRoles.has(role) ? "is-active" : ""}`}
            type="button"
            aria-pressed={selectedRoles.has(role)}
            onClick={() => onToggle(role)}
          >
            <span className={`dot ${meta.color}`} aria-hidden="true" />
            {meta.label}
          </button>
        ))}
      </div>
    </section>
  );
}

function ReaderView({
  selectedSection,
  selectedSectionData,
  setSelectedSection,
  annotations,
  readingPlan,
  togglePlanItem,
}) {
  return (
    <>
      <section className="reader-grid" aria-label="Reader workspace">
        <aside className="panel outline-panel">
          <PanelHeader title="Article outline" actionIcon={<ListFilter size={16} />} />
          <ol className="outline-list">
            {samplePaper.sections.map((section) => (
              <li key={section.id}>
                <button
                  type="button"
                  className={selectedSection === section.id ? "is-selected" : ""}
                  onClick={() => setSelectedSection(section.id)}
                >
                  <span>{section.label}</span>
                  <span>p. {section.page}</span>
                </button>
              </li>
            ))}
          </ol>
          <div className="legend-block">
            <div className="legend-heading">
              <span>Role count</span>
              <button type="button">Edit</button>
            </div>
            {Object.entries(roleMeta).map(([role, meta]) => {
              const count = samplePaper.annotations.filter((annotation) => annotation.type === role).length;
              return (
                <div className="legend-row" key={role}>
                  <span className={`dot ${meta.color}`} aria-hidden="true" />
                  <span>{meta.label}</span>
                  <strong>{count}</strong>
                </div>
              );
            })}
          </div>
        </aside>

        <article className="panel reading-panel">
          <div className="reader-bar">
            <span>{selectedSectionData?.label}</span>
            <span>{annotations.length} matched annotations</span>
            <button type="button" aria-label="More reading actions">
              <MoreHorizontal size={18} aria-hidden="true" />
            </button>
          </div>
          <div className="paper-page">
            <p className="section-gist">{selectedSectionData?.text}</p>
            <div className="annotation-stack">
              {annotations.length === 0 ? (
                <p className="empty-state">No annotations match the current role filters or search.</p>
              ) : (
                annotations.map((annotation) => <AnnotationLine annotation={annotation} key={annotation.id} />)
              )}
            </div>
          </div>
        </article>

        <aside className="panel insight-panel">
          <div className="tabs">
            <button className="is-active" type="button">
              Insights
            </button>
            <button type="button">Notes (3)</button>
          </div>
          <div className="key-term-list">
            <div className="mini-heading">
              <span>Key terms</span>
              <button type="button">View all</button>
            </div>
            {samplePaper.keyTerms.map((term) => (
              <details key={term.id}>
                <summary>
                  <span>{term.label}</span>
                  <strong>{term.count}</strong>
                </summary>
                <p>{term.text}</p>
              </details>
            ))}
          </div>
        </aside>
      </section>

      <section className="lower-grid">
        <FigureNavigator />
        <ReadingPlan items={readingPlan} onToggle={togglePlanItem} />
      </section>
    </>
  );
}

function PanelHeader({ title, actionIcon }) {
  return (
    <div className="panel-header">
      <h2>{title}</h2>
      <button type="button" aria-label={`${title} actions`}>
        {actionIcon}
      </button>
    </div>
  );
}

function AnnotationLine({ annotation }) {
  const meta = roleMeta[annotation.type];
  const section = samplePaper.sections.find((item) => item.id === annotation.sectionId);

  return (
    <article className={`annotation-line ${annotation.type}`}>
      <div>
        <span className={`highlight ${annotation.type}`}>{annotation.text}</span>
        <small>
          {section?.label} / p. {annotation.page}
        </small>
      </div>
      <span className={`role-chip ${annotation.type}`}>{meta.label}</span>
    </article>
  );
}

function FigureNavigator() {
  return (
    <section className="panel figure-panel">
      <div className="panel-header">
        <h2>Figure / table navigator</h2>
        <button type="button">View all</button>
      </div>
      <div className="figure-list">
        {samplePaper.figures.map((figure, index) => (
          <article key={figure.id} className="figure-card">
            <div className="figure-thumb" aria-hidden="true">
              <span className="axis-line" />
              <span className="bar-one" style={{ "--bar-h": `${38 + index * 15}%` }} />
              <span className="bar-two" style={{ "--bar-h": `${58 + index * 8}%` }} />
              <span className="bar-three" style={{ "--bar-h": `${72 - index * 5}%` }} />
            </div>
            <strong>{figure.label}</strong>
            <span>{figure.title}</span>
            <small>p. {figure.page}</small>
          </article>
        ))}
      </div>
    </section>
  );
}

function ReadingPlan({ items, onToggle }) {
  return (
    <section className="panel plan-panel">
      <div className="panel-header">
        <h2>Reading plan</h2>
        <button type="button">Manage</button>
      </div>
      <div className="plan-table" role="table" aria-label="Reading plan">
        <div className="plan-row plan-head" role="row">
          <span>Done</span>
          <span>Section</span>
          <span>Focus</span>
          <span>Status</span>
        </div>
        {items.map((item) => (
          <button className="plan-row" type="button" key={item.id} onClick={() => onToggle(item.id)}>
            <span className={`check-box ${item.done ? "is-checked" : ""}`}>
              {item.done ? <Check size={13} aria-hidden="true" /> : null}
            </span>
            <span>{item.label}</span>
            <span>{item.text}</span>
            <strong>{item.done ? "Done" : "Pending"}</strong>
          </button>
        ))}
      </div>
    </section>
  );
}

function EvidenceMap({ annotations, setSelectedSection }) {
  return (
    <section className="section-block">
      <h2>
        <span className="dot cyan" aria-hidden="true" />
        Evidence map
      </h2>
      <div className="evidence-table" role="table" aria-label="Evidence annotations">
        <div className="evidence-row evidence-head" role="row">
          <span>Role</span>
          <span>Section</span>
          <span>Page</span>
          <span>Annotation</span>
        </div>
        {annotations.map((annotation) => {
          const section = samplePaper.sections.find((item) => item.id === annotation.sectionId);
          return (
            <button
              className="evidence-row"
              key={annotation.id}
              type="button"
              onClick={() => setSelectedSection(annotation.sectionId)}
            >
              <span className={`role-chip ${annotation.type}`}>{roleMeta[annotation.type].label}</span>
              <span>{section?.label}</span>
              <span>{annotation.page}</span>
              <span>{annotation.text}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function RecallView({ openAnswers, toggleAnswer }) {
  return (
    <section className="recall-grid">
      <div className="section-block">
        <h2>
          <span className="dot purple" aria-hidden="true" />
          Active recall
        </h2>
        <div className="recall-list">
          {samplePaper.recallPrompts.map((prompt, index) => (
            <article className="recall-card" key={prompt.id}>
              <div>
                <span className={`role-chip ${prompt.type}`}>{roleMeta[prompt.type].label}</span>
                <h3>
                  {index + 1}. {prompt.text}
                </h3>
              </div>
              <button type="button" onClick={() => toggleAnswer(prompt.id)}>
                <Brain size={16} aria-hidden="true" />
                {openAnswers.has(prompt.id) ? "Hide answer" : "Reveal answer"}
              </button>
              {openAnswers.has(prompt.id) && <p>{prompt.answer}</p>}
            </article>
          ))}
        </div>
      </div>
      <aside className="panel study-panel">
        <h2>One-week memory</h2>
        <p>{samplePaper.metadata.keyClaim}</p>
        <div className="memory-line">
          <span>Fast triage</span>
          <strong>Title / summary / Figure 1 / limitations</strong>
        </div>
        <div className="memory-line">
          <span>Close-read trigger</span>
          <strong>Cost-model assumptions or policy reuse</strong>
        </div>
      </aside>
    </section>
  );
}

function ExportView({ exportText, onCopy, copied }) {
  return (
    <section className="export-grid">
      <article className="section-block export-panel">
        <h2>
          <span className="dot green" aria-hidden="true" />
          Evidence brief
        </h2>
        <pre>{exportText}</pre>
      </article>
      <aside className="panel export-actions">
        <h2>Export</h2>
        <button className="primary-action" type="button" onClick={onCopy}>
          <Copy size={17} aria-hidden="true" />
          {copied ? "Copied" : "Copy brief"}
        </button>
        <a className="secondary-action" href={samplePaper.metadata.pdfUrl} target="_blank">
          <FileText size={17} aria-hidden="true" />
          Open sample PDF
          <ExternalLink size={14} aria-hidden="true" />
        </a>
        <p>
          Export keeps every AI-style summary tethered to section, role, and page metadata so
          readers can audit the source quickly.
        </p>
      </aside>
    </section>
  );
}

export default App;
