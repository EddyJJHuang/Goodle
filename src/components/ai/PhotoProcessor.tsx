import React, { useState, useRef } from 'react';
import { Camera, Upload, Loader2, Check, AlertCircle } from 'lucide-react';
import { aiService } from '../../api/services/ai';
import { PhotoAnalysisResult } from '../../types/ai';

interface PhotoProcessorProps {
  onAnalysisCollplete: (result: PhotoAnalysisResult, imagePath: string) => void;
}

const PhotoProcessor: React.FC<PhotoProcessorProps> = ({ onAnalysisCollplete }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fileInputKey, setFileInputKey] = useState(0); 

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Reset state
    setError(null);
    setPreview(URL.createObjectURL(file));
    setAnalyzing(true);

    try {
      // 1. Create a FormData object to upload the file
      // Note: The backend expects 'pet_id' and 'photo' in FormData for /analyze-photo/upload
      // We use a temporary ID 'temp_upload' for initial analysis without saving to DB yet, 
      // or generate a UUID if the backend requires a unique one. 
      // Looking at the backend code, it calls analyzer.analyze_and_persist which might require a real ID if it saves to DB.
      // However, for the "Post Pet" flow, we might just want analysis results first. 
      // Let's assume we generate a temporary ID or the backend handles "temp". 
      // The backend actually persists the pet info. 
      // Strategy: We'll use a client-side generated UUID or timestamp as a temporary pet_id.
      const tempPetId = `temp_${Date.now()}`; 
      
      const formData = new FormData();
      formData.append('pet_id', tempPetId);
      formData.append('photo', file);

      // We need to implement the upload method in aiService if it's strictly JSON based in the current file.
      // Let's check api/services/ai.ts again. It has analyzePhoto (JSON) but maybe not upload.
      // Wait, the backend has /analyze-photo/upload. We should probably use that.
      // Since aiService.ts might not have it, we'll implement the call directly here or extend aiService.
      // For now, let's implement the fetch/axios call here or assume we will update aiService.
      
      // Actually, better to update aiService first. But I am in this file now. 
      // I will write the component to call a new method `uploadAndAnalyzePhoto` which I will add to aiService.
      
      const result = await aiService.uploadAndAnalyzePhoto(tempPetId, file);
      
      onAnalysisCollplete(result.data, preview || ''); // We might want to pass the backend path if returned
      
    } catch (err: any) {
      console.error('Analysis failed', err);
      setError(err.response?.data?.message || 'Failed to analyze photo. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="bg-white shadow-sm rounded-xl p-6 sm:p-8 border border-gray-100">
      <div className="md:flex md:items-start md:gap-6">
        <div className="md:w-1/3 mb-4 md:mb-0">
          <h2 className="text-lg font-medium text-gray-900 flex items-center gap-2">
            <Camera className="text-secondary" size={20} /> Photos
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Upload a clear photo of your pet. AI will automatically detect breed, age, and features!
          </p>
        </div>
        <div className="md:w-2/3">
          <div className="grid grid-cols-1 gap-4">
             <div className="relative group">
                  {!preview ? (
                      <label className="relative flex flex-col justify-center items-center w-full h-48 rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 hover:bg-gray-100 hover:border-primary transition-all cursor-pointer">
                          <div className="space-y-1 text-center">
                              {analyzing ? (
                                  <Loader2 className="mx-auto h-12 w-12 text-primary animate-spin" />
                              ) : (
                                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                              )}
                              <div className="text-sm text-gray-600">
                                  <span className="font-medium text-primary hover:text-orange-600">
                                      {analyzing ? 'Analyzing...' : 'Click to upload'}
                                  </span>
                                  {!analyzing && ' or drag and drop'}
                              </div>
                              <p className="text-xs text-gray-500">JPG, PNG up to 5MB</p>
                          </div>
                          <input 
                              key={fileInputKey}
                              type="file" 
                              className="sr-only" 
                              accept="image/*"
                              onChange={handleFileChange} 
                              disabled={analyzing}
                          />
                      </label>
                  ) : (
                      <div className="relative h-64 rounded-lg overflow-hidden border border-gray-200 bg-gray-100 flex items-center justify-center">
                          <img src={preview} alt="Uploaded" className="max-h-full max-w-full object-contain" />
                          <button 
                              onClick={() => { setPreview(null); setFileInputKey(k => k + 1); }}
                              className="absolute top-2 right-2 bg-white/90 text-gray-700 p-1.5 rounded-full hover:text-red-600 transition-colors shadow-sm"
                          >
                              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                          </button>
                          
                          {analyzing && (
                              <div className="absolute inset-0 bg-white/50 backdrop-blur-sm flex items-center justify-center">
                                  <div className="text-center">
                                      <Loader2 className="h-10 w-10 text-primary animate-spin mx-auto mb-2" />
                                      <p className="text-primary font-medium">Analyzing Pet Features...</p>
                                  </div>
                              </div>
                          )}

                          {!analyzing && !error && (
                             <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-green-100 text-green-800 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1 shadow-sm">
                                <Check size={12} /> Analysis Complete
                             </div>
                          )}
                      </div>
                  )}
                  
                  {error && (
                      <div className="mt-3 bg-red-50 text-red-600 p-3 rounded-md text-sm flex items-center gap-2">
                          <AlertCircle size={16} /> {error}
                      </div>
                  )}
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PhotoProcessor;
