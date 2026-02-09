import React, { useState } from 'react';
import { Camera, Search, Loader2, MapPin, AlertCircle } from 'lucide-react';
import { aiService } from '../../api/services/ai';
import { MatchLostDogResult } from '../../types/ai';

interface LostPetMatcherProps {
  onMatchFound: (result: MatchLostDogResult) => void;
}

const LostPetMatcher: React.FC<LostPetMatcherProps> = ({ onMatchFound }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleMatch = async () => {
    if (!file) return;

    setAnalyzing(true);
    setError(null);

    try {
        // 1. Upload the notice image first (or we could use base64 if small)
        // Since we don't have a direct 'uploadNotice' endpoint, we might likely use matchLostDog with base64
        // OR we need to convert file to base64.
        
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = async () => {
            const base64 = reader.result as string;
            // Remove prefix data:image/jpeg;base64,
            const cleanBase64 = base64.split(',')[1];
            
            try {
                const result = await aiService.matchLostDog({
                    notice_image_base64: cleanBase64,
                    use_db_reports: true, // Search against existing database
                    similarity_threshold: 0.75
                });
                onMatchFound(result.data);
            } catch (apiErr: any) {
                console.error("API Match Error", apiErr);
                setError("Failed to match. " + (apiErr.response?.data?.message || apiErr.message));
            } finally {
                setAnalyzing(false);
            }
        };
        
    } catch (err) {
        console.error('Match process failed', err);
        setError('An unexpected error occurred.');
        setAnalyzing(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-orange-100 overflow-hidden">
        <div className="p-6 bg-gradient-to-r from-orange-50 to-white">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Search className="text-orange-500" /> Find My Lost Dog
            </h2>
            <p className="text-sm text-gray-600 mt-1">
                Upload a photo of your lost dog. Our Gemini AI will search through stray reports to find a match!
            </p>
        </div>
        
        <div className="p-6">
            <div className="flex flex-col sm:flex-row gap-4 items-center">
                <label className="flex-1 w-full relative cursor-pointer group">
                    <div className={`border-2 border-dashed rounded-lg p-6 text-center transition-all ${file ? 'border-orange-300 bg-orange-50' : 'border-gray-300 hover:border-orange-400 hover:bg-gray-50'}`}>
                        {file ? (
                             <div className="flex flex-col items-center">
                                <img src={URL.createObjectURL(file)} alt="Preview" className="h-24 w-24 object-cover rounded-full mb-2 border-2 border-white shadow-sm" />
                                <span className="text-sm font-medium text-gray-900 truncate max-w-[200px]">{file.name}</span>
                                <span className="text-xs text-orange-600 mt-1">Click to change</span>
                             </div>
                        ) : (
                            <div className="flex flex-col items-center py-2">
                                <div className="bg-orange-100 p-3 rounded-full mb-3 group-hover:bg-orange-200 transition-colors">
                                    <Camera className="text-orange-600" size={24} />
                                </div>
                                <span className="text-sm font-medium text-gray-700">Upload Photo of Dog</span>
                                <span className="text-xs text-gray-500 mt-1">Clear face shots work best</span>
                            </div>
                        )}
                    </div>
                    <input type="file" className="sr-only" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} />
                </label>

                <button 
                    onClick={handleMatch}
                    disabled={!file || analyzing}
                    className={`w-full sm:w-auto px-8 py-4 rounded-lg font-bold shadow-sm flex items-center justify-center gap-2 transition-all ${!file || analyzing ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-orange-500 text-white hover:bg-orange-600 hover:-translate-y-0.5'}`}
                >
                    {analyzing ? <Loader2 className="animate-spin" /> : <Search />}
                    {analyzing ? 'Searching...' : 'Scan & Match'}
                </button>
            </div>
            
            {error && (
                <div className="mt-4 bg-red-50 text-red-600 p-3 rounded-md text-sm flex items-center gap-2">
                    <AlertCircle size={16} /> {error}
                </div>
            )}
        </div>
    </div>
  );
};

export default LostPetMatcher;
