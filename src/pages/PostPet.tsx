import React, { useState } from 'react';
import { Camera, Upload, Wand2, Check, Loader2, Info } from 'lucide-react';
import PhotoProcessor from '../components/ai/PhotoProcessor';
import VideoProcessor from '../components/ai/VideoProcessor';
import { PhotoAnalysisResult, VideoAnalysisResult } from '../types/ai';

const PostPet = () => {
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [currentPetId] = useState(`pet_${Date.now()}`); // Generate a temp ID for this session
  const [formData, setFormData] = useState({
      name: '',
      breed: '',
      color: '',
      age: '',
      description: '',
      personality: [] as string[],
      imagePath: ''
  });

  const handlePhotoAnalysis = (result: PhotoAnalysisResult, imagePath: string) => {
    setAnalyzed(true);
    setFormData(prev => ({
        ...prev,
        breed: result.breed || prev.breed,
        age: result.age_group || prev.age,
        // Map tags to description or personality
        description: `This ${result.size} ${result.breed} appears to be a ${result.age_group}. \n\nAI Suggested Traits: ${result.appearance_tags.join(', ')}`,
        personality: result.personality_guess ? [result.personality_guess] : [],
        imagePath: imagePath
    }));
  };

  const handleVideoAnalysis = (result: VideoAnalysisResult) => {
      const traits = [];
      if (result.activity_level > 7) traits.push('High Energy');
      else if (result.activity_level < 4) traits.push('Calm');
      
      if (result.emotional_stability > 7) traits.push('Confident');
      
      traits.push(`Play Style: ${result.play_preference}`);

      setFormData(prev => ({
          ...prev,
          personality: [...new Set([...prev.personality, ...traits])]
      }));
  };

  return (
    <div className="flex-grow py-10 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 text-center sm:text-left">
          <h1 className="text-3xl font-display font-bold text-gray-900">Post a Pet for Adoption</h1>
          <p className="mt-2 text-sm text-gray-500">Help a furry friend find their forever home. AI will help you fill out the details!</p>
        </div>

        <form className="space-y-8" onSubmit={(e) => e.preventDefault()}>
          
          {/* AI Workflow Section */}
          <div className="space-y-6">
              {/* Step 1: Photos */}
              <PhotoProcessor onAnalysisCollplete={handlePhotoAnalysis} />

              {/* Step 2: Video (Optional) */}
              <VideoProcessor currentPetId={currentPetId} onAnalysisResult={handleVideoAnalysis} />
          </div>

          {/* AI Insights Display */}
          {analyzed && (
              <div className="bg-green-50 border border-green-100 rounded-xl p-6 animate-in fade-in slide-in-from-top-4 duration-500">
                  <h3 className="text-green-800 font-bold flex items-center gap-2 mb-2">
                      <Wand2 size={18} /> AI Analysis Complete
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-green-700">
                      <div>
                          <span className="font-semibold block mb-1">Detected Breed:</span> 
                          <span className="bg-white px-2 py-1 rounded border border-green-200">{formData.breed || 'Unknown'}</span>
                      </div>
                       <div>
                          <span className="font-semibold block mb-1">Age Estimate:</span> 
                          <span className="bg-white px-2 py-1 rounded border border-green-200 capitalize">{formData.age || 'Unknown'}</span>
                      </div>
                      <div className="md:col-span-2">
                          <span className="font-semibold block mb-1">Personality Insights:</span>
                          <div className="flex flex-wrap gap-2">
                              {formData.personality.length > 0 ? (
                                  formData.personality.map((trait, idx) => (
                                      <span key={idx} className="bg-green-600 text-white px-2 py-0.5 rounded-full text-xs">{trait}</span>
                                  ))
                              ) : (
                                  <span className="text-gray-400 italic">Upload a video to get personality insights</span>
                              )}
                          </div>
                      </div>
                  </div>
              </div>
          )}

          {/* Details Form - Auto-filled by AI */}
          <div className="bg-white shadow-sm rounded-xl p-6 sm:p-8 border border-gray-100">
              <div className="flex justify-between items-center mb-6">
                 <h2 className="text-lg font-medium text-gray-900">Pet Details</h2>
                 {analyzed && <span className="text-xs text-green-600 flex items-center gap-1"><Check size={12}/> Auto-filled by AI</span>}
              </div>
              
              <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                  <div className="sm:col-span-6">
                      <label className="block text-sm font-medium text-gray-700">Pet Name</label>
                      <div className="mt-1">
                          <input 
                            type="text" 
                            value={formData.name}
                            onChange={(e) => setFormData({...formData, name: e.target.value})}
                            className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" 
                            placeholder="e.g. Buddy" 
                          />
                      </div>
                  </div>
                  <div className="sm:col-span-3">
                      <label className="block text-sm font-medium text-gray-700">Breed</label>
                      <div className="mt-1">
                          <input 
                            type="text" 
                            value={formData.breed}
                            onChange={(e) => setFormData({...formData, breed: e.target.value})}
                            className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" 
                            placeholder="e.g. Golden Retriever" 
                          />
                      </div>
                  </div>
                   <div className="sm:col-span-3">
                      <label className="block text-sm font-medium text-gray-700">Age / Life Stage</label>
                      <div className="mt-1">
                          <input 
                            type="text" 
                            value={formData.age}
                            onChange={(e) => setFormData({...formData, age: e.target.value})}
                            className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" 
                            placeholder="e.g. Puppy, Adult" 
                          />
                      </div>
                  </div>
                  <div className="sm:col-span-6">
                      <label className="block text-sm font-medium text-gray-700">Description & Personality</label>
                      <div className="mt-1">
                          <textarea 
                            rows={4} 
                            value={formData.description}
                            onChange={(e) => setFormData({...formData, description: e.target.value})}
                            className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md p-3 border" 
                            placeholder="Describe the pet's character..."
                          ></textarea>
                      </div>
                      <p className="mt-2 text-xs text-gray-500">AI suggestion: Upload a video to generate a more detailed personality description.</p>
                  </div>
              </div>
          </div>

          <div className="flex justify-end gap-3 pt-4">
               <button className="bg-white py-3 px-6 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50">Cancel</button>
               <button className="bg-primary border border-transparent rounded-md shadow-sm py-3 px-8 text-sm font-bold text-white hover:bg-orange-500 transform hover:-translate-y-0.5 transition-all">
                  Post Adoption Request
               </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PostPet;