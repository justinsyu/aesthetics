#!/usr/bin/env python3
import html
import json
import textwrap
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "ai_sessions_curated.json"
HTML_PATH = ROOT / "ispor_2026_ai_guide.html"
BG_PATH = ROOT / "tan_slide_background.png"

THEME_COLORS = {
    "Evidence synthesis": "lime",
    "Modeling and analytics": "blue",
    "HTA, regulatory, and submissions": "orange",
    "RWE and unstructured data": "pink",
    "Skills and workforce": "gray",
    "AI methods in HEOR": "red",
}

SHORT_TITLES = {
    "Applied Generative AI for HEOR: Introduction": "Applied GenAI for HEOR: intro",
    "Prompt Engineering for HEOR: Practical Skills and Use Cases for HEOR Professionals": "Prompt engineering for HEOR",
    "Applied Generative AI for HEOR: Advanced Architectures": "Applied GenAI: advanced architectures",
    "Operationalizing Artificial Intelligence Guidance to Create Best in Class Abstraction and Curation Approaches": "Operationalizing AI guidance",
    "Is There a Consensus on the Framework for Evaluating Artificial Intelligence (AI)-Assisted Systematic Review Tools in HEOR?": "Evaluating AI-assisted SLR tools",
    "Next-Generation Methods: AI-Enabled Evidence Curation, Transparent Modeling, and HTA Readiness": "AI curation, modeling, HTA readiness",
    "Oncology Poster Tour": "Oncology posters: AI-assisted JCA SLR",
    "Towards More Trustworthy Models: ISPOR— SMDM Model Validation II Joint Task Force": "Trustworthy model validation task force",
    "Transforming HEOR With Artificial Intelligence and Real-World Data": "AI plus RWD symposium",
    "Living HTA in the Age of AI Innovation: Supporting HTA Decisions at the Speed of Evolving Evidence": "Living HTA in the age of AI",
    "The Enduring Challenge of Medical Device Identification in Real-World Data: Is Artificial Intelligence Abstraction Ready for Broad Use and Acceptance?": "AI abstraction for device RWD",
    "Use of Agentic AI to Create Health Economic Models in Both R and Excel": "Agentic AI for R and Excel models",
    "Behavioral Phenotyping for Value Assessment: Trajectory and AI Approaches to Rethink Medication Adherence Measurement": "AI phenotyping for adherence",
    "Minutes, Not Months: AI-Enabled Insights to Drive Evidence Strategy": "AI-enabled evidence strategy",
    "Methodology Research in HEOR Poster Tour": "Methodology posters: clinical AI and LLM cohorts",
    "Frontiers in Health Decision Modeling: A Dialogue With ISPOR and SMDM": "AI-enabled decision modeling dialogue",
    "Agentic AI in Evidence Submissions: Rigor, Trust, Traceability, & Compliance": "Agentic AI in evidence submissions",
    "Beyond Claims and EHRs: Social Media as Real-World Evidence to Uncover Patient Experiences and Unmet Needs": "Social listening with NLP and LLMs",
    "The NextGen of Clinical Trials: Patient-Driven or Tech-Driven?": "Patient-driven vs tech-driven trials",
    "New Frontiers in Large Language Models": "New frontiers in LLMs",
    "Novel Real-World Evidence Applications": "AI pharmacovigilance podium",
    "Live, Interactive Workshop of Generative AI for Real-World Market Access Challenges": "GenAI for market access challenges",
    "Rare Hope for Even Rarer Diseases: Innovation, Evidence, and Regulatory Perspectives": "AI evidence generation in rare disease",
    "Beyond the Bots: How AI-Enabled Literature Reviews Are Maturing, and What HEOR Needs Next": "How AI literature reviews are maturing",
    "Advancements in Real-World Evidence (RWE) to Accelerate Access in Rare Cancers: Challenges, Methods, and Decision Making": "RWE and AI for rare cancers",
    "Driving the Next Era of Evidence-Based Medicine Through AI, Diverse Data, and Collaboration": "AI, diverse data, collaboration",
    "The Evolving RWE Executive: Navigating AI Disruption and Changing Data Preferences": "RWE leadership amid AI disruption",
    "Tackle AI in HEOR With ISPOR Education": "ISPOR AI education",
    "The GenAI Paradox for Qualitative Evidence Summarization: Exploring Real-World Use Cases and Validation Frameworks for Understudied but Impactful Use Cases": "GenAI qualitative evidence frameworks",
    "ISPOR Good Practices Task Force on Generative Artificial Intelligence (GenAI) for Systematic Literature Reviews (SLRs): Preliminary Recommendations": "GenAI for SLRs task force",
    "Communicating Value in the Age of AI—Skills, Tools, and Confidence for HEOR Careers": "Communicating value in the age of AI",
    "The Future of RWE: Claims and EMR Were Just the Beginning": "Future RWE: AI-supported methods",
    "Real-World Evidence Poster Tour": "RWE posters: AI-enabled content analysis",
    "Advancing HEOR With Next-Generation AI: Multimodal LLMs, Digital Twins, and Reinforcement Learning for Personalized Therapy": "Multimodal LLMs, twins, RL",
    "Health Equity in Treatment, Costs, and Care Delivery": "ML eligibility and equity podium",
    "Productivity Gains From Generative AI Across the HEOR Workflow: Successful Case Studies": "GenAI productivity case studies",
    "Beyond Black Boxes: Case Studies of Transparent, Validated LLM Workflows for Accelerating Global HTA Submissions and Decisions": "Validated LLM workflows for HTA",
    "Amplifying Patient Voice: AI-Driven Narrative Analysis in Clinical Trials": "AI narrative analysis in trials",
    "Strategic Integration of Generative AI in Health Economic Modeling: Emerging Methods, Implementation, Evaluation, and HTA Implications": "GenAI in health economic modeling",
}


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def make_background() -> None:
    width, height = 1600, 900
    base = Image.new("RGB", (width, height), "#f6f1e8")
    overlays = [
        ((-210, -170, 700, 620), "#d7ff5f", 78),
        ((1040, -110, 1790, 520), "#b8d8ff", 68),
        ((910, 540, 1710, 1130), "#ffb86b", 48),
        ((-260, 610, 650, 1160), "#ffd3e0", 44),
    ]
    for box, color, alpha in overlays:
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        draw.ellipse(box, fill=(*Image.new("RGB", (1, 1), color).getpixel((0, 0)), alpha))
        layer = layer.filter(ImageFilter.GaussianBlur(70))
        base = Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
    noise = Image.new("RGBA", (width, height), (255, 250, 240, 0))
    draw = ImageDraw.Draw(noise)
    for y in range(0, height, 6):
        draw.line([(0, y), (width, y)], fill=(16, 18, 15, 3))
    base = Image.alpha_composite(base.convert("RGBA"), noise)
    base.save(BG_PATH)


def load_sessions() -> tuple[dict, list[dict]]:
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return payload["metadata"], payload["sessions"]


def short_title(session: dict) -> str:
    return SHORT_TITLES.get(session["title"], textwrap.shorten(session["title"], width=74, placeholder="..."))


def session_link(session: dict, label: str | None = None) -> str:
    label = label or session["title"]
    return f'<a href="{esc(session["url"])}">{esc(label)}</a>' if session.get("url") else esc(label)


def pill(label: str, color: str = "gray") -> str:
    return f'<span class="pill {color}">{esc(label)}</span>'


def speaker_line(session: dict, limit: int = 3) -> str:
    speakers = session.get("speakers") or []
    if not speakers:
        return ""
    names = [speaker["name"] for speaker in speakers[:limit] if speaker.get("name")]
    extra = len(speakers) - len(names)
    line = "; ".join(names)
    if extra > 0:
        line += f"; +{extra} more"
    return line


def event_card(session: dict, compact: bool = False) -> str:
    color = THEME_COLORS.get(session["theme"], "gray")
    related = ""
    if session["related_presentations"]:
        related = f'<div class="event-related">{len(session["related_presentations"])} related presentation{"s" if len(session["related_presentations"]) != 1 else ""}</div>'
    return f"""
      <div class="event-card {color} {'compact' if compact else ''}">
        <div class="event-top"><span>{esc(session['time'])}</span><span>{esc(session['session_type'])}</span></div>
        <h3>{session_link(session, short_title(session) if compact else session['title'])}</h3>
        <p>{esc(session['summary'])}</p>
        {related}
      </div>
    """


def calendar_slide(sessions_by_day: dict[str, list[dict]]) -> str:
    day_order = ["Sun May 17", "Mon May 18", "Tue May 19", "Wed May 20"]
    columns = []
    for day in day_order:
        items = sessions_by_day.get(day, [])
        compact_class = "dense" if len(items) > 12 else "normal"
        cards = []
        for session in items:
            color = THEME_COLORS.get(session["theme"], "gray")
            rel = f'<span class="cal-rel">+{len(session["related_presentations"])} podium/poster</span>' if session["related_presentations"] else ""
            cards.append(
                f"""
                <div class="cal-event {color}">
                  <div class="cal-time">{esc(session['time'])}</div>
                  <div class="cal-title">{session_link(session, short_title(session))}</div>
                  <div class="cal-meta">{esc(session['session_type'])}{rel}</div>
                </div>
                """
            )
        columns.append(
            f"""
            <div class="cal-day {compact_class}">
              <div class="cal-head"><b>{esc(day)}</b><span>{len(items)} sessions</span></div>
              <div class="cal-list">{''.join(cards)}</div>
            </div>
            """
        )
    return "".join(columns)


def day_focus_slide(day: str, sessions: list[dict], narrative: str, route_cards: list[tuple[str, str]]) -> str:
    route_html = "".join(
        f"""
        <div class="route-card">
          <h3>{esc(title)}</h3>
          <p>{esc(text)}</p>
        </div>
        """
        for title, text in route_cards
    )
    session_html = "".join(event_card(session, compact=True) for session in sessions)
    return f"""
      <div class="section-head tight">
        <span class="eyebrow">Day plan</span>
        <h2>{esc(day)}</h2>
        <p>{esc(narrative)}</p>
      </div>
      <div class="day-grid">
        <div class="day-events">{session_html}</div>
        <div class="routes">{route_html}</div>
      </div>
    """


def objective_matrix(sessions: list[dict]) -> str:
    picks = [
        (
            "Evidence synthesis and SLR automation",
            [
                "Is There a Consensus on the Framework for Evaluating Artificial Intelligence (AI)-Assisted Systematic Review Tools in HEOR?",
                "Beyond the Bots: How AI-Enabled Literature Reviews Are Maturing, and What HEOR Needs Next",
                "ISPOR Good Practices Task Force on Generative Artificial Intelligence (GenAI) for Systematic Literature Reviews (SLRs): Preliminary Recommendations",
            ],
        ),
        (
            "Model automation and reproducible analytics",
            [
                "Use of Agentic AI to Create Health Economic Models in Both R and Excel",
                "Agentic AI in Evidence Submissions: Rigor, Trust, Traceability, & Compliance",
                "Strategic Integration of Generative AI in Health Economic Modeling: Emerging Methods, Implementation, Evaluation, and HTA Implications",
            ],
        ),
        (
            "RWE, unstructured data, and patient voice",
            [
                "The Enduring Challenge of Medical Device Identification in Real-World Data: Is Artificial Intelligence Abstraction Ready for Broad Use and Acceptance?",
                "Beyond Claims and EHRs: Social Media as Real-World Evidence to Uncover Patient Experiences and Unmet Needs",
                "Amplifying Patient Voice: AI-Driven Narrative Analysis in Clinical Trials",
            ],
        ),
        (
            "HTA, regulatory, and submissions readiness",
            [
                "Operationalizing Artificial Intelligence Guidance to Create Best in Class Abstraction and Curation Approaches",
                "Living HTA in the Age of AI Innovation: Supporting HTA Decisions at the Speed of Evolving Evidence",
                "Beyond Black Boxes: Case Studies of Transparent, Validated LLM Workflows for Accelerating Global HTA Submissions and Decisions",
            ],
        ),
        (
            "Career, leadership, and operating model",
            [
                "The Evolving RWE Executive: Navigating AI Disruption and Changing Data Preferences",
                "Tackle AI in HEOR With ISPOR Education",
                "Communicating Value in the Age of AI—Skills, Tools, and Confidence for HEOR Careers",
            ],
        ),
    ]
    by_title = {session["title"]: session for session in sessions}
    rows = []
    for objective, titles in picks:
        links = []
        for title in titles:
            session = by_title[title]
            links.append(f"<li><b>{esc(session['date_short'].split()[0])} {esc(session['time'].split(' - ')[0])}</b> {session_link(session, short_title(session))}</li>")
        rows.append(
            f"""
            <div class="objective-row">
              <div class="objective-title">{esc(objective)}</div>
              <ul>{''.join(links)}</ul>
            </div>
            """
        )
    return "".join(rows)


def podium_poster_slide(sessions: list[dict]) -> str:
    rows = []
    for session in sessions:
        if not session["related_presentations"]:
            continue
        for related in session["related_presentations"]:
            color = THEME_COLORS.get(session["theme"], "gray")
            rows.append(
                f"""
                <div class="poster-row {color}">
                  <div class="poster-code">{esc(related['code'] or 'Item')}</div>
                  <div>
                    <div class="poster-title">{esc(textwrap.shorten(related['title'], width=118, placeholder='...'))}</div>
                    <div class="poster-meta">{esc(session['date_short'])} · {esc(session['time'])} · {session_link(session, short_title(session))}</div>
                  </div>
                </div>
                """
            )
    return "".join(rows)


def slide(number: int, body: str, extra_class: str = "") -> str:
    return f"""
    <article class="slide {extra_class}">
      <img class="slide-bg-img" src="{BG_PATH.name}" alt="" aria-hidden="true" />
      <div class="wrap">{body}</div>
      <div class="slide-num">{number:02d} / 09</div>
    </article>
    """


def build_html(metadata: dict, sessions: list[dict]) -> str:
    sessions_by_day = defaultdict(list)
    for session in sessions:
        sessions_by_day[session["date_short"]].append(session)
    theme_counts = Counter(session["theme"] for session in sessions)
    day_counts = Counter(session["date_short"] for session in sessions)

    max_day = max(day_counts.values())
    day_bars = "".join(
        f"""
        <div class="bar-row">
          <div class="bar-label">{esc(day)}</div>
          <div class="track"><span class="bar {['lime','blue','orange','pink'][i]}" style="width:{count / max_day * 100:.1f}%"></span></div>
          <div class="bar-value">{count}</div>
        </div>
        """
        for i, (day, count) in enumerate(day_counts.items())
    )
    max_theme = max(theme_counts.values())
    theme_cards = "".join(
        f"""
        <div class="theme-card {THEME_COLORS.get(theme, 'gray')}">
          <div class="theme-count">{count}</div>
          <div class="theme-name">{esc(theme)}</div>
          <div class="theme-bar"><span style="width:{count / max_theme * 100:.1f}%"></span></div>
        </div>
        """
        for theme, count in theme_counts.most_common()
    )

    sun = sessions_by_day["Sun May 17"]
    mon = sessions_by_day["Mon May 18"]
    tue = sessions_by_day["Tue May 19"]
    wed = sessions_by_day["Wed May 20"]

    slides = [
        slide(
            1,
            f"""
            <div class="hero">
              <span class="eyebrow">ISPOR 2026 · May 17-20</span>
              <h1>AI field guide for HEOR attendees</h1>
              <p class="hero-copy">A schedule-first guide to the AI sessions, conflicts, and poster or podium targets most relevant to evidence synthesis, modeling, RWE, HTA, patient voice, and career development.</p>
              <div class="metrics">
                <div class="metric"><div class="num">{metadata['session_count']}</div><div class="label">AI-related agenda items</div></div>
                <div class="metric"><div class="num">{metadata['ai_track_count']}</div><div class="label">Official AI-track sessions</div></div>
                <div class="metric"><div class="num">{metadata['related_presentation_count']}</div><div class="label">AI podium or poster targets</div></div>
                <div class="metric"><div class="num">4</div><div class="label">Conference days to plan</div></div>
              </div>
            </div>
            """,
            "slide-hero",
        ),
        slide(
            2,
            f"""
            <div class="section-head">
              <span class="eyebrow">At a glance</span>
              <h2>AI clusters around evidence synthesis and modeling</h2>
              <p>Monday is the densest day, but the program spans foundational short courses, practical workshops, policy and HTA sessions, RWE leadership, and final-day case studies.</p>
            </div>
            <div class="overview-grid">
              <div class="panel dark">
                <div class="panel-pad">
                  <h3>Sessions by day</h3>
                  <div class="bars">{day_bars}</div>
                </div>
              </div>
              <div class="theme-grid">{theme_cards}</div>
            </div>
            <div class="takeaway-strip">
              <div>{pill('Planning signal', 'lime')} 10:30 Monday, 4:45 Monday, 12:15 Tuesday, and 10:00 Wednesday are major conflict blocks.</div>
              <div>{pill('Data note', 'blue')} Public program data did not include room assignments at extraction time.</div>
            </div>
            """,
        ),
        slide(
            3,
            f"""
            <div class="section-head calendar-head">
              <span class="eyebrow">Calendar view</span>
              <h2>All AI-related sessions by conference day</h2>
            </div>
            <div class="calendar-grid">{calendar_slide(sessions_by_day)}</div>
            <div class="legend">
              {pill('Evidence synthesis', 'lime')}
              {pill('Modeling and analytics', 'blue')}
              {pill('HTA, regulatory, submissions', 'orange')}
              {pill('RWE and unstructured data', 'pink')}
              {pill('Skills and workforce', 'gray')}
            </div>
            """,
            "slide-calendar",
        ),
        slide(
            4,
            day_focus_slide(
                "Sunday foundation",
                sun,
                "Use Sunday to choose a hands-on skill base. The morning has two overlapping options; the afternoon extends the applied GenAI course into architectures.",
                [
                    ("If you are new to applied GenAI", "Take the introductory HEOR course, then continue into advanced architectures after lunch."),
                    ("If you already use chat tools", "Prompt engineering is the practical morning alternative, especially for HEOR communication and workflow design."),
                    ("Pre-conference setup", "Bring examples from SLR, model, or evidence-generation work so the short courses map to your own use cases."),
                ],
            ),
        ),
        slide(
            5,
            day_focus_slide(
                "Monday conflict map",
                mon,
                "Monday carries almost half of the AI-related agenda. Pick a primary lane before 10:30 AM, then decide whether 4:45 PM is a modeling, evidence-submission, social listening, LLM, or market-access block.",
                [
                    ("Evidence synthesis lane", "AI-assisted SLR tools at 10:30, JCA poster content at 11:30, then LLM podiums at 4:45."),
                    ("Modeling lane", "Operational guidance at 10:30, agentic model creation at 1:45, then submissions or decision-modeling sessions late afternoon."),
                    ("RWE and HTA lane", "Device abstraction and Living HTA at 12:15, AI evidence strategy at 3:15, social listening or market access at 4:45."),
                ],
            ),
        ),
        slide(
            6,
            day_focus_slide(
                "Tuesday operating model",
                tue,
                "Tuesday is the best day for governance, leadership, education, and framework building. It also includes a rare-disease AI session and late-day next-generation AI methods.",
                [
                    ("Morning decision", "Choose between mature AI-enabled reviews and rare-disease evidence generation; both are 10:30 AM."),
                    ("Midday leadership block", "RWE executives, diverse data, rare cancers, and ISPOR education cluster around 12:15-1:15."),
                    ("Afternoon framework block", "GenAI qualitative evidence, GenAI SLR recommendations, and the 4:45 next-generation AI workshop form a strong methods arc."),
                ],
            ),
        ),
        slide(
            7,
            day_focus_slide(
                "Wednesday case studies",
                wed,
                "Wednesday is compact but high value: start with GenAI productivity cases, then choose one of three simultaneous 10:00 AM sessions.",
                [
                    ("If you need examples", "The 8:00 AM productivity session is the clearest cross-workflow case-study slot."),
                    ("If you care about HTA trust", "Choose validated LLM workflows for global HTA submissions and decision-making."),
                    ("If you focus on patients or models", "Pick AI-driven patient narrative analysis or strategic GenAI integration in health economic modeling."),
                ],
            ),
        ),
        slide(
            8,
            f"""
            <div class="section-head">
              <span class="eyebrow">Choose by objective</span>
              <h2>Build a route around the job you need AI to do</h2>
              <p>Attendees will get more from the program by selecting a use-case lane, then adding one cross-cutting governance or validation session.</p>
            </div>
            <div class="objective-matrix">{objective_matrix(sessions)}</div>
            """,
        ),
        slide(
            9,
            f"""
            <div class="section-head poster-head">
              <span class="eyebrow">Podium and poster targets</span>
              <h2>Do not miss the embedded AI presentations</h2>
              <p>Several AI items sit inside broader research podium or poster-tour sessions; these are easy to overlook if you filter only for the AI track.</p>
            </div>
            <div class="poster-grid">{podium_poster_slide(sessions)}</div>
            """,
            "slide-posters",
        ),
    ]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ISPOR 2026 AI Field Guide</title>
  <style>
    :root {{
      --ink: #10120f;
      --muted: #5c6257;
      --paper: #f6f1e8;
      --paper-2: #ebe4d6;
      --card: #fffaf0;
      --line: #1b1f17;
      --lime: #d7ff5f;
      --orange: #ffb86b;
      --blue: #b8d8ff;
      --pink: #ffd3e0;
      --gray: #d6d0c2;
      --red: #ff8a76;
      --shadow: 0 18px 48px rgba(16, 18, 15, 0.08);
      --radius: 26px;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; background: var(--paper); color: var(--ink); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; scrollbar-width: none; }}
    html::-webkit-scrollbar, body::-webkit-scrollbar {{ display: none; }}
    body, *, *::before, *::after {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    a {{ color: inherit; text-decoration-thickness: 1px; text-underline-offset: 2px; }}
    .slide {{ min-height: 100vh; height: 100vh; width: 100vw; position: relative; overflow: hidden; display: flex; align-items: flex-start; padding: 58px 0 34px; break-after: page; page-break-after: always; background: var(--paper); }}
    .slide:last-child {{ break-after: auto; page-break-after: auto; }}
    .slide-bg-img {{ position: absolute; inset: 0; z-index: 0; width: 100%; height: 100%; object-fit: cover; pointer-events: none; user-select: none; }}
    .slide > *:not(.slide-bg-img) {{ position: relative; z-index: 1; }}
    .wrap {{ width: min(1390px, calc(100vw - 60px)); margin: 0 auto; }}
    h1, h2, h3, p {{ margin: 0; letter-spacing: 0; }}
    h1 {{ font-size: 84px; line-height: .95; font-weight: 560; max-width: 1260px; }}
    h2 {{ font-size: 54px; line-height: 1; font-weight: 560; }}
    h3 {{ font-size: 24px; line-height: 1.06; font-weight: 760; }}
    .eyebrow {{ display: inline-flex; align-items: center; border: 1.4px solid var(--line); padding: 8px 12px; border-radius: 999px; font-size: 14px; font-weight: 850; text-transform: uppercase; margin-bottom: 16px; background: var(--lime); }}
    .section-head {{ margin-bottom: 22px; }}
    .section-head p {{ color: var(--muted); font-size: 22px; line-height: 1.28; max-width: 1240px; margin-top: 12px; }}
    .section-head.tight {{ margin-bottom: 18px; }}
    .slide-num {{ position: absolute; right: 38px; bottom: 25px; font-size: 11px; text-transform: uppercase; color: rgba(16,18,15,.42); font-weight: 850; }}
    .hero {{ display: grid; gap: 28px; }}
    .slide-hero .eyebrow {{ justify-self: start; }}
    .slide-hero h1 {{ max-width: 1390px; }}
    .hero-copy {{ max-width: 1180px; color: var(--muted); font-size: 29px; line-height: 1.22; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 10px; }}
    .metric, .panel, .theme-card, .event-card, .route-card, .objective-row {{ border: 1.5px solid var(--line); background: rgba(255,250,240,.86); border-radius: var(--radius); box-shadow: var(--shadow); }}
    .metric {{ min-height: 148px; padding: 22px; }}
    .num {{ font-size: 56px; line-height: .95; font-weight: 620; }}
    .label {{ margin-top: 12px; color: var(--muted); font-size: 17px; line-height: 1.22; }}
    .slide-hero .metric .label {{ font-size: 20px; line-height: 1.16; }}
    .overview-grid {{ display: grid; grid-template-columns: .9fr 1.25fr; gap: 18px; align-items: stretch; }}
    .panel.dark {{ background: #11130f; color: var(--paper); }}
    .panel-pad {{ padding: 28px; }}
    .panel h3 {{ margin-bottom: 28px; }}
    .bars {{ display: grid; gap: 20px; }}
    .bar-row {{ display: grid; grid-template-columns: 120px 1fr 42px; align-items: center; gap: 16px; }}
    .bar-label {{ font-size: 18px; font-weight: 820; }}
    .track {{ height: 30px; border: 1px solid rgba(246,241,232,.36); border-radius: 999px; background: rgba(246,241,232,.08); overflow: hidden; }}
    .bar {{ display: block; height: 100%; border-radius: 999px; }}
    .bar-value {{ font-size: 20px; font-weight: 850; }}
    .lime {{ --accent: var(--lime); }}
    .blue {{ --accent: var(--blue); }}
    .orange {{ --accent: var(--orange); }}
    .pink {{ --accent: var(--pink); }}
    .gray {{ --accent: var(--gray); }}
    .red {{ --accent: var(--red); }}
    .bar.lime, .pill.lime, .theme-card.lime .theme-bar span, .poster-row.lime .poster-code {{ background: var(--lime); }}
    .bar.blue, .pill.blue, .theme-card.blue .theme-bar span, .poster-row.blue .poster-code {{ background: var(--blue); }}
    .bar.orange, .pill.orange, .theme-card.orange .theme-bar span, .poster-row.orange .poster-code {{ background: var(--orange); }}
    .bar.pink, .pill.pink, .theme-card.pink .theme-bar span, .poster-row.pink .poster-code {{ background: var(--pink); }}
    .bar.gray, .pill.gray, .theme-card.gray .theme-bar span, .poster-row.gray .poster-code {{ background: var(--gray); }}
    .bar.red, .pill.red, .theme-card.red .theme-bar span, .poster-row.red .poster-code {{ background: var(--red); }}
    .theme-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }}
    .theme-card {{ padding: 18px; min-height: 139px; }}
    .theme-count {{ font-size: 40px; line-height: .95; font-weight: 680; }}
    .theme-name {{ margin-top: 8px; color: var(--muted); font-size: 16px; line-height: 1.2; min-height: 38px; }}
    .theme-bar {{ height: 12px; border: 1px solid rgba(16,18,15,.28); border-radius: 999px; background: rgba(16,18,15,.08); margin-top: 12px; overflow: hidden; }}
    .theme-bar span {{ display: block; height: 100%; border-radius: 999px; }}
    .takeaway-strip {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 18px; }}
    .takeaway-strip > div {{ border: 1.3px solid var(--line); border-radius: 20px; padding: 15px 18px; background: rgba(255,250,240,.7); font-size: 17px; line-height: 1.28; }}
    .pill {{ display: inline-flex; align-items: center; border: 1.2px solid var(--line); border-radius: 999px; padding: 4px 8px; margin-right: 7px; font-size: 11px; line-height: 1; font-weight: 850; text-transform: uppercase; white-space: nowrap; }}
    .calendar-head {{ margin-bottom: 14px; }}
    .calendar-grid {{ display: grid; grid-template-columns: .74fr 2.05fr 1.55fr .76fr; gap: 9px; height: 650px; }}
    .cal-day {{ border: 1.4px solid var(--line); border-radius: 20px; overflow: hidden; background: rgba(255,250,240,.86); display: flex; flex-direction: column; }}
    .cal-head {{ display: flex; justify-content: space-between; gap: 8px; align-items: center; padding: 10px 11px; background: #11130f; color: var(--paper); }}
    .cal-head b {{ font-size: 15px; }}
    .cal-head span {{ font-size: 10px; color: rgba(246,241,232,.7); font-weight: 780; text-transform: uppercase; white-space: nowrap; }}
    .cal-list {{ display: grid; gap: 5px; padding: 8px; overflow: hidden; }}
    .cal-day.dense .cal-list {{ grid-template-columns: repeat(2, 1fr); gap: 4px; padding: 6px; }}
    .cal-event {{ border: 1px solid rgba(16,18,15,.58); border-left: 7px solid var(--accent); border-radius: 11px; padding: 5px 7px 5px 8px; background: rgba(255,250,240,.76); min-height: 0; }}
    .cal-day.dense .cal-event {{ padding: 3px 5px 3px 7px; border-radius: 8px; border-left-width: 6px; }}
    .cal-time {{ font-size: 9.5px; line-height: 1; color: var(--muted); font-weight: 850; }}
    .cal-title {{ margin-top: 2px; font-size: 11px; line-height: 1.05; font-weight: 780; }}
    .cal-day.dense .cal-title {{ font-size: 8.8px; line-height: 1.03; }}
    .cal-meta {{ margin-top: 2px; font-size: 8.6px; line-height: 1; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .cal-day.dense .cal-meta {{ font-size: 7.2px; }}
    .cal-rel {{ margin-left: 4px; color: var(--ink); font-weight: 820; }}
    .legend {{ display: flex; gap: 6px; align-items: center; margin-top: 12px; }}
    .day-grid {{ display: grid; grid-template-columns: 1.42fr .72fr; gap: 16px; align-items: start; }}
    .day-events {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }}
    .event-card {{ padding: 14px 15px; border-left: 8px solid var(--accent); min-height: 138px; }}
    .event-card.compact {{ min-height: 74px; padding: 8px 10px; border-radius: 16px; border-left-width: 7px; }}
    .event-top {{ display: flex; justify-content: space-between; gap: 8px; color: var(--muted); font-size: 10px; font-weight: 850; text-transform: uppercase; margin-bottom: 6px; }}
    .event-card h3 {{ font-size: 18px; line-height: 1.08; }}
    .event-card.compact h3 {{ font-size: 11.5px; line-height: 1.05; }}
    .event-card p {{ margin-top: 8px; font-size: 13.5px; line-height: 1.26; color: var(--muted); }}
    .event-card.compact p {{ display: none; }}
    .event-related {{ margin-top: 6px; color: var(--ink); font-size: 11px; font-weight: 820; }}
    .routes {{ display: grid; gap: 12px; }}
    .route-card {{ padding: 18px; background: #11130f; color: var(--paper); min-height: 134px; }}
    .route-card h3 {{ font-size: 22px; }}
    .route-card p {{ margin-top: 10px; color: rgba(246,241,232,.72); font-size: 16px; line-height: 1.3; }}
    .objective-matrix {{ display: grid; gap: 12px; }}
    .objective-row {{ display: grid; grid-template-columns: 350px 1fr; gap: 18px; align-items: start; padding: 16px 18px; border-left: 10px solid var(--lime); }}
    .objective-title {{ font-size: 21px; line-height: 1.08; font-weight: 820; }}
    .objective-row ul {{ margin: 0; padding-left: 20px; display: grid; gap: 7px; }}
    .objective-row li {{ font-size: 17px; line-height: 1.22; color: var(--muted); }}
    .objective-row li b {{ color: var(--ink); }}
    .poster-head {{ margin-bottom: 15px; }}
    .slide-posters .wrap {{ width: min(1480px, calc(100vw - 60px)); }}
    .slide-posters .section-head p {{ max-width: 1480px; white-space: nowrap; }}
    .poster-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px 12px; }}
    .poster-row {{ display: grid; grid-template-columns: 58px 1fr; gap: 10px; align-items: start; border: 1.2px solid var(--line); border-radius: 15px; padding: 8px 10px; background: rgba(255,250,240,.82); min-height: 54px; }}
    .poster-code {{ border: 1.2px solid var(--line); border-radius: 999px; padding: 5px 6px; text-align: center; font-size: 12px; line-height: 1; font-weight: 850; }}
    .poster-title {{ font-size: 12.5px; line-height: 1.08; font-weight: 760; }}
    .poster-meta {{ margin-top: 3px; color: var(--muted); font-size: 10.5px; line-height: 1.05; }}
    @page {{ size: 1600px 900px; margin: 0; }}
    @media print {{
      html, body {{ width: 1600px; height: 900px; }}
      .slide {{ width: 1600px; height: 900px; min-height: 900px; padding: 58px 0 34px; }}
      .wrap {{ width: 1390px; }}
      .slide-posters .wrap {{ width: 1480px; }}
      .metric, .panel, .theme-card, .event-card, .route-card, .objective-row {{ box-shadow: none; }}
    }}
    @media screen and (max-width: 900px) {{
      .wrap {{ width: min(1390px, calc(100vw - 32px)); }}
    }}
  </style>
</head>
<body>
{''.join(slides)}
</body>
</html>
"""


def main() -> None:
    make_background()
    metadata, sessions = load_sessions()
    HTML_PATH.write_text(build_html(metadata, sessions), encoding="utf-8")
    print(HTML_PATH)


if __name__ == "__main__":
    main()
