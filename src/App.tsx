import React from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Matching from './pages/Matching';
import LostFound from './pages/LostFound';
import Adoption from './pages/Adoption';
import PetDetails from './pages/PetDetails';
import PostPet from './pages/PostPet';

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen flex flex-col bg-gray-50 font-body">
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/match" element={<Matching />} />
            <Route path="/lost-found" element={<LostFound />} />
            <Route path="/adoption" element={<Adoption />} />
            <Route path="/adoption/:id" element={<PetDetails />} />
            <Route path="/post" element={<PostPet />} />
          </Routes>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;