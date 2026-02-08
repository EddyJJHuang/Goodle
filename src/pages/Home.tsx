import React from 'react';
import { NavLink } from 'react-router-dom';
import { Heart, MapPin, Home as HomeIcon, Video, Shield, Wand2 } from 'lucide-react';

const Home = () => {
  return (
    <div className="flex-grow">
      <div className="relative bg-gradient-to-b from-orange-50 to-gray-50 py-12 sm:py-20 overflow-hidden">
        {/* Background blobs */}
        <div className="absolute top-0 left-0 -ml-20 -mt-20 w-64 h-64 bg-yellow-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-primary rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h1 className="text-4xl sm:text-6xl font-display font-extrabold text-gray-900 mb-6 leading-tight">
              Find Friends, <span className="text-primary">Find Home</span>, <br /> Find Love.
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              The all-in-one platform for pet lovers. Match your furry friend, report lost pets, or adopt a new family member today.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <NavLink to="/match" className="bg-primary text-white px-8 py-4 rounded-xl font-bold text-lg shadow-lg shadow-orange-500/30 hover:shadow-orange-500/50 hover:bg-orange-600 transition-all transform hover:-translate-y-1">
                Start Matching
              </NavLink>
              <NavLink to="/post" className="bg-white text-gray-800 px-8 py-4 rounded-xl font-bold text-lg shadow-md border border-gray-100 hover:border-primary/50 transition-all">
                Create Profile
              </NavLink>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <NavLink to="/match" className="group relative bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border border-gray-100 overflow-hidden cursor-pointer">
               <div className="absolute top-0 right-0 w-32 h-32 bg-red-100 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
               <div className="relative z-10">
                   <div className="w-14 h-14 bg-red-100 text-red-500 rounded-2xl flex items-center justify-center mb-6 group-hover:rotate-6 transition-transform">
                       <Heart size={28} fill="currentColor" />
                   </div>
                   <h3 className="text-2xl font-bold text-gray-900 mb-3">Pet Social</h3>
                   <p className="text-gray-500 mb-6">Swipe right to find playdates! AI-powered matching based on breed, energy level, and personality.</p>
               </div>
            </NavLink>

            {/* Feature 2 */}
            <NavLink to="/lost-found" className="group relative bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border border-gray-100 overflow-hidden cursor-pointer">
               <div className="absolute top-0 right-0 w-32 h-32 bg-blue-100 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
               <div className="relative z-10">
                   <div className="w-14 h-14 bg-blue-100 text-secondary rounded-2xl flex items-center justify-center mb-6 group-hover:rotate-6 transition-transform">
                       <MapPin size={28} />
                   </div>
                   <h3 className="text-2xl font-bold text-gray-900 mb-3">Lost & Found</h3>
                   <p className="text-gray-500 mb-6">Report lost pets or sightings. Integrated maps with red/blue markers for quick identification.</p>
               </div>
            </NavLink>

            {/* Feature 3 */}
            <NavLink to="/adoption" className="group relative bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border border-gray-100 overflow-hidden cursor-pointer">
               <div className="absolute top-0 right-0 w-32 h-32 bg-green-100 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
               <div className="relative z-10">
                   <div className="w-14 h-14 bg-green-100 text-green-600 rounded-2xl flex items-center justify-center mb-6 group-hover:rotate-6 transition-transform">
                       <HomeIcon size={28} />
                   </div>
                   <h3 className="text-2xl font-bold text-gray-900 mb-3">Adoption Square</h3>
                   <p className="text-gray-500 mb-6">Browse pets looking for a forever home. Filter by breed, age, and health status.</p>
               </div>
            </NavLink>
          </div>
        </div>
      </div>

      <section className="py-16 bg-white border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col lg:flex-row items-center gap-12">
                <div className="w-full lg:w-1/2">
                    <div className="bg-gray-50 rounded-3xl p-8 border border-gray-200 relative">
                        <div className="absolute top-0 left-0 w-full h-2 bg-primary rounded-t-3xl"></div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Pet Profile</h2>
                        <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center mb-6 bg-white cursor-pointer hover:bg-gray-50 transition-colors group">
                            <div className="w-12 h-12 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                                <Wand2 size={24} />
                            </div>
                            <p className="text-sm font-medium text-gray-700">Click to upload photos or drag and drop</p>
                            <p className="text-xs text-gray-400 mt-1">AI Analysis will auto-tag breed</p>
                        </div>
                    </div>
                </div>
                <div className="w-full lg:w-1/2">
                    <span className="text-primary font-bold tracking-wider uppercase text-sm">Easy Onboarding</span>
                    <h2 className="text-3xl sm:text-4xl font-display font-bold text-gray-900 mt-2 mb-6">
                        Let AI Help You Build<br/>The Perfect Profile
                    </h2>
                    <ul className="space-y-6">
                        <li className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-orange-100 text-primary flex items-center justify-center shrink-0">
                                <Wand2 size={20} />
                            </div>
                            <div>
                                <h4 className="font-bold text-gray-900 text-lg">AI Recognition</h4>
                                <p className="text-gray-600">Upload a photo and let our AI suggest the breed and color tags instantly.</p>
                            </div>
                        </li>
                         <li className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-blue-100 text-secondary flex items-center justify-center shrink-0">
                                <Video size={20} />
                            </div>
                            <div>
                                <h4 className="font-bold text-gray-900 text-lg">Video Moments</h4>
                                <p className="text-gray-600">Showcase your pet's personality with a 10s short video clip.</p>
                            </div>
                        </li>
                         <li className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-green-100 text-green-600 flex items-center justify-center shrink-0">
                                <Shield size={20} />
                            </div>
                            <div>
                                <h4 className="font-bold text-gray-900 text-lg">Privacy First</h4>
                                <p className="text-gray-600">You control what information is visible to the public.</p>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
      </section>

       <section className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-12">Trusted by Pet Owners Everywhere</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                <div className="p-4">
                    <div className="text-4xl font-extrabold text-primary mb-2">10k+</div>
                    <div className="text-gray-500 font-medium">Happy Matches</div>
                </div>
                <div className="p-4">
                    <div className="text-4xl font-extrabold text-secondary mb-2">500+</div>
                    <div className="text-gray-500 font-medium">Lost Pets Found</div>
                </div>
                <div className="p-4">
                    <div className="text-4xl font-extrabold text-green-500 mb-2">2k+</div>
                    <div className="text-gray-500 font-medium">Adoptions</div>
                </div>
                <div className="p-4">
                    <div className="text-4xl font-extrabold text-purple-500 mb-2">50k+</div>
                    <div className="text-gray-500 font-medium">Active Profiles</div>
                </div>
            </div>
        </div>
      </section>
    </div>
  );
};

export default Home;