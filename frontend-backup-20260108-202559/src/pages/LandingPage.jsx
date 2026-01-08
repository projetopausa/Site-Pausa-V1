import React, { useState } from 'react';
import { Heart, Menu, X } from 'lucide-react';
import HeroSection from '../components/HeroSection';
import GisFeatures from '../components/GisFeatures';
import JourneySection from '../components/JourneySection';
import ContactForm from '../components/ContactForm';
import Footer from '../components/Footer';

const LandingPage = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setMenuOpen(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-purple-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <Heart className="w-6 h-6 text-purple-600" />
              <span className="text-xl font-semibold text-purple-900">Portal Pausa</span>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="lg:hidden p-2 rounded-lg hover:bg-purple-50 transition-colors"
            >
              {menuOpen ? (
                <X className="w-6 h-6 text-purple-900" />
              ) : (
                <Menu className="w-6 h-6 text-purple-900" />
              )}
            </button>

            {/* Desktop menu */}
            <div className="hidden lg:flex items-center space-x-8">
              <button
                onClick={() => scrollToSection('sobre')}
                className="text-purple-900 hover:text-purple-600 transition-colors text-sm font-medium"
              >
                Sobre o GIS
              </button>
              <button
                onClick={() => scrollToSection('como-funciona')}
                className="text-purple-900 hover:text-purple-600 transition-colors text-sm font-medium"
              >
                Como Funciona
              </button>
              <button
                onClick={() => scrollToSection('contato')}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
              >
                Participar
              </button>
            </div>
          </div>

          {/* Mobile menu */}
          {menuOpen && (
            <div className="lg:hidden py-4 space-y-3 border-t border-purple-100">
              <button
                onClick={() => scrollToSection('sobre')}
                className="block w-full text-left px-4 py-2 text-purple-900 hover:bg-purple-50 rounded-lg transition-colors text-sm font-medium"
              >
                Sobre o GIS
              </button>
              <button
                onClick={() => scrollToSection('como-funciona')}
                className="block w-full text-left px-4 py-2 text-purple-900 hover:bg-purple-50 rounded-lg transition-colors text-sm font-medium"
              >
                Como Funciona
              </button>
              <button
                onClick={() => scrollToSection('contato')}
                className="block w-full text-left px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
              >
                Participar
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* Main content */}
      <main className="pt-16">
        <HeroSection />
        <GisFeatures />
        <JourneySection />
        <ContactForm />
      </main>

      <Footer />
    </div>
  );
};

export default LandingPage;
