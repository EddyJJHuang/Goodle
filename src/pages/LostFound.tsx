import React, { useState } from 'react';
import { Search, MapPin, Plus, Minus, AlertCircle, X, ChevronRight } from 'lucide-react';
import { mockMapMarkers } from '../services/mockData';
import LostPetMatcher from '../components/ai/LostPetMatcher';
import { MatchLostDogResult } from '../types/ai';

const LostFound = () => {
  const [selectedMarker, setSelectedMarker] = useState<string | null>(null);
  const [showMatcher, setShowMatcher] = useState(false);
  const [matchResult, setMatchResult] = useState<MatchLostDogResult | null>(null);

  const handleMatchFound = (result: MatchLostDogResult) => {
      setMatchResult(result);
      setShowMatcher(false); // Close matcher to show results
  };

  return (
    <div className="flex-1 relative overflow-hidden h-[calc(100vh-64px)] bg-gray-200">
        {/* Pseudo Map Background */}
        <div className="absolute inset-0 bg-gray-200 z-0 cursor-grab active:cursor-grabbing opacity-50" style={{
            backgroundImage: 'linear-gradient(#e5e7eb 1px, transparent 1px), linear-gradient(90deg, #e5e7eb 1px, transparent 1px)',
            backgroundSize: '40px 40px'
        }}>
           {/* Simulated Roads/Shapes */}
           <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-30" xmlns="http://www.w3.org/2000/svg">
               <path d="M-100,300 Q400,250 800,500 T1600,600" fill="none" stroke="#9ca3af" strokeWidth="20" />
               <path d="M200,800 Q500,600 600,200 T800,-100" fill="none" stroke="#9ca3af" strokeWidth="15" />
           </svg>
        </div>

        {/* Map UI Overlay - Search */}
        <div className="absolute top-6 left-6 z-10 w-80 max-w-[calc(100vw-3rem)] pointer-events-none">
            <div className="bg-white/95 backdrop-blur-sm rounded-xl shadow-xl border border-gray-200 p-4 space-y-5 pointer-events-auto">
                {!matchResult ? (
                    <>
                        <div className="relative">
                            <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
                            <input type="text" placeholder="Search location or breed..." className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent" />
                        </div>
                        
                        <div className="pt-2 border-t border-gray-100">
                             <button 
                                onClick={() => setShowMatcher(true)}
                                className="w-full bg-orange-50 text-orange-600 hover:bg-orange-100 border border-orange-200 rounded-lg py-3 px-4 flex items-center justify-center gap-2 font-medium transition-colors"
                             >
                                <Search size={18} />
                                Find by Photo (AI)
                             </button>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Show On Map</label>
                            <div className="flex flex-col space-y-2">
                                 <label className="flex items-center space-x-3 cursor-pointer p-2 rounded-lg hover:bg-gray-50">
                                    <input type="checkbox" defaultChecked className="text-primary rounded border-gray-300 focus:ring-primary h-4 w-4" />
                                    <div className="flex items-center space-x-2">
                                        <span className="w-3 h-3 bg-primary rounded-full"></span>
                                        <span className="text-sm font-medium text-gray-700">Stray Reports</span>
                                    </div>
                                </label>
                                <label className="flex items-center space-x-3 cursor-pointer p-2 rounded-lg hover:bg-gray-50">
                                    <input type="checkbox" defaultChecked className="text-secondary rounded border-gray-300 focus:ring-secondary h-4 w-4" />
                                    <div className="flex items-center space-x-2">
                                        <span className="w-3 h-3 bg-secondary rounded-full"></span>
                                        <span className="text-sm font-medium text-gray-700">Lost Pet Announcements</span>
                                    </div>
                                </label>
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="animate-in fade-in slide-in-from-left-4">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="font-bold text-gray-900">AI Search Results</h3>
                            <button onClick={() => setMatchResult(null)} className="text-gray-400 hover:text-gray-600"><X size={18}/></button>
                        </div>
                        
                        <div className="bg-orange-50 border border-orange-100 rounded-lg p-3 mb-4">
                            <div className="flex items-center gap-2 text-orange-800 font-medium mb-1">
                                <Search size={16} />
                                {matchResult.is_match ? 'Potential Match Found!' : 'No High Confidence Match'}
                            </div>
                            <p className="text-xs text-orange-700">
                                Similarity Score: {(matchResult.similarity_score * 100).toFixed(1)}%
                            </p>
                        </div>

                        {matchResult.matched_report_ids.length > 0 ? (
                            <div className="space-y-3">
                                <p className="text-xs text-gray-500 font-medium uppercase">Matched Reports</p>
                                {matchResult.matched_report_ids.map(id => (
                                    <div key={id} className="bg-white border border-gray-200 rounded-lg p-2 flex gap-3 hover:border-primary cursor-pointer transition-colors">
                                        <div className="w-12 h-12 bg-gray-200 rounded-md flex-shrink-0 overflow-hidden">
                                             <img src="https://images.unsplash.com/photo-1544175287-e467232a3f14?auto=format&fit=crop&q=80&w=150" alt="Match" className="w-full h-full object-cover" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-gray-900 truncate">Report #{id.substring(0, 8)}</p>
                                            <p className="text-xs text-gray-500">2km away • 2h ago</p>
                                        </div>
                                        <ChevronRight size={16} className="text-gray-400 self-center" />
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-gray-500 text-sm">
                                <p>No matching stray reports found yet.</p>
                                <button className="mt-2 text-primary hover:underline" onClick={() => setMatchResult(null)}>Try another photo</button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>

        {/* AI Matcher Modal Overlay */}
        {showMatcher && (
            <div className="absolute inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
                <div className="w-full max-w-lg relative">
                    <button 
                        onClick={() => setShowMatcher(false)}
                        className="absolute -top-12 right-0 text-white hover:text-gray-200 transition-colors"
                    >
                        <X size={24} />
                    </button>
                    <LostPetMatcher onMatchFound={handleMatchFound} />
                </div>
            </div>
        )}

        {/* Markers (Demo) */}
        {!matchResult && mockMapMarkers.map((marker) => (
             <div 
                key={marker.id} 
                className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer group z-10 transition-all hover:scale-110 hover:z-20"
                style={{ top: `${marker.lat}%`, left: `${marker.lng}%` }}
                onClick={() => setSelectedMarker(marker.id)}
             >
                <div className="relative">
                     {/* Pulse effect for selected/active */}
                     <div className={`absolute -inset-4 rounded-full opacity-30 animate-ping ${marker.type === 'stray' ? 'bg-primary' : 'bg-secondary'}`}></div>
                     
                     <div className={`relative w-10 h-10 rounded-full border-4 border-white shadow-lg overflow-hidden ${marker.type === 'stray' ? 'bg-primary' : 'bg-secondary'}`}>
                        <img src={marker.image} alt="Pet" className="w-full h-full object-cover" />
                     </div>
                </div>
             </div>
        ))}

        {/* Selected Marker Detail Card */}
        {selectedMarker && (
            <div className="absolute bottom-1/2 left-1/2 transform -translate-x-1/2 -translate-y-20 z-30">
                 {mockMapMarkers.filter(m => m.id === selectedMarker).map(marker => (
                    <div key={marker.id} className="w-64 bg-white rounded-xl shadow-2xl overflow-hidden border border-gray-200 animate-in fade-in zoom-in duration-300">
                        <div className="relative h-32">
                            <img src={marker.image} alt="Pet" className="w-full h-full object-cover" />
                             <div className={`absolute top-2 right-2 text-white text-xs px-2 py-0.5 rounded-full font-bold shadow-sm ${marker.type === 'stray' ? 'bg-primary' : 'bg-secondary'}`}>
                                {marker.type === 'stray' ? 'Stray' : 'Lost'}
                             </div>
                        </div>
                        <div className="p-3">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="font-bold text-gray-900">{marker.petName || 'Unknown Pet'}</h3>
                                    <p className="text-xs text-gray-500">{marker.timeAgo}</p>
                                </div>
                                <AlertCircle size={16} className="text-gray-400" />
                            </div>
                            <p className="mt-2 text-xs text-gray-600 line-clamp-2">
                                {marker.description}
                            </p>
                            <div className="mt-3 flex space-x-2">
                                <button className="flex-1 bg-primary text-white text-xs font-semibold py-1.5 px-3 rounded-md hover:bg-orange-600 transition-colors shadow-sm">
                                    Contact
                                </button>
                                <button className="flex-1 bg-gray-100 text-gray-700 text-xs font-semibold py-1.5 px-3 rounded-md hover:bg-gray-200 transition-colors" onClick={() => setSelectedMarker(null)}>
                                    Close
                                </button>
                            </div>
                        </div>
                        {/* Triangle pointing down */}
                        <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-white rotate-45"></div>
                    </div>
                 ))}
            </div>
        )}

        {/* Map Controls */}
        <div className="absolute bottom-6 right-6 z-10 flex flex-col items-end space-y-4">
            <div className="bg-white rounded-lg shadow-lg border border-gray-200 flex flex-col overflow-hidden">
                <button className="p-2 hover:bg-gray-100 text-gray-600 border-b border-gray-200"><Plus size={20} /></button>
                <button className="p-2 hover:bg-gray-100 text-gray-600"><Minus size={20} /></button>
            </div>
            <button className="group flex items-center space-x-2 bg-primary hover:bg-orange-600 text-white px-6 py-3 rounded-full shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200">
                <AlertCircle size={20} />
                <span className="font-bold text-lg">Report Now</span>
            </button>
        </div>
    </div>
  );
};

export default LostFound;