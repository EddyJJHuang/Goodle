import client from '../client';
import {
  MatchLostDogPayload,
  MatchLostDogResult,
  MatchNotification,
  PhotoAnalysisResult,
  StrayReportPayload,
  VideoAnalysisResult,
} from '../../types/ai';

export interface AnalyzePhotoPayload {
  pet_id: string;
  image_base64?: string;
  image_path?: string;
}

export interface AnalyzeVideoPayload {
  pet_id: string;
  video_path: string;
  preprocess_seconds?: number;
}

export const aiService = {
  analyzePhoto: (payload: AnalyzePhotoPayload) =>
    client.post<PhotoAnalysisResult>('/ai/analyze-photo', payload),

  analyzeVideo: (payload: AnalyzeVideoPayload) =>
    client.post<VideoAnalysisResult>('/ai/analyze-video', payload),

  upsertStrayReport: (payload: StrayReportPayload) =>
    client.post<{ report_id: string }>('/ai/stray-reports', payload),

  listStrayReports: () =>
    client.get<any[]>('/ai/stray-reports'),

  matchLostDog: (payload: MatchLostDogPayload) =>
    client.post<MatchLostDogResult>('/ai/match-lost-dog', payload),

  listMatchNotifications: () =>
    client.get<MatchNotification[]>('/ai/notifications'),
};
