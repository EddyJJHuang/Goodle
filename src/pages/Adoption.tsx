import React from 'react';
import { NavLink } from 'react-router-dom';
import { Search, MapPin, ArrowRight, Heart } from 'lucide-react';
import { mockPets } from '../services/mockData';

const Adoption = () => {
  const adoptablePets = mockPets.filter(p => p.status === 'Available');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-10 text-center md:text-left">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl mb-4">
            Find Your New Best Friend
        </h1>
        <p className="mt-2 text-lg text-gray-500 max-w-2xl">
            Browse through hundreds of loving pets waiting for their forever homes. Use the filters below to find the perfect match for your lifestyle.
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl shadow-sm p-6 mb-10 border border-gray-100">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-end">
              <div className="lg:col-span-4 w-full">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Search by Name or Keyword</label>
                  <div className="relative rounded-md shadow-sm">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <Search className="text-gray-400" size={18} />
                      </div>
                      <input type="text" className="focus:ring-primary focus:border-primary block w-full pl-10 sm:text-sm border-gray-300 rounded-xl py-3" placeholder="e.g. 'Golden Retriever' or 'Playful'" />
                  </div>
              </div>
              <div className="lg:col-span-8 flex flex-col sm:flex-row gap-4 w-full">
                   <div className="w-full sm:w-1/3">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Breed</label>
                        <select className="block w-full pl-3 pr-10 py-3 text-base border-gray-300 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-xl">
                            <option>Any Breed</option>
                            <option>Mixed Breed</option>
                            <option>Golden Retriever</option>
                            <option>Labrador</option>
                        </select>
                   </div>
                   <div className="w-full sm:w-1/3">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Age</label>
                        <select className="block w-full pl-3 pr-10 py-3 text-base border-gray-300 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-xl">
                            <option>Any Age</option>
                            <option>Puppy (0-1 yr)</option>
                            <option>Young (1-3 yrs)</option>
                            <option>Adult (3-8 yrs)</option>
                        </select>
                   </div>
                   <div className="w-full sm:w-auto sm:flex-shrink-0">
                        <label className="block text-sm font-medium text-transparent mb-2 select-none">Action</label>
                        <button className="w-full inline-flex items-center justify-center px-6 py-3 border border-transparent text-sm font-bold rounded-xl text-white bg-primary hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors shadow-lg shadow-primary/30">
                            Apply Filters
                        </button>
                   </div>
              </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider mr-2 py-1">Popular:</span>
              <button className="px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-xs font-semibold hover:bg-blue-200 transition-colors">House Trained</button>
              <button className="px-3 py-1 rounded-full bg-green-100 text-green-800 text-xs font-semibold hover:bg-green-200 transition-colors">Good with Kids</button>
              <button className="px-3 py-1 rounded-full bg-purple-100 text-purple-800 text-xs font-semibold hover:bg-purple-200 transition-colors">Special Needs</button>
          </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
        {adoptablePets.map((pet) => (
             <NavLink to={`/adoption/${pet.id}`} key={pet.id} className="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 flex flex-col h-full">
                <div className="relative h-64 overflow-hidden">
                    <img src={pet.image} alt={pet.name} className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500" />
                    <div className="absolute bottom-3 left-3">
                        <span className="px-2 py-1 bg-green-500 text-white text-xs font-bold rounded-md shadow-sm">Available</span>
                    </div>
                    <button className="absolute top-3 right-3 p-2 bg-white/50 backdrop-blur-sm rounded-full text-white hover:bg-red-500 hover:text-white transition-colors">
                        <Heart size={16} fill="currentColor" className="text-white hover:text-white"/>
                    </button>
                </div>
                <div className="p-5 flex flex-col flex-grow">
                    <div className="flex justify-between items-start mb-2">
                        <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary transition-colors">{pet.name}</h3>
                        <span className="text-xs font-semibold text-gray-500 bg-gray-100 px-2 py-1 rounded-md">{pet.breed}</span>
                    </div>
                    <div className="flex items-center gap-2 mb-3 text-xs text-gray-500 font-medium">
                        <span>{pet.age}</span> • <span>{pet.gender}</span>
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2 mb-4 flex-grow">
                        {pet.description}
                    </p>
                    <div className="flex flex-wrap gap-2 mb-4">
                        {pet.tags.slice(0, 2).map(tag => (
                             <span key={tag} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                                {tag}
                             </span>
                        ))}
                    </div>
                    <div className="mt-auto border-t border-gray-100 pt-4 flex items-center justify-between">
                        <div className="flex items-center text-xs text-gray-500">
                            <MapPin size={14} className="mr-1" />
                            {pet.location}
                        </div>
                        <span className="text-primary font-bold text-sm flex items-center gap-1 transition-colors group-hover:translate-x-1 duration-300">
                            Details <ArrowRight size={14} />
                        </span>
                    </div>
                </div>
             </NavLink>
        ))}

        {/* Promo Card */}
        <div className="bg-primary rounded-2xl overflow-hidden shadow-lg border border-primary flex flex-col h-full justify-center items-center text-center p-8 relative">
            <div className="absolute inset-0 bg-black/10"></div>
            <div className="relative z-10">
                <Heart size={64} className="text-white mb-4 mx-auto" />
                <h3 className="text-2xl font-bold text-white mb-2">Can't Adopt?</h3>
                <p className="text-white/90 mb-6">You can still help! Foster a pet or donate to support our local shelters.</p>
                <button className="bg-white text-primary font-bold py-3 px-6 rounded-xl hover:bg-gray-50 shadow-md transition-all transform hover:-translate-y-1">
                    Learn How to Help
                </button>
            </div>
        </div>
      </div>
    </div>
  );
};

export default Adoption;