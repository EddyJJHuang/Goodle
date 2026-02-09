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

  uploadAndAnalyzePhoto: (petId: string, photo: File) => {
    const formData = new FormData();
    formData.append('pet_id', petId);
    formData.append('photo', photo);
    return client.post<PhotoAnalysisResult>('/ai/analyze-photo/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  analyzeVideo: (payload: AnalyzeVideoPayload) =>
    client.post<VideoAnalysisResult>('/ai/analyze-video', payload),

  uploadAndAnalyzeVideo: (petId: string, video: File) => {
    const formData = new FormData();
    formData.append('pet_id', petId);
    formData.append('video', video);
    formData.append('preprocess_seconds', '10');
    return client.post<VideoAnalysisResult>('/ai/analyze-video/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  upsertStrayReport: (payload: StrayReportPayload) =>
    client.post<{ report_id: string }>('/ai/stray-reports', payload),

  listStrayReports: () =>
    client.get<any[]>('/ai/stray-reports'),

  matchLostDog: (payload: MatchLostDogPayload) =>
    client.post<MatchLostDogResult>('/ai/match-lost-dog', payload),

  listMatchNotifications: () =>
    client.get<MatchNotification[]>('/ai/notifications'),
};
