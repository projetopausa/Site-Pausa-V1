import React, { useState } from 'react';
import { Heart, Lock, Loader2, ExternalLink } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Checkbox } from './ui/checkbox';
import { toast } from 'sonner';

const ContactForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    whatsapp: '',
    acceptCommunication: false
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [contactId, setContactId] = useState(null);

  // URL da sua API no Render - use variável de ambiente
  const API_URL = process.env.REACT_APP_API_URL || 'https://portal-pausa-backend.onrender.com';

  const formatPhoneNumber = (value) => {
    // Remove tudo que não é número
    const numbers = value.replace(/\D/g, '');
    
    // Formata: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
    if (numbers.length <= 2) {
      return numbers;
    } else if (numbers.length <= 7) {
      return `(${numbers.slice(0, 2)}) ${numbers.slice(2)}`;
    } else if (numbers.length <= 11) {
      return `(${numbers.slice(0, 2)}) ${numbers.slice(2, 7)}-${numbers.slice(7)}`;
    } else {
      return `(${numbers.slice(0, 2)}) ${numbers.slice(2, 7)}-${numbers.slice(7, 11)}`;
    }
  };

  const validatePhone = (phone) => {
    const numbers = phone.replace(/\D/g, '');
    // Valida se tem 10 ou 11 dígitos (DDD + número)
    return numbers.length === 10 || numbers.length === 11;
  };

  const handlePhoneChange = (e) => {
    const formatted = formatPhoneNumber(e.target.value);
    setFormData({ ...formData, whatsapp: formatted });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validações
    if (!formData.name.trim()) {
      toast.error('Por favor, nos diga como gostaria de ser chamada');
      return;
    }

    if (!formData.whatsapp.trim()) {
      toast.error('Por favor, informe seu WhatsApp para contato');
      return;
    }

    if (!validatePhone(formData.whatsapp)) {
      toast.error('Parece que esse número não está completo. Verifique o formato: (XX) XXXXX-XXXX');
      return;
    }

    setIsSubmitting(true);

    try {
      console.log(`Enviando para: ${API_URL}/api/contact`);
      
      const response = await fetch(`${API_URL}/api/contact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name.trim(),
          whatsapp: formData.whatsapp,
          acceptCommunication: formData.acceptCommunication
        })
      });

      console.log('Status da resposta:', response.status);
      
      const result = await response.json();
      console.log('Resposta da API:', result);

      if (response.ok && result.success) {
        setIsSubmitted(true);
        setContactId(result.contact_id);
        
        toast.success(result.message || 'Recebemos seu interesse! Em breve entraremos em contato via WhatsApp 💜', {
          duration: 5000,
          icon: '🎉'
        });
        
        // Reset form after 5 seconds
        setTimeout(() => {
          setFormData({ name: '', whatsapp: '', acceptCommunication: false });
          setIsSubmitted(false);
          setContactId(null);
        }, 5000);
        
      } else {
        // Erro da API
        const errorMsg = result.detail || result.message || 'Erro ao processar seu cadastro.';
        toast.error(`Ops! ${errorMsg}`, {
          duration: 4000
        });
      }
      
    } catch (error) {
      console.error('Erro na requisição:', error);
      
      // Diferentes tipos de erro
      if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
        toast.error('Não foi possível conectar ao servidor. Verifique sua conexão ou tente novamente mais tarde.', {
          duration: 5000,
          icon: '📡'
        });
      } else {
        toast.error('Vamos tentar de novo, está tudo bem. Por favor, tente novamente.', {
          duration: 4000
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section id="contato" className="py-20 bg-gradient-to-br from-purple-100 via-pink-50 to-purple-100 relative overflow-hidden">
      {/* Floating shapes */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-10 right-10 w-40 h-40 bg-purple-300/20 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-20 left-10 w-48 h-48 bg-pink-300/20 rounded-full blur-3xl animate-float-delayed"></div>
      </div>

      <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl p-8 sm:p-12 border border-purple-200">
          {/* Header */}
          <div className="text-center mb-8 animate-fade-in">
            <h2 className="text-3xl sm:text-4xl font-semibold text-purple-900 mb-4">
              A revolução na saúde feminina começa com uma conversa.
            </h2>
            <p className="text-lg text-purple-700/70">
              Participe do nosso piloto e seja uma das primeiras a experimentar o cuidado que realmente escuta.
            </p>
            
            {/* Debug info - só aparece em desenvolvimento */}
            {process.env.NODE_ENV === 'development' && (
              <div className="mt-4 p-3 bg-purple-50 rounded-lg text-sm text-purple-700">
                <div className="flex items-center justify-between">
                  <span>API: <code className="bg-purple-100 px-2 py-1 rounded">{API_URL}</code></span>
                  <a 
                    href={`${API_URL}/api/test-db`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center text-purple-600 hover:text-purple-800"
                  >
                    Testar conexão <ExternalLink className="w-3 h-3 ml-1" />
                  </a>
                </div>
              </div>
            )}
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6 animate-slide-up">
            {/* Name field */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-purple-900 mb-2">
                Como gostaria de ser chamada? *
              </label>
              <Input
                id="name"
                type="text"
                placeholder="Seu nome ou como gostaria de ser chamada"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border-purple-200 focus:border-purple-500 focus:ring-purple-500"
                disabled={isSubmitting || isSubmitted}
                required
              />
            </div>

            {/* WhatsApp field */}
            <div>
              <label htmlFor="whatsapp" className="block text-sm font-medium text-purple-900 mb-2">
                Seu WhatsApp para contato *
              </label>
              <Input
                id="whatsapp"
                type="tel"
                placeholder="(11) 98765-4321"
                value={formData.whatsapp}
                onChange={handlePhoneChange}
                className="w-full px-4 py-3 rounded-xl border-purple-200 focus:border-purple-500 focus:ring-purple-500"
                disabled={isSubmitting || isSubmitted}
                required
              />
              <p className="mt-1 text-xs text-purple-600">
                Formato: (DDD) 9XXXX-XXXX
              </p>
            </div>

            {/* Checkbox */}
            <div className="flex items-start space-x-3 p-3 bg-purple-50 rounded-lg">
              <Checkbox
                id="communication"
                checked={formData.acceptCommunication}
                onCheckedChange={(checked) => 
                  setFormData({ ...formData, acceptCommunication: checked })
                }
                disabled={isSubmitting || isSubmitted}
                className="mt-1"
              />
              <label
                htmlFor="communication"
                className="text-sm text-purple-700 cursor-pointer leading-relaxed"
              >
                Quero receber informações sobre saúde feminina e novidades do Portal Pausa.
                <span className="block text-xs text-purple-500 mt-1">
                  (Opcional) Podemos enviar conteúdos exclusivos sobre bem-estar na menopausa.
                </span>
              </label>
            </div>

            {/* Submit button */}
            <Button
              type="submit"
              disabled={isSubmitting || isSubmitted}
              className="w-full py-6 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium text-lg transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 relative overflow-hidden group"
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center space-x-2">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Enviando para nossa comunidade...</span>
                </span>
              ) : isSubmitted ? (
                <span className="flex items-center justify-center space-x-2">
                  <Heart className="w-5 h-5 animate-pulse" fill="currentColor" />
                  <span>Cadastro realizado com sucesso! 💜</span>
                </span>
              ) : (
                <span className="flex items-center justify-center space-x-2">
                  <span>Quero fazer parte desta comunidade</span>
                  <Heart className="w-5 h-5 group-hover:scale-110 transition-transform" />
                </span>
              )}
            </Button>

            {/* Mensagem de confirmação */}
            {isSubmitted && contactId && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-xl text-center animate-pulse">
                <p className="text-green-800 font-medium">
                  ✅ Cadastro #{contactId.substring(0, 8)} realizado!
                </p>
                <p className="text-green-600 text-sm mt-1">
                  Em breve você receberá uma mensagem nossa no WhatsApp.
                </p>
              </div>
            )}

            {/* Trust badge */}
            <div className="flex flex-col items-center justify-center space-y-2 text-sm text-purple-700/70 pt-4 border-t border-purple-100">
              <div className="flex items-center space-x-2">
                <Lock className="w-4 h-4" />
                <span>Seus dados estão seguros conosco</span>
              </div>
              <p className="text-xs text-center max-w-md">
                Utilizamos seu contato apenas para comunicação sobre o projeto Portal Pausa. 
                Não compartilhamos seus dados com terceiros.
              </p>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
};

export default ContactForm;