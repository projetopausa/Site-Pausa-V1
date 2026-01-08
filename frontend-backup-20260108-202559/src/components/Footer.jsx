import React from 'react';
import { Heart } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-purple-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-3 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Heart className="w-6 h-6 text-pink-400" />
              <span className="text-xl font-semibold">Portal Pausa</span>
            </div>
            <p className="text-purple-200 text-sm leading-relaxed">
              Cuidado inteligente e empático para mulheres na peri/menopausa. 
              Tecnologia com coração.
            </p>
          </div>

          {/* Links */}
          <div className="space-y-4">
            <h3 className="font-semibold text-lg">Legal</h3>
            <div className="space-y-2">
              <a
                href="#privacidade"
                className="block text-purple-200 hover:text-white transition-colors text-sm"
              >
                Política de Privacidade
              </a>
              <a
                href="#termos"
                className="block text-purple-200 hover:text-white transition-colors text-sm"
              >
                Termos de Uso
              </a>
            </div>
          </div>

          {/* Contact info */}
          <div className="space-y-4">
            <h3 className="font-semibold text-lg">Contato</h3>
            <div className="space-y-2 text-sm text-purple-200">
              <p>Fale conosco via WhatsApp:</p>
              <a
                href="https://wa.me/5511965970387"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors font-medium"
              >
                (11) 96597-0387
              </a>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-8 pt-8 border-t border-purple-800 text-center text-sm text-purple-300">
          <p>© 2025 Portal Pausa. Feito com 💜 para mulheres incríveis.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
