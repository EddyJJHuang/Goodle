import React from 'react';
import { useParams } from 'react-router-dom';
import { Heart, Share, MapPin, CheckCircle, Activity, Shield, Calendar, MessageCircle, Info } from 'lucide-react';
import { mockPets } from '../services/mockData';

const PetDetails = () => {
  const { id } = useParams<{ id: string }>();
  // Fallback to first pet if not found for demo purposes
  const pet = mockPets.find(p => p.id === id) || mockPets[0];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
       {/* Breadcrumb would go here */}
       
       <div className="lg:grid lg:grid-cols-2 lg:gap-x-12 lg:items-start">
           {/* Image Gallery */}
           <div className="flex flex-col gap-4">
               <div className="aspect-w-4 aspect-h-3 w-full rounded-2xl overflow-hidden shadow-lg bg-gray-100 relative group">
                   <img src={pet.image} alt={pet.name} className="w-full h-full object-cover transform transition-transform duration-500 hover:scale-105" />
                   <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-bold text-primary shadow-sm">
                        Available for Adoption
                   </div>
               </div>
               <div className="grid grid-cols-4 gap-3">
                   {pet.images.concat([pet.image, pet.image, pet.image]).slice(0, 4).map((img, idx) => (
                       <button key={idx} className={`relative aspect-square rounded-lg overflow-hidden ${idx === 0 ? 'ring-2 ring-primary ring-offset-2' : 'hover:opacity-75 transition-opacity'}`}>
                           <img src={img} alt={`Thumbnail ${idx}`} className="w-full h-full object-cover" />
                       </button>
                   ))}
               </div>
           </div>

           {/* Info */}
           <div className="mt-10 px-2 sm:px-0 sm:mt-16 lg:mt-0">
               <div className="mb-8 border-b border-gray-200 pb-8">
                   <div className="flex justify-between items-start">
                       <div>
                           <h1 className="text-4xl font-extrabold tracking-tight text-gray-900">{pet.name}</h1>
                           <p className="mt-2 text-lg text-primary font-medium">{pet.breed}</p>
                       </div>
                       <div className="flex space-x-2">
                           <button className="p-2 rounded-full bg-gray-100 text-gray-400 hover:text-red-500 transition-colors">
                               <Heart size={24} />
                           </button>
                           <button className="p-2 rounded-full bg-gray-100 text-gray-400 hover:text-blue-500 transition-colors">
                               <Share size={24} />
                           </button>
                       </div>
                   </div>

                   <div className="mt-6 grid grid-cols-3 gap-4">
                        <div className="bg-white border border-gray-200 rounded-xl p-4 text-center shadow-sm">
                            <span className="block text-xs font-semibold text-gray-500 uppercase tracking-wide">Age</span>
                            <span className="block mt-1 text-xl font-bold text-gray-900">{pet.age}</span>
                        </div>
                        <div className="bg-white border border-gray-200 rounded-xl p-4 text-center shadow-sm">
                            <span className="block text-xs font-semibold text-gray-500 uppercase tracking-wide">Gender</span>
                            <span className="block mt-1 text-xl font-bold text-gray-900">{pet.gender}</span>
                        </div>
                         <div className="bg-white border border-gray-200 rounded-xl p-4 text-center shadow-sm">
                            <span className="block text-xs font-semibold text-gray-500 uppercase tracking-wide">Size</span>
                            <span className="block mt-1 text-xl font-bold text-gray-900">Medium</span>
                        </div>
                   </div>
               </div>

               <div className="mb-8">
                   <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                       <Info className="text-primary" size={24} /> About Me
                   </h3>
                   <div className="prose prose-sm text-gray-600">
                       <p>{pet.description}</p>
                       <p className="mt-2">He was rescued from a busy street but has adapted wonderfully to indoor life. He is incredibly friendly, loves belly rubs, and gets along well with other dogs.</p>
                   </div>
                   <div className="flex flex-wrap gap-2 mt-4">
                        {pet.health?.vaccinated && (
                             <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                <CheckCircle size={14} className="mr-1"/> Fully Vaccinated
                             </span>
                        )}
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            <Shield size={14} className="mr-1"/> Microchipped
                        </span>
                        {pet.tags.map(tag => (
                             <span key={tag} className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                <Activity size={14} className="mr-1"/> {tag}
                             </span>
                        ))}
                   </div>
               </div>

               <div className="mb-8 p-5 bg-orange-50 border border-orange-100 rounded-xl">
                   <h3 className="text-lg font-bold text-orange-800 mb-3 flex items-center gap-2">
                       <Shield size={20} /> Adoption Requirements
                   </h3>
                   <ul className="list-disc list-inside text-sm text-gray-700 space-y-1 ml-1">
                       <li>Must have a fenced yard</li>
                       <li>Experience with active breeds preferred</li>
                       <li>Commitment to daily exercise (1hr+)</li>
                   </ul>
               </div>

               <div className="flex flex-col gap-4 pt-6 border-t border-gray-200">
                   <div className="flex items-center justify-between mb-2">
                       <div className="flex items-center gap-3">
                           <img src={pet.ownerImage} alt="Owner" className="w-10 h-10 rounded-full object-cover ring-2 ring-white shadow-sm" />
                           <div>
                               <p className="text-sm font-semibold text-gray-900">{pet.ownerName || 'Goodle Shelter'}</p>
                               <p className="text-xs text-gray-500">Current Caretaker</p>
                           </div>
                       </div>
                       <div className="text-xs text-gray-400 flex items-center gap-1">
                           <MapPin size={14} /> {pet.location}
                       </div>
                   </div>
                   <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                       <button className="flex-1 bg-primary hover:bg-orange-600 text-white font-bold py-3 px-6 rounded-xl shadow-md transition transform active:scale-95 flex items-center justify-center gap-2">
                           <MessageCircle size={20} /> Contact Owner
                       </button>
                       <button className="flex-1 bg-white border-2 border-primary text-primary hover:bg-orange-50 font-bold py-3 px-6 rounded-xl transition transform active:scale-95 flex items-center justify-center gap-2">
                           <Calendar size={20} /> Meet & Greet
                       </button>
                   </div>
               </div>
           </div>
       </div>
    </div>
  );
};

export default PetDetails;