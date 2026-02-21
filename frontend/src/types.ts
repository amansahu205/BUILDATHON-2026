export interface VerdictCase {
  id: string;
  case_name: string;
  case_type: string;
  opposing_party: string;
  deposition_date: string;
  witness_name: string;
  witness_role: string;
  extracted_facts: string;
  prior_statements: string;
  exhibit_list: string;
  focus_areas: string;
  aggression_level: "Low" | "Medium" | "High";
}

export interface TranscriptEntry {
  speaker: "agent" | "witness";
  text: string;
  timestamp: Date;
}
