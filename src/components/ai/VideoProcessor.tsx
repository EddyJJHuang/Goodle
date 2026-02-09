import React, { useState } from 'react';
import { Video, Upload, Loader2, Check, AlertCircle, PlayCircle } from 'lucide-react';
import { aiService } from '../../api/services/ai';
import { VideoAnalysisResult } from '../../types/ai';

interface VideoProcessorProps {
  onAnalysisResult: (result: VideoAnalysisResult) => void;
  currentPetId: string; // We likely need a Pet ID to associate the video with
}

const VideoProcessor: React.FC<VideoProcessorProps> = ({ onAnalysisResult, currentPetId }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 50 * 1024 * 1024) {
        setError("File size too large. Please upload visuals under 50MB.");
        return;
    }

    setVideoFile(file);
    setError(null);
    setAnalyzing(true);
    setProgress(10); // Start progress

    try {
      // Simulate progress while uploading/processing
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 5, 90));
      }, 500);

      const result = await aiService.uploadAndAnalyzeVideo(currentPetId, file);
      
      clearInterval(progressInterval);
      setProgress(100);
      onAnalysisResult(result.data);
      
    } catch (err: any) {
      console.error('Video analysis failed', err);
      setError(err.response?.data?.message || 'Failed to analyze video. Please try again.');
      setVideoFile(null); // Reset on error
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="bg-white shadow-sm rounded-xl p-6 sm:p-8 border border-gray-100">
      <div className="md:flex md:items-start md:gap-6">
        <div className="md:w-1/3 mb-4 md:mb-0">
          <h2 className="text-lg font-medium text-gray-900 flex items-center gap-2">
            <Video className="text-purple-500" size={20} /> Personality Video
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Upload a short video (10-30s) of the pet playing or interacting. AI will analyze their personality traits!
          </p>
        </div>
        <div className="md:w-2/3">
          <div className="relative">
            {!videoFile ? (
                 <label className="relative flex flex-col justify-center items-center w-full h-32 rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 hover:bg-gray-100 hover:border-purple-500 transition-all cursor-pointer">
                    <div className="space-y-1 text-center">
                        <Upload className="mx-auto h-8 w-8 text-gray-400" />
                        <div className="text-sm text-gray-600">
                            <span className="font-medium text-purple-600 hover:text-purple-700">Upload Video</span>
                        </div>
                        <p className="text-xs text-gray-500">MP4, MOV up to 50MB</p>
                    </div>
                    <input type="file" className="sr-only" accept="video/*" onChange={handleFileChange} />
                </label>
            ) : (
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div className="flex items-center gap-3">
                        <div className="bg-purple-100 p-2 rounded-full">
                            <PlayCircle className="text-purple-600" size={24} />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">{videoFile.name}</p>
                            <p className="text-xs text-gray-500">{(videoFile.size / (1024 * 1024)).toFixed(1)} MB</p>
                        </div>
                        {analyzing ? (
                             <div className="text-right">
                                <span className="text-xs font-semibold text-purple-600">{progress}%</span>
                             </div>
                        ) : (
                            !error && <Check className="text-green-500" size={20} />
                        )}
                    </div>
                    
                    {analyzing && (
                        <div className="mt-3 w-full bg-gray-200 rounded-full h-1.5">
                            <div className="bg-purple-600 h-1.5 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
                        </div>
                    )}
                    
                    {!analyzing && !error && (
                         <p className="mt-2 text-xs text-green-600 font-medium flex items-center gap-1">
                            <Check size={12} /> Personality analysis complete!
                         </p>
                    )}
                </div>
            )}

            {error && (
                <div className="mt-2 text-xs text-red-600 flex items-center gap-1">
                    <AlertCircle size={12} /> {error}
                </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoProcessor;
