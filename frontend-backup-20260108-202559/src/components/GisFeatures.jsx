import React from 'react';
import { Ear, Users, TrendingUp } from 'lucide-react';
import { gisFeatures } from '../mock';

const iconMap = {
  ear: Ear,
  users: Users,
  trendingUp: TrendingUp
};

const GisFeatures = () => {
  return (
    <section id="sobre" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="text-3xl sm:text-4xl font-semibold text-purple-900 mb-4">
            O que é o GIS?
          </h2>
          <p className="text-lg text-purple-700/70 max-w-2xl mx-auto">
            Um sistema de cuidado que entende, acolhe e transforma
          </p>
        </div>

        {/* Features grid */}
        <div className="grid md:grid-cols-3 gap-8">
          {gisFeatures.map((feature, index) => {
            const Icon = iconMap[feature.icon];
            return (
              <div
                key={feature.id}
                className="group bg-white rounded-2xl p-8 shadow-sm hover:shadow-xl transition-all duration-300 border border-purple-100 hover:border-purple-300 animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                {/* Icon */}
                <div className="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mb-6 group-hover:bg-purple-600 group-hover:scale-110 transition-all duration-300">
                  <Icon className="w-8 h-8 text-purple-600 group-hover:text-white transition-colors duration-300" />
                </div>

                {/* Content */}
                <h3 className="text-xl font-semibold text-purple-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-purple-700/70 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default GisFeatures;
