const metadata = {
    title:
      "Health care costs associated with disease progression of untreated chronic hepatitis C in the United States",
    shortTitle: "Untreated HCV Cost Progression",
    authors: [
      "Suk-Chan Jang",
      "Ji Haeng Heo",
      "Shao-Hsuan Chang",
      "Mahek Garg",
      "Ikenna Unigwe",
      "Haesuk Park",
    ],
    journal: "Journal of Managed Care & Specialty Pharmacy",
    citation: "J Manag Care Spec Pharm. 2026;32(6):643-650.",
    articleType: "Research brief",
    source: "Local PDF sample",
    pdfUrl: "/sample-paper.pdf",
  background:
    "Despite effective direct-acting antiviral therapies, many US patients with chronic hepatitis C remain untreated, creating clinical and economic burden as disease progresses.",
  objective:
    "Estimate health care costs related to disease progression among untreated, newly diagnosed adults with chronic hepatitis C in the United States.",
  keyClaim:
    "Untreated chronic hepatitis C was associated with sharply escalating per-patient per-month costs as liver disease advanced, supporting early screening and treatment to prevent high-cost progression.",
  note:
    "Extracted from the local 8-page PDF. Supplementary materials are referenced by the article but are not included in the sample PDF.",
};

const metrics = [
    {
      id: "cohort",
      label: "Untreated cohort",
      value: "36,923",
      text: "Newly diagnosed adults with chronic hepatitis C in claims data",
    },
    {
      id: "chc-cost",
      label: "CHC adjusted PPPM",
      value: "$4,483",
      text: "All-cause per-patient per-month cost at chronic HCV stage",
    },
    {
      id: "lt-cost",
      label: "Transplant adjusted PPPM",
      value: "$27,836",
      text: "All-cause per-patient per-month cost at liver transplantation",
    },
    {
      id: "liver-share",
      label: "Liver-related share",
      value: "57.4%",
      text: "Liver-related proportion of all-cause costs at transplantation",
    },
];

const sections = [
    {
      id: "plain-language-summary",
      label: "Plain Language Summary",
      page: "643",
      status: "Done",
      focus: "Why this matters",
      text:
        "Costs increased rapidly with liver disease progression among untreated hepatitis C patients, from $4,483 PPPM for chronic infection to $27,836 PPPM for liver transplantation.",
    },
    {
      id: "introduction",
      label: "Introduction",
      page: "644",
      status: "Done",
      focus: "Context and study objective",
      text:
        "The paper frames untreated chronic hepatitis C as a continuing US public health and economic problem despite DAA availability, and argues that contemporary stage-specific untreated-cost inputs are needed for policy and economic models.",
    },
    {
      id: "methods",
      label: "Methods",
      page: "644",
      status: "Done",
      focus: "Claims cohort and cost models",
      text:
        "Researchers followed untreated, treatment-naive adults with chronic hepatitis C in claims data and attributed utilization and costs to disease-stage periods until progression, disenrollment, or study end.",
    },
    {
      id: "results",
      label: "Results",
      page: "646",
      status: "In progress",
      focus: "Stage-specific PPPM cost escalation",
      text:
        "Adjusted costs rose monotonically with disease severity, and liver-related costs became a larger share of total costs at advanced stages.",
    },
    {
      id: "discussion",
      label: "Discussion",
      page: "648",
      status: "Pending",
      focus: "Policy interpretation",
      text:
        "The authors position the findings as updated real-world inputs for economic evaluations and policy decisions, arguing that older cost estimates may misstate the value of screening and treatment expansion.",
    },
    {
      id: "limitations",
      label: "Limitations",
      page: "649",
      status: "Pending",
      focus: "Claims-data caveats",
      text:
        "The authors note claims-based staging uncertainty, possible untreated-status misclassification, limited generalizability beyond commercially insured populations, variable follow-up, and changes in practice patterns during 2013-2023.",
    },
];

const keyTerms = [
    {
      id: "daa",
      label: "Direct-acting antiviral therapy",
      count: 11,
      text:
        "Curative hepatitis C treatment class discussed as central to preventing progression.",
    },
    {
      id: "pppm",
      label: "PPPM",
      count: 26,
      text:
        "Per-patient per-month cost, calculated by dividing costs accrued during a stage-specific observation period by months in that period.",
    },
    {
      id: "cc",
      label: "Compensated cirrhosis",
      count: 17,
      text:
        "Advanced liver disease stage after chronic hepatitis C and before decompensated cirrhosis in the study hierarchy.",
    },
    {
      id: "dc",
      label: "Decompensated cirrhosis",
      count: 15,
      text:
        "A more severe cirrhosis stage associated with substantially higher adjusted PPPM costs than compensated cirrhosis.",
    },
    {
      id: "hcc",
      label: "Hepatocellular carcinoma",
      count: 13,
      text:
        "Liver cancer stage abbreviated HCC; adjusted all-cause PPPM costs were $19,021 in the study.",
    },
    {
      id: "two-part",
      label: "Two-part model",
      count: 5,
      text:
        "Statistical approach used for liver-related costs: first estimating whether any cost occurred, then estimating positive costs.",
    },
];

const annotations = [
    {
      id: "ann-claim-1",
      type: "claim",
      sectionId: "plain-language-summary",
      page: "643",
      text:
        "Early testing and treatment can prevent progression and reduce costs.",
    },
    {
      id: "ann-evidence-1",
      type: "evidence",
      sectionId: "introduction",
      page: "644",
      text:
        "The introduction states that nearly two-thirds of US patients with chronic hepatitis C remained untreated through 2022.",
    },
    {
      id: "ann-method-1",
      type: "method",
      sectionId: "methods",
      page: "645",
      text:
        "Patients needed at least 1 inpatient or 2 outpatient chronic hepatitis C claims and continuous enrollment for at least 1 year before the index date.",
    },
    {
      id: "ann-method-2",
      type: "method",
      sectionId: "methods",
      page: "645",
      text:
        "All-cause costs were modeled with generalized linear models using a gamma distribution; liver-related costs used a two-part model for excess zero costs.",
    },
    {
      id: "ann-method-3",
      type: "method",
      sectionId: "methods",
      page: "645",
      text:
        "Costs were calculated per patient per month and adjusted to 2023 US dollars using the medical-care component of CPI-U.",
    },
    {
      id: "ann-evidence-2",
      type: "evidence",
      sectionId: "results",
      page: "647",
      text:
        "Adjusted all-cause PPPM costs were $4,483 for chronic hepatitis C, $6,240 for compensated cirrhosis, $14,166 for decompensated cirrhosis, $19,021 for hepatocellular carcinoma, and $27,836 for liver transplantation.",
    },
    {
      id: "ann-evidence-3",
      type: "evidence",
      sectionId: "results",
      page: "647",
      text:
        "Liver-related PPPM costs were $70, $309, $2,001, $5,791, and $15,986 across the same stages.",
    },
    {
      id: "ann-claim-2",
      type: "claim",
      sectionId: "discussion",
      page: "648",
      text:
        "Granular separation of decompensated cirrhosis, hepatocellular carcinoma, and liver transplantation revealed cost differences that broader end-stage liver disease categories can obscure.",
    },
    {
      id: "ann-limitation-1",
      type: "limitation",
      sectionId: "limitations",
      page: "649",
      text:
        "The claims data did not include laboratory values to validate disease staging.",
    },
    {
      id: "ann-limitation-2",
      type: "limitation",
      sectionId: "limitations",
      page: "649",
      text:
        "Some treated patients may have been misclassified as untreated if DAA treatment occurred outside captured claims channels.",
    },
    {
      id: "ann-limitation-3",
      type: "limitation",
      sectionId: "limitations",
      page: "649",
      text:
        "Commercial-insurance data limit generalizability to uninsured and other underrepresented populations.",
    },
    {
      id: "ann-question-1",
      type: "question",
      sectionId: "introduction",
      page: "644",
      text:
        "How would cost estimates differ in Medicaid, uninsured, correctional, or safety-net populations not fully represented by commercial claims?",
    },
    {
      id: "ann-question-2",
      type: "question",
      sectionId: "discussion",
      page: "648",
      text:
        "Which policy models currently rely on pre-DAA or early-DAA cost inputs, and how sensitive are their conclusions to these updated stage-specific costs?",
    },
];

const figures = [
    {
      id: "table-1",
      label: "Table 1",
      title:
        "Characteristics of patients with hepatitis C stratified by progression to each liver disease stage",
      page: "646",
      text:
        "Baseline demographics, comorbidities, insurance type, region, index year, and follow-up time varied significantly across disease stages.",
    },
    {
      id: "figure-1",
      label: "Figure 1",
      title: "Adjusted PPPM health care costs by disease stage",
      page: "647",
      text:
        "All-cause, liver-related, non-liver-related medical, and pharmacy costs increased with disease progression; total adjusted costs were highest at liver transplantation.",
    },
    {
      id: "supplement-3",
      label: "Supplementary Table 3",
      title: "Mean unadjusted PPPM all-cause costs",
      page: "Supplement",
      text:
        "The article reports unadjusted all-cause PPPM costs of $4,403, $6,106, $15,813, $17,290, and $20,009 across stages.",
    },
];

const readingPlan = [
    {
      id: "triage",
      label: "Fast triage",
      text: "Read title, summary, Figure 1, and limitations before committing to close reading.",
      done: true,
    },
    {
      id: "methods-pass",
      label: "Methods pass",
      text: "Check cohort definition, untreated classification, stage assignment, and cost modeling.",
      done: true,
    },
    {
      id: "results-pass",
      label: "Results pass",
      text: "Compare adjusted all-cause and liver-related PPPM costs across the five disease stages.",
      done: false,
    },
    {
      id: "critique",
      label: "Critique pass",
      text: "Pressure-test claims-data limitations and external validity beyond commercially insured patients.",
      done: false,
    },
    {
      id: "one-week-memory",
      label: "One-week memory",
      text: "Save the policy-relevant takeaway in one sentence and export the evidence map.",
      done: false,
    },
];

const recallPrompts = [
    {
      id: "recall-1",
      label: "Main finding",
      type: "claim",
      text:
        "What was the study's main policy-relevant cost finding across hepatitis C disease stages?",
      answer:
        "Adjusted all-cause PPPM costs rose from $4,483 at chronic hepatitis C to $27,836 at liver transplantation, with liver-related costs taking up a larger share as disease advanced.",
    },
    {
      id: "recall-2",
      label: "Untreated definition",
      type: "method",
      text: "How did the authors define untreated status using claims data?",
      answer:
        "Untreated status required absence of DAA, interferon, or pegylated-interferon prescriptions during the year before index and throughout follow-up after chronic hepatitis C diagnosis.",
    },
    {
      id: "recall-3",
      label: "Cost model",
      type: "method",
      text: "Why did the authors use a two-part model for liver-related costs?",
      answer:
        "They used it to account for excess zero costs: first modeling whether any liver-related cost occurred, then modeling adjusted positive costs.",
    },
    {
      id: "recall-4",
      label: "Generalizability",
      type: "limitation",
      text:
        "What is one reason the results may not generalize to all people with chronic hepatitis C?",
      answer:
        "The data came from commercially insured and Medicare Supplemental claims, so uninsured and other underrepresented populations may have different access, disease progression, and cost patterns.",
    },
    {
      id: "recall-5",
      label: "Disease stages",
      type: "evidence",
      text: "Which disease-stage categories did the study use?",
      answer:
        "Chronic hepatitis C, compensated cirrhosis, decompensated cirrhosis, hepatocellular carcinoma, and liver transplantation.",
    },
];

export const samplePaper = { metadata, metrics, sections, keyTerms, annotations, figures, readingPlan, recallPrompts };

export default samplePaper;
