import React from 'react';
import { Heart } from 'lucide-react';
import { heroData } from '../mock';

const HeroSection = () => {
  const scrollToContact = () => {
    const element = document.getElementById('contato');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <section className="relative min-h-screen flex items-center overflow-hidden bg-gradient-to-br from-purple-50 via-pink-50 to-purple-50">
      {/* Floating shapes */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-32 h-32 bg-purple-200/30 rounded-full blur-3xl animate-float"></div>
        <div className="absolute top-40 right-20 w-48 h-48 bg-pink-200/30 rounded-full blur-3xl animate-float-delayed"></div>
        <div className="absolute bottom-20 left-1/4 w-40 h-40 bg-purple-300/20 rounded-full blur-3xl animate-float"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div className="text-left space-y-8 animate-fade-in">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-semibold text-purple-900 leading-tight">
              {heroData.headline}
            </h1>
            
            <p className="text-lg sm:text-xl text-purple-800/80 leading-relaxed">
              {heroData.subheadline}
            </p>

            <button
              onClick={scrollToContact}
              className="group inline-flex items-center space-x-2 px-8 py-4 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl"
            >
              <span className="font-medium">{heroData.ctaText}</span>
              <Heart className="w-5 h-5 group-hover:animate-pulse" />
            </button>

            {/* Trust badge */}
            <div className="flex items-center space-x-2 text-sm text-purple-700/70">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>Cuidado digital baseado em evidências científicas</span>
            </div>
          </div>

          {/* Image */}
          <div className="relative animate-fade-in-delayed">
            <div className="relative rounded-3xl overflow-hidden shadow-2xl">
              <img
                src={heroData.heroImage}
                alt="Mulheres conversando e se apoiando"
                className="w-full h-auto object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-purple-900/20 to-transparent"></div>
            </div>
            
            {/* Floating card */}
            <div className="absolute -bottom-6 -left-6 bg-white rounded-2xl p-4 shadow-xl animate-float max-w-xs">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                  <Heart className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-purple-900">Apoio contínuo</p>
                  <p className="text-xs text-purple-600">24/7 via WhatsApp</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
