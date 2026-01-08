import React from 'react';
import { MessageSquare, Heart, Mail, Users } from 'lucide-react';
import { journeySteps } from '../mock';

const iconMap = {
  messageSquare: MessageSquare,
  heart: Heart,
  mail: Mail,
  users: Users
};

const JourneySection = () => {
  return (
    <section id="como-funciona" className="py-20 bg-gradient-to-b from-slate-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="text-3xl sm:text-4xl font-semibold text-purple-900 mb-4">
            Como funciona?
          </h2>
          <p className="text-lg text-purple-700/70 max-w-2xl mx-auto">
            Uma jornada simples de cuidado e transformação
          </p>
        </div>

        {/* Journey timeline */}
        <div className="relative">
          {/* Timeline line - hidden on mobile */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-purple-200 -translate-y-1/2"></div>

          {/* Steps */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-4">
            {journeySteps.map((step, index) => {
              const Icon = iconMap[step.icon];
              return (
                <div
                  key={step.id}
                  className="relative animate-slide-up"
                  style={{ animationDelay: `${index * 150}ms` }}
                >
                  {/* Step card */}
                  <div className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all duration-300 border border-purple-100">
                    {/* Step number */}
                    <div className="absolute -top-4 -left-4 w-10 h-10 bg-purple-600 text-white rounded-full flex items-center justify-center font-semibold shadow-lg">
                      {step.id}
                    </div>

                    {/* Icon circle */}
                    <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4 mx-auto">
                      <Icon className="w-8 h-8 text-purple-600" />
                    </div>

                    {/* Content */}
                    <p className="text-purple-900 font-medium text-center leading-snug">
                      {step.title}
                    </p>
                  </div>

                  {/* Dotted connector for mobile/tablet */}
                  {index < journeySteps.length - 1 && (
                    <div className="lg:hidden flex justify-center py-4">
                      <div className="w-0.5 h-8 border-l-2 border-dashed border-purple-300"></div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Bottom message */}
        <div className="mt-16 text-center animate-fade-in-delayed">
          <p className="text-purple-800 text-lg font-medium">
            A revolução na saúde feminina começa com uma conversa.
          </p>
        </div>
      </div>
    </section>
  );
};

export default JourneySection;
