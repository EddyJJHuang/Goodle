import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { PawPrint, Menu, X, Bell, User } from 'lucide-react';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-2 rounded-md text-sm font-bold transition-colors duration-200 ${
      isActive
        ? 'text-primary bg-orange-50'
        : 'text-gray-600 hover:text-primary hover:bg-gray-50'
    }`;

  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <NavLink to="/" className="flex-shrink-0 flex items-center gap-2 cursor-pointer">
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-orange-400 rounded-full flex items-center justify-center text-white shadow-lg transform -rotate-6">
                <PawPrint size={24} fill="currentColor" />
              </div>
              <span className="font-display text-2xl font-bold text-gray-900 tracking-tight">
                Goodle
              </span>
            </NavLink>
            <div className="hidden md:ml-10 md:flex md:space-x-4">
              <NavLink to="/match" className={navLinkClass}>Pet Matching</NavLink>
              <NavLink to="/lost-found" className={navLinkClass}>Lost & Found</NavLink>
              <NavLink to="/adoption" className={navLinkClass}>Adoption Square</NavLink>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <button className="hidden sm:flex items-center gap-2 bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded-full shadow-md transition-all transform hover:-translate-y-0.5 text-sm font-bold">
              <NavLink to="/post">New Post</NavLink>
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100">
              <Bell size={20} />
            </button>
            <div className="hidden sm:flex items-center gap-3 pl-4 border-l border-gray-200">
               <div className="text-right hidden lg:block">
                <p className="text-sm font-bold text-gray-900">Alex J.</p>
                <p className="text-xs text-gray-500">My Dog: Bella</p>
              </div>
              <div className="h-10 w-10 rounded-full bg-gray-200 overflow-hidden border-2 border-primary cursor-pointer">
                <img src="https://i.pravatar.cc/150?u=alex" alt="User" className="h-full w-full object-cover" />
              </div>
            </div>
            <div className="-mr-2 flex md:hidden">
              <button
                onClick={() => setIsOpen(!isOpen)}
                className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none"
              >
                {isOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isOpen && (
        <div className="md:hidden bg-white border-b border-gray-100">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <NavLink to="/match" onClick={() => setIsOpen(false)} className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary hover:bg-gray-50">Pet Matching</NavLink>
            <NavLink to="/lost-found" onClick={() => setIsOpen(false)} className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary hover:bg-gray-50">Lost & Found</NavLink>
            <NavLink to="/adoption" onClick={() => setIsOpen(false)} className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary hover:bg-gray-50">Adoption Square</NavLink>
             <NavLink to="/post" onClick={() => setIsOpen(false)} className="block px-3 py-2 rounded-md text-base font-medium text-primary bg-orange-50">Post New Pet</NavLink>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;