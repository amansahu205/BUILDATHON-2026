import type { VerdictCase } from "./types";

const cases: VerdictCase[] = [
  {
    id: "lyman_v_cctd",
    case_name: "Lyman v. Capital City Transit District",
    case_type: "Personal Injury — Transit Negligence",
    opposing_party: "Capital City Transit District",
    deposition_date: "2026-03-15",
    witness_name: "Mark Hensley; Route Supervisor, CCTD",
    witness_role:
      "Corporate representative and route supervisor responsible for driver scheduling and safety compliance",
    extracted_facts:
      "On January 12, 2026, CCTD Bus #4417 ran a red light at the intersection of 5th Ave and Main St, striking plaintiff Sarah Lyman in a marked crosswalk. Driver had been on shift for 14.5 hours. CCTD policy caps shifts at 10 hours. Internal memo dated December 2025 flagged chronic understaffing on Route 9. Three prior incidents on same route in preceding 6 months. Dashcam footage shows driver looking at personal phone 3 seconds before impact.",
    prior_statements:
      "Hensley stated in initial police report: 'All drivers were within shift limits that week.' Hensley told CCTD internal review board: 'We had adequate staffing on Route 9 in January.' Hensley email to HR on Jan 5: 'We are dangerously short on Route 9 — I may need drivers to double up.'",
    exhibit_list:
      "Exhibit A: Dashcam footage timestamp 14:32:07; Exhibit B: Driver shift log showing 14.5-hour shift; Exhibit C: CCTD Policy Manual §4.2 (10-hour cap); Exhibit D: Internal memo re: Route 9 understaffing; Exhibit E: Hensley email to HR dated Jan 5, 2026; Exhibit F: Three prior incident reports on Route 9",
    focus_areas:
      "Inconsistency between Hensley's public statements and internal email; Knowledge of understaffing before the accident; Failure to enforce shift-hour policy; Pattern of safety violations on Route 9",
    aggression_level: "Medium",
  },
  {
    id: "utah_v_gunn",
    case_name: "State of Utah v. Derek Gunn",
    case_type: "Criminal — Securities Fraud",
    opposing_party: "Derek Gunn, CEO of Apex Digital Holdings",
    deposition_date: "2026-04-02",
    witness_name: "Derek Gunn; CEO, Apex Digital Holdings",
    witness_role:
      "Defendant and chief executive who authorized misleading investor communications and inflated revenue projections",
    extracted_facts:
      "Between March and September 2025, Apex Digital Holdings issued quarterly reports overstating revenue by 340%. Internal Slack messages show Gunn directed CFO to 'make the numbers work.' SEC filing on August 15 contained projections Gunn personally signed off on. Twelve retail investors lost a combined $4.2M. Gunn liquidated $1.8M in personal stock options two weeks before the restatement. Company auditor resigned citing 'irreconcilable differences with management.'",
    prior_statements:
      "Gunn on CNBC (July 2025): 'Our financials are rock solid — fully audited.' Gunn to board of directors (Aug 2025): 'I was not involved in day-to-day accounting decisions.' Gunn Slack message to CFO (June 2025): 'If Q2 doesn't hit $12M on paper, we're dead. Fix it.'",
    exhibit_list:
      "Exhibit A: SEC Form 10-Q filed August 15, 2025; Exhibit B: Internal Slack logs — Gunn to CFO; Exhibit C: Stock option liquidation records; Exhibit D: Auditor resignation letter; Exhibit E: CNBC interview transcript; Exhibit F: Board meeting minutes, August 2025; Exhibit G: Investor loss declarations (12 affidavits)",
    focus_areas:
      "Direct involvement in falsifying revenue figures; Contradiction between public statements and internal communications; Insider trading via stock liquidation timing; Knowledge of auditor concerns prior to resignation",
    aggression_level: "High",
  },
  {
    id: "atlantis_v_tamontes",
    case_name: "Atlantis Property Group v. Tamontes Construction LLC",
    case_type: "Civil — Breach of Contract / Construction Defect",
    opposing_party: "Tamontes Construction LLC",
    deposition_date: "2026-02-28",
    witness_name: "Ricardo Tamontes; Owner, Tamontes Construction LLC",
    witness_role:
      "General contractor and company owner responsible for construction quality and contract compliance",
    extracted_facts:
      "Tamontes Construction was contracted for a $3.4M residential development. Project delivered 7 months late. Independent inspection found 23 code violations including improper load-bearing wall framing and substandard electrical work. Tamontes subcontracted electrical work to an unlicensed firm. Original contract required all subcontractors to be licensed and bonded. Two units experienced water intrusion within 60 days of occupancy.",
    prior_statements:
      "Tamontes at project handoff meeting: 'Everything passed inspection — we're code compliant across the board.' Tamontes in email to Atlantis PM: 'All subs are licensed, I personally verified.' Subcontractor invoice shows payment to 'QuickWire Solutions' — a company with no state contractor license on file.",
    exhibit_list:
      "Exhibit A: Construction contract with licensing clause §7.3; Exhibit B: Independent inspection report — 23 violations; Exhibit C: QuickWire Solutions invoice; Exhibit D: State licensing database search results; Exhibit E: Tamontes email re: subcontractor verification; Exhibit F: Water intrusion damage photos; Exhibit G: Project timeline showing 7-month delay",
    focus_areas:
      "Use of unlicensed subcontractors in violation of contract; False representations about code compliance; Knowledge of defects prior to handoff; Pattern of cutting corners to reduce costs",
    aggression_level: "Low",
  },
  {
    id: "reyes_v_haller",
    case_name: "Reyes v. Haller Medical Group",
    case_type: "Medical Malpractice — Informed Consent",
    opposing_party: "Haller Medical Group",
    deposition_date: "2026-05-10",
    witness_name: "Dr. Catherine Haller; Chief of Surgery, Haller Medical Group",
    witness_role:
      "Attending surgeon who performed the procedure and was responsible for obtaining informed consent",
    extracted_facts:
      "On October 3, 2025, Dr. Haller performed a laparoscopic cholecystectomy on plaintiff Maria Reyes. During the procedure, Dr. Haller converted to open surgery due to unexpected adhesions. The consent form signed by Reyes only authorized the laparoscopic approach. Post-operative complications included bile duct injury requiring a second corrective surgery. Hospital records show the pre-op assessment noted 'possible adhesions from prior abdominal surgery' but this risk was not discussed with the patient. Reyes was not informed of the conversion until post-anesthesia recovery.",
    prior_statements:
      "Dr. Haller in post-op notes: 'Conversion to open was necessary and within standard of care.' Dr. Haller to hospital risk management: 'I discussed all potential complications with the patient pre-operatively.' Nursing notes from pre-op: 'Consent discussion lasted approximately 4 minutes. Patient asked no questions.'",
    exhibit_list:
      "Exhibit A: Signed consent form — laparoscopic only; Exhibit B: Pre-operative assessment noting possible adhesions; Exhibit C: Operative report detailing conversion; Exhibit D: Post-operative complication records; Exhibit E: Nursing notes — consent discussion duration; Exhibit F: Dr. Haller's statement to risk management; Exhibit G: Second surgery records for bile duct repair",
    focus_areas:
      "Failure to obtain informed consent for open conversion; Knowledge of adhesion risk from pre-op assessment; Contradiction between claimed consent discussion and nursing notes; Whether 4-minute consent discussion meets standard of care",
    aggression_level: "Medium",
  },
  {
    id: "chen_v_meridian",
    case_name: "Chen v. Meridian Financial Advisors",
    case_type: "Civil — Fiduciary Breach / Elder Financial Abuse",
    opposing_party: "Meridian Financial Advisors",
    deposition_date: "2026-06-20",
    witness_name: "James Whitfield; Senior Advisor, Meridian Financial",
    witness_role:
      "Financial advisor assigned to manage plaintiff's retirement portfolio under fiduciary duty",
    extracted_facts:
      "Between 2024-2025, Whitfield executed 847 trades in 82-year-old plaintiff Henry Chen's retirement account, generating $312K in commissions. Account value decreased by 41% during the same period. S&P 500 gained 18% in the same timeframe. Whitfield moved 60% of Chen's portfolio into high-risk crypto derivatives without documented client authorization. Chen has documented mild cognitive decline diagnosed in March 2024. Whitfield's supervisor flagged the account for 'excessive activity' in July 2024 but no action was taken.",
    prior_statements:
      "Whitfield in compliance review: 'Mr. Chen was fully aware of and approved every trade.' Whitfield to Chen's daughter (recorded call): 'Your father specifically asked for aggressive growth strategies.' Internal compliance flag note: 'Advisor Whitfield — Account #4492 shows churn indicators. Supervisor Martinez marked resolved without review.'",
    exhibit_list:
      "Exhibit A: Trade log — 847 transactions over 14 months; Exhibit B: Commission statements totaling $312K; Exhibit C: Account performance vs. S&P 500 benchmark; Exhibit D: Chen cognitive evaluation dated March 2024; Exhibit E: Compliance flag and supervisor dismissal; Exhibit F: Recorded call transcript — Whitfield to Chen's daughter; Exhibit G: Portfolio allocation showing 60% crypto derivatives; Exhibit H: Meridian fiduciary duty policy manual",
    focus_areas:
      "Churning a vulnerable elderly client's account for commissions; Trading in unsuitable high-risk instruments for a retiree; Knowledge of client's cognitive decline; Supervisor failure to act on compliance flags",
    aggression_level: "High",
  },
];

export default cases;
