import React, { useState } from 'react';
import { Camera, Upload, Wand2, Check, Loader2 } from 'lucide-react';

const PostPet = () => {
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [formData, setFormData] = useState({
      breed: '',
      color: '',
      tags: [] as string[]
  });

  const handleSimulateAI = () => {
    setAnalyzing(true);
    // Simulate AI delay
    setTimeout(() => {
        setAnalyzing(false);
        setAnalyzed(true);
        setFormData({
            breed: 'Golden Retriever Mix',
            color: 'Golden',
            tags: ['Friendly', 'Long Coat', 'Adult']
        });
    }, 2500);
  };

  return (
    <div className="flex-grow py-10 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8 text-center sm:text-left">
          <h1 className="text-3xl font-display font-bold text-gray-900">Post a Pet for Adoption</h1>
          <p className="mt-2 text-sm text-gray-500">Help a furry friend find their forever home. Please fill out the details below as accurately as possible.</p>
        </div>

        <form className="space-y-8" onSubmit={(e) => e.preventDefault()}>
          {/* Photos */}
          <div className="bg-white shadow-sm rounded-xl p-6 sm:p-8 border border-gray-100">
            <div className="md:flex md:items-start md:gap-6">
              <div className="md:w-1/3 mb-4 md:mb-0">
                <h2 className="text-lg font-medium text-gray-900 flex items-center gap-2">
                  <Camera className="text-secondary" size={20} /> Photos
                </h2>
                <p className="mt-1 text-sm text-gray-500">Upload up to 5 photos. High quality photos increase adoption chances!</p>
              </div>
              <div className="md:w-2/3">
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                   <div className="col-span-2 sm:col-span-3 relative group">
                        <label className="relative flex flex-col justify-center items-center w-full h-48 rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 hover:bg-gray-100 hover:border-primary transition-all cursor-pointer">
                            <div className="space-y-1 text-center">
                                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                                <div className="text-sm text-gray-600">
                                    <span className="font-medium text-primary hover:text-orange-600">Click to upload</span> or drag and drop
                                </div>
                                <p className="text-xs text-gray-500">PNG, JPG, GIF up to 5MB</p>
                            </div>
                            <input type="file" className="sr-only" onChange={handleSimulateAI} />
                        </label>
                   </div>
                   {analyzed && (
                       <div className="relative aspect-square rounded-lg overflow-hidden border border-gray-200">
                           <img src="https://images.unsplash.com/photo-1552053831-71594a27632d?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80" alt="Uploaded" className="w-full h-full object-cover" />
                           <div className="absolute top-1 right-1 bg-green-500 rounded-full p-0.5"><Check size={12} className="text-white"/></div>
                       </div>
                   )}
                </div>
              </div>
            </div>
          </div>

          {/* AI Analysis Result */}
          {analyzing && (
              <div className="bg-blue-50 border border-blue-100 rounded-xl p-6 flex items-center justify-center gap-3 text-blue-700 animate-pulse">
                  <Loader2 className="animate-spin" /> Analyzing photo features with Gemini AI...
              </div>
          )}

          {analyzed && (
              <div className="bg-green-50 border border-green-100 rounded-xl p-6 animate-in fade-in slide-in-from-top-4 duration-500">
                  <h3 className="text-green-800 font-bold flex items-center gap-2 mb-2">
                      <Wand2 size={18} /> AI Analysis Complete
                  </h3>
                  <div className="flex gap-4 text-sm text-green-700">
                      <div>
                          <span className="font-semibold">Detected Breed:</span> {formData.breed}
                      </div>
                       <div>
                          <span className="font-semibold">Color:</span> {formData.color}
                      </div>
                  </div>
              </div>
          )}

          {/* Details */}
          <div className="bg-white shadow-sm rounded-xl p-6 sm:p-8 border border-gray-100">
              <h2 className="text-lg font-medium text-gray-900 mb-6">Pet Details</h2>
              <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                  <div className="sm:col-span-6">
                      <label className="block text-sm font-medium text-gray-700">Pet Name</label>
                      <div className="mt-1">
                          <input type="text" className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" placeholder="e.g. Buddy" />
                      </div>
                  </div>
                  <div className="sm:col-span-3">
                      <label className="block text-sm font-medium text-gray-700">Breed</label>
                      <div className="mt-1">
                          <input type="text" defaultValue={formData.breed} className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" placeholder="e.g. Golden Retriever" />
                      </div>
                  </div>
                   <div className="sm:col-span-3">
                      <label className="block text-sm font-medium text-gray-700">Age</label>
                      <div className="mt-1">
                          <input type="text" className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" placeholder="e.g. 2 years" />
                      </div>
                  </div>
                  <div className="sm:col-span-6">
                      <label className="block text-sm font-medium text-gray-700">Personality</label>
                      <div className="mt-1">
                          <textarea rows={3} className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md p-3 border" placeholder="Describe the pet's character..."></textarea>
                      </div>
                  </div>
              </div>
          </div>

          <div className="flex justify-end gap-3 pt-4">
               <button className="bg-white py-3 px-6 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50">Cancel</button>
               <button className="bg-primary border border-transparent rounded-md shadow-sm py-3 px-8 text-sm font-bold text-white hover:bg-orange-500 transform hover:-translate-y-0.5 transition-all">Post Adoption Request</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PostPet;