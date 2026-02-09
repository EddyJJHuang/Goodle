export interface PhotoAnalysisResult {
  breed: string;
  size: 'small' | 'medium' | 'large';
  age_group: 'puppy' | 'adult' | 'senior';
  appearance_tags: string[];
  personality_guess: string;
}

export interface VideoAnalysisResult {
  activity_level: number;
  approach_speed: number;
  emotional_stability: number;
  play_preference: 'chase' | 'wrestle' | 'mixed' | string;
  body_language_score: number;
}

export interface LocationInput {
  latitude: number;
  longitude: number;
}

export interface StrayReportPayload {
  report_id: string;
  image_base64?: string;
  image_path?: string;
  reported_at?: string;
  location?: LocationInput;
}

export interface CandidateReportPayload extends StrayReportPayload {}

export interface MatchLostDogPayload {
  owner_id?: string;
  notice_image_base64?: string;
  notice_image_path?: string;
  lost_at?: string;
  location?: LocationInput;
  use_db_reports?: boolean;
  candidate_reports?: CandidateReportPayload[];
  similarity_threshold?: number;
  max_distance_km?: number;
  max_time_gap_hours?: number;
}

export interface MatchLostDogResult {
  is_match: boolean;
  similarity_score: number;
  matched_report_ids: string[];
  candidate_count: number;
}

export interface MatchNotification {
  id: number;
  owner_id: string;
  matched_report_ids: string[];
  similarity_score: number;
  created_at: string;
}
