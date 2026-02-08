import React, { useState } from 'react';
import { Heart, X, Star, Info, MapPin, BadgeCheck, ChevronDown, Activity, Users, ShieldCheck } from 'lucide-react';
import { mockPets } from '../services/mockData';

const Matching = () => {
  const [currentPetIndex, setCurrentPetIndex] = useState(0);
  const pet = mockPets[currentPetIndex % mockPets.length];

  const handleNext = () => {
    setCurrentPetIndex((prev) => prev + 1);
  };

  return (
    <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 flex flex-col md:flex-row gap-8 bg-gray-50 min-h-[calc(100vh-64px)]">
      {/* Sidebar Filters */}
      <aside className="w-full md:w-1/4 hidden md:flex flex-col gap-6">
        <div className="bg-white p-6 rounded-2xl shadow-sm sticky top-24 border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-display font-bold text-gray-900">Filters</h2>
            <button className="text-sm text-primary font-semibold hover:text-primary-hover">Reset</button>
          </div>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Maximum Distance</label>
            <input type="range" min="1" max="100" defaultValue="25" className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary" />
            <div className="flex justify-between mt-1 text-xs text-gray-500">
                <span>5km</span>
                <span className="font-bold text-gray-900">25 km</span>
                <span>100km</span>
            </div>
          </div>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
            <div className="flex gap-2">
                <button className="flex-1 py-2 rounded-xl border border-gray-200 text-gray-600 hover:border-primary hover:text-primary transition-colors text-sm font-semibold">Male</button>
                <button className="flex-1 py-2 rounded-xl border-2 border-primary bg-primary/10 text-primary text-sm font-bold">Female</button>
            </div>
          </div>
          <div className="mb-6">
             <label className="block text-sm font-medium text-gray-700 mb-2">Personality</label>
             <div className="flex flex-wrap gap-2">
                 {['Playful', 'Calm', 'Energetic', 'Friendly'].map(tag => (
                     <span key={tag} className={`px-3 py-1 rounded-full text-xs font-medium cursor-pointer border transition-colors ${tag === 'Calm' ? 'bg-primary text-white border-primary' : 'bg-gray-100 text-gray-600 border-transparent hover:border-primary hover:text-primary'}`}>
                         {tag}
                     </span>
                 ))}
             </div>
          </div>
        </div>
      </aside>

      {/* Main Card Area */}
      <main className="w-full md:w-2/4 flex flex-col items-center justify-center">
        <div className="w-full max-w-md relative aspect-[3/4] md:aspect-[4/5] group">
            {/* Card Content */}
            <div className="absolute inset-0 bg-white rounded-3xl overflow-hidden shadow-2xl border border-gray-100 transition-transform duration-300">
                <div className="relative h-2/3 w-full">
                    <img src={pet.image} alt={pet.name} className="w-full h-full object-cover" />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent"></div>
                    
                    <div className="absolute top-4 left-4 flex gap-2">
                        <span className="bg-black/30 backdrop-blur-md text-white px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1">
                            <MapPin size={12} /> {pet.distance} away
                        </span>
                        <span className="bg-primary text-white px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1 shadow-lg">
                            <BadgeCheck size={12} /> Verified
                        </span>
                    </div>

                    <div className="absolute bottom-0 left-0 w-full p-6 text-white">
                        <div className="flex items-end gap-3 mb-1">
                            <h1 className="text-4xl font-display font-bold">{pet.name}</h1>
                            <span className="text-xl font-medium mb-1.5 opacity-90">{pet.age}</span>
                        </div>
                        <p className="text-sm font-medium opacity-90 flex items-center gap-1">
                            {pet.breed}
                        </p>
                    </div>
                </div>

                <div className="h-1/3 p-6 flex flex-col justify-between bg-white relative">
                    <div className="flex flex-wrap gap-2 mb-2">
                         <span className="px-3 py-1.5 bg-yellow-100 text-yellow-700 rounded-lg text-xs font-bold flex items-center gap-1">⚡ High Energy</span>
                         <span className="px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg text-xs font-bold flex items-center gap-1">🤝 Social Butterfly</span>
                         <span className="px-3 py-1.5 bg-green-100 text-green-700 rounded-lg text-xs font-bold flex items-center gap-1">🧠 Smart</span>
                    </div>
                    <p className="text-gray-600 text-sm line-clamp-2 leading-relaxed">
                        {pet.description}
                    </p>
                    <div className="w-full flex justify-center mt-2">
                        <button className="text-gray-400 hover:text-gray-600 transition-colors">
                            <ChevronDown size={20} className="animate-bounce" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="absolute -bottom-8 left-0 right-0 flex justify-center items-center gap-6 z-20">
                <button onClick={handleNext} className="w-16 h-16 rounded-full bg-white shadow-xl text-red-500 hover:bg-red-50 hover:scale-110 transition-all duration-300 flex items-center justify-center border border-gray-100">
                    <X size={32} />
                </button>
                <button className="w-12 h-12 rounded-full bg-white shadow-lg text-blue-400 hover:bg-blue-50 hover:scale-110 transition-all duration-300 flex items-center justify-center border border-gray-100">
                    <Star size={24} />
                </button>
                <button onClick={handleNext} className="w-16 h-16 rounded-full bg-primary shadow-xl shadow-primary/40 text-white hover:bg-red-500 hover:scale-110 transition-all duration-300 flex items-center justify-center">
                    <Heart size={32} fill="currentColor" />
                </button>
            </div>
        </div>

        <p className="mt-16 text-gray-400 text-sm font-medium flex items-center gap-2">
            <span className="w-4 h-4 border border-gray-300 rounded flex items-center justify-center text-[10px]">←</span> 
            Pass <span className="mx-2">|</span> Like 
            <span className="w-4 h-4 border border-gray-300 rounded flex items-center justify-center text-[10px]">→</span>
        </p>
      </main>

       {/* Right Sidebar - Info */}
       <aside className="w-full md:w-1/4 hidden lg:block">
        <div className="flex flex-col gap-6 sticky top-24">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <h3 className="font-display font-bold text-lg text-gray-900 mb-4">About {pet.name}</h3>
                <div className="space-y-4">
                    <div className="flex items-start gap-3">
                        <div className="bg-purple-100 p-2 rounded-lg text-purple-600">
                            <Activity size={18} />
                        </div>
                        <div>
                            <p className="text-xs text-gray-500 font-bold uppercase tracking-wider">Activity Level</p>
                            <div className="w-full bg-gray-200 h-1.5 rounded-full mt-1.5 w-32">
                                <div className="bg-purple-500 h-1.5 rounded-full" style={{width: '85%'}}></div>
                            </div>
                            <p className="text-xs text-gray-900 mt-1 font-semibold">Very High</p>
                        </div>
                    </div>
                     <div className="flex items-start gap-3">
                        <div className="bg-orange-100 p-2 rounded-lg text-orange-600">
                            <Users size={18} />
                        </div>
                        <div>
                            <p className="text-xs text-gray-500 font-bold uppercase tracking-wider">Sociability</p>
                            <div className="w-full bg-gray-200 h-1.5 rounded-full mt-1.5 w-32">
                                <div className="bg-orange-500 h-1.5 rounded-full" style={{width: '95%'}}></div>
                            </div>
                            <p className="text-xs text-gray-900 mt-1 font-semibold">Loves Everyone</p>
                        </div>
                    </div>
                    <div className="border-t border-gray-100 pt-4 mt-2">
                        <p className="text-xs text-gray-500 font-bold uppercase tracking-wider mb-2">Vaccination Status</p>
                        <div className="flex items-center gap-2 text-green-600 text-sm font-bold">
                            <ShieldCheck size={18} /> Fully Vaccinated
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </aside>
    </div>
  );
};

export default Matching;