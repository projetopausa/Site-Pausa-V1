// Mock data for Portal Pausa landing page

export const mockSubmitForm = async (formData) => {
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
    data: {
      id: Math.random().toString(36).substr(2, 9),
      ...formData,
      timestamp: new Date().toISOString()
    }
  };
};

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
