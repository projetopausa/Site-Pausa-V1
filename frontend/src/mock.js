// Mock data for Portal Pausa landing page - MANTIDO PARA COMPATIBILIDADE

// Função mock mantida para fallback e desenvolvimento
export const mockSubmitForm = async (formData) => {
  // Verifica se estamos em desenvolvimento e se a API não está disponível
  const isDevelopment = process.env.NODE_ENV === 'development';
  const API_URL = process.env.REACT_APP_API_URL;
  
  // Se tiver URL de API, não usa mock (a não ser que explicitamente solicitado)
  if (API_URL && !formData._useMock) {
    console.warn('mockSubmitForm chamado, mas REACT_APP_API_URL está definido. Use a API real.');
    return {
      success: false,
      message: 'Use a API real em vez do mock',
      detail: 'A variável REACT_APP_API_URL está definida no ambiente'
    };
  }
  
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock validation
  if (!formData.name || !formData.whatsapp) {
    throw new Error('Por favor, preencha todos os campos obrigatórios');
  }
  
  // Mock successful response
  return {
    success: true,
    message: 'Obrigada por se cadastrar! Entraremos em contato em breve.',
    contact_id: `mock_${Math.random().toString(36).substr(2, 9)}`,
    data: {
      id: Math.random().toString(36).substr(2, 9),
      ...formData,
      timestamp: new Date().toISOString()
    }
  };
};

// Função real para usar no ContactForm.jsx
export const submitContactForm = async (formData) => {
  const API_URL = process.env.REACT_APP_API_URL || 'https://portal-pausa-backend.onrender.com';
  
  try {
    const response = await fetch(`${API_URL}/api/contact`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData)
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Erro ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Erro ao enviar formulário:', error);
    
    // Fallback para mock em desenvolvimento se a API falhar
    if (process.env.NODE_ENV === 'development') {
      console.warn('API falhou, usando mock como fallback');
      return await mockSubmitForm({ ...formData, _useMock: true });
    }
    
    throw error;
  }
};

// Dados estáticos mantidos
export const heroData = {
  headline: "Você não precisa passar por isso sozinha.",
  subheadline: "O Portal Pausa é um abraço digital para mulheres na peri/menopausa. Cuidado inteligente que escuta, acolhe e guia - direto no seu WhatsApp.",
  ctaText: "Quero conhecer o GIS",
  heroImage: "https://images.unsplash.com/photo-1491438590914-bc09fcaaf77a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwyfHx3b21lbiUyMHRhbGtpbmd8ZW58MHx8fHwxNzY3ODY3MTU0fDA&ixlib=rb-4.1.0&q=85"
};

export const gisFeatures = [
  {
    id: 1,
    icon: "ear",
    title: "Falamos sua língua",
    description: "Conte seus sintomas no WhatsApp, como falaria com uma amiga. Nossa IA entende sua linguagem natural, sem termos médicos complicados."
  },
  {
    id: 2,
    icon: "users",
    title: "Cuidado que se adapta a você",
    description: "Receba micro-hábitos possíveis para seu dia a dia, baseados em evidências científicas. Pequenas ações, grandes mudanças."
  },
  {
    id: 3,
    icon: "trendingUp",
    title: "Seu bem-estar ajuda outras mulheres",
    description: "Seus relatos anônimos viram dados que ajudam a criar políticas públicas mais justas para todas."
  }
];

export const journeySteps = [
  {
    id: 1,
    icon: "messageSquare",
    title: "Você relata seus sintomas no WhatsApp"
  },
  {
    id: 2,
    icon: "heart",
    title: "Nossa IA analisa com empatia e ciência"
  },
  {
    id: 3,
    icon: "mail",
    title: "Você recebe orientações acolhedoras"
  },
  {
    id: 4,
    icon: "users",
    title: "Juntas, transformamos a saúde feminina"
  }
];

// Utilitário para testar conexão com a API
export const testAPIConnection = async () => {
  const API_URL = process.env.REACT_APP_API_URL || 'https://portal-pausa-backend.onrender.com';
  
  try {
    const startTime = Date.now();
    const response = await fetch(`${API_URL}/health`);
    const endTime = Date.now();
    
    const data = await response.json().catch(() => ({}));
    
    return {
      connected: response.ok,
      status: response.status,
      responseTime: endTime - startTime,
      data: data,
      url: API_URL
    };
  } catch (error) {
    return {
      connected: false,
      error: error.message,
      url: API_URL
    };
  }
};