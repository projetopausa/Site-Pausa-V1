# Portal Pausa - Product Requirements Document

## Problema Original
Criar landing page empática para apresentar o Portal Pausa - plataforma de cuidado digital para mulheres na peri/menopausa, com foco em comunicação empática + saúde digital.

## Escolhas do Usuário
1. **Backend**: MongoDB completo para salvar leads
2. **Imagens**: Combinação de ícones lucide-react + imagens reais
3. **WhatsApp**: Integração real (+55 11 965970387)
4. **Validação**: Campos obrigatórios + formato telefone brasileiro
5. **Estrutura**: 4 seções + footer (privacidade, termos)

## Personas
- **Mulheres na peri/menopausa**: 40-55 anos, buscam apoio e informação
- **Participantes do piloto**: Interessadas em soluções digitais de saúde

## Requisitos Core
### Frontend
- ✅ Hero Section com imagem e CTA
- ✅ Seção GIS Features (3 cards)
- ✅ Seção Journey (4 passos)
- ✅ Formulário de contato (nome + WhatsApp)
- ✅ Footer com links legais
- ✅ Navegação fixa com menu responsivo
- ✅ Animações delicadas (float, fade-in, slide-up)
- ✅ Design empático (roxo #7C3AED, rosa #F472B6, verde #10B981)

### Backend (Pendente)
- ⏳ Modelo MongoDB para leads
- ⏳ Endpoint POST /api/leads
- ⏳ Validação server-side
- ⏳ Integração WhatsApp

## Arquitetura
**Tech Stack**: React + FastAPI + MongoDB
**Componentes Shadcn**: Button, Input, Checkbox, Sonner (toast)
**Imagens**: Unsplash (hero + wellness)

## Implementado (08/01/2025)
### ✅ Frontend com Mock Data
- `/app/frontend/src/pages/LandingPage.jsx` - Página principal
- `/app/frontend/src/components/HeroSection.jsx` - Hero empático
- `/app/frontend/src/components/GisFeatures.jsx` - Cards de features
- `/app/frontend/src/components/JourneySection.jsx` - Timeline de jornada
- `/app/frontend/src/components/ContactForm.jsx` - Formulário com validação
- `/app/frontend/src/components/Footer.jsx` - Footer com WhatsApp
- `/app/frontend/src/mock.js` - Dados mockados
- `/app/frontend/src/App.css` - Animações customizadas

### ✅ Migração CRA → Vite (08/01/2025)
**Stack Modernizada:**
- ✅ Vite 7.3.1 (antes: CRA/Webpack 4)
- ✅ React 19.2.3 (antes: 19.0.0)
- ✅ React Router 7.12.0 (antes: 7.5.1)
- ✅ Node.js dependencies atualizadas
- ✅ ESM modules nativos
- ✅ Hot Module Replacement (HMR) ultra-rápido

**Resultados da Migração:**
- ⚡ Build time: 90s → 5.2s (94% mais rápido!)
- 📦 Bundle size: 396KB total (otimizado)
- 🚀 Dev server start: <1s (antes: ~15s)
- ✅ Zero erros de dependência
- ✅ Configurações modernas (vite.config.js, postcss, tailwind)

**Arquivos Criados/Atualizados:**
- `/app/frontend/vite.config.js` - Config Vite com proxy e otimizações
- `/app/frontend/tailwind.config.js` - Tailwind otimizado
- `/app/frontend/postcss.config.js` - PostCSS config
- `/app/frontend/src/main.jsx` - Entry point Vite
- `/app/frontend/src/lib/utils.js` - Utilities (cn helper)
- `/app/frontend/.env.development` - Env vars dev
- `/app/frontend/.env.production` - Env vars prod
- `/app/frontend/package.json` - Scripts atualizados

## Backlog Priorizado
### P0 - Próxima Sprint
1. Implementar backend MongoDB para salvar leads
2. Criar endpoint POST /api/leads
3. Conectar formulário ao backend real
4. Testar fluxo completo end-to-end

### P1 - Features Futuras
1. Páginas de Privacidade e Termos de Uso
2. Analytics (tracking de conversões)
3. Email de confirmação após cadastro
4. Dashboard admin para visualizar leads

### P2 - Melhorias
1. Testes automatizados
2. SEO otimizado
3. Performance (lazy loading de imagens)
4. Modo escuro

## Contratos de API (Planejado)
```
POST /api/leads
Request: {
  "name": "string",
  "whatsapp": "string (formato: (XX) XXXXX-XXXX)",
  "acceptCommunication": boolean
}
Response: {
  "success": true,
  "message": "Lead cadastrado com sucesso",
  "data": {
    "id": "string",
    "name": "string",
    "whatsapp": "string",
    "acceptCommunication": boolean,
    "createdAt": "ISO date"
  }
}
```

## Próximos Passos
1. ✅ Entregar frontend funcional com mock
2. ⏳ Desenvolver backend MongoDB
3. ⏳ Integrar frontend + backend
4. ⏳ Testar com testing_agent_v3
5. ⏳ Deploy
