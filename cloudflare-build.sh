#!/bin/bash

# Força Node.js 18
export NODE_VERSION=18.20.4

echo "🚀 Iniciando build do Portal Pausa..."
echo "Node.js versão: $(node --version)"
echo "npm versão: $(npm --version)"

# Vai para frontend
cd frontend

# Limpa cache se necessário
rm -rf node_modules/.cache

# Instala dependências
echo "📦 Instalando dependências..."
npm install --legacy-peer-deps --no-audit --progress=false

# Build
echo "🔨 Fazendo build..."
CI=false npm run build

# Verifica se build foi criado
if [ -d "build" ]; then
    echo "✅ Build criado com sucesso!"
    echo "📁 Tamanho do build: $(du -sh build)"
else
    echo "❌ ERRO: Pasta build não foi criada!"
    exit 1
fi