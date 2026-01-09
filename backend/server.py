import os
import logging
import uuid
import httpx
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict

# 1. Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PortalPausa")

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# URL do Google Script
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwLndrbygG7Je7C7htmrf_9AMCwgKy6sXRuckAW6RVUXv1hQwlQbIWwjpKDe1xZkkrc/exec"

app = FastAPI(title="Portal Pausa API", version="1.0.0")

# 2. Configuração do CORS (CRUCIAL: Isso deve lidar com o OPTIONS automaticamente)
origins = [
    "*", # Para testes, permite tudo. Em produção, coloque a URL exata do seu site (ex: https://meusite.com)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)

# 3. Middleware de Log Customizado
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"📥 [{request_id}] {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        logger.info(f"📤 [{request_id}] Status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"💥 [{request_id}] Erro: {str(e)}")
        raise

# 4. Modelos Pydantic
class ContactForm(BaseModel):
    name: str = Field(..., min_length=2)
    whatsapp: str
    acceptCommunication: bool = False

class ContactResponse(BaseModel):
    success: bool
    message: str
    contact_id: Optional[str] = None

# 5. Router
api_router = APIRouter(prefix="/api")

@app.get("/")
async def root():
    return {"status": "online", "service": "Portal Pausa Backend"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Rota POST Principal
@api_router.post("/contact", response_model=ContactResponse)
async def submit_contact_form(contact: ContactForm):
    logger.info(f"📝 Processando contato: {contact.name}")
    
    # Validação simples
    whatsapp_clean = ''.join(filter(str.isdigit, contact.whatsapp))
    if len(whatsapp_clean) < 10:
        return ContactResponse(success=False, message="WhatsApp inválido.")

    # Preparar payload para o Google
    payload = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "name": contact.name,
        "whatsapp": contact.whatsapp,
        "whatsapp_clean": whatsapp_clean,
        "acceptCommunication": "Sim" if contact.acceptCommunication else "Não",
        "source": "portal_pausa_backend"
    }

    # Enviar para o Google Apps Script
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # follow_redirects=True é OBRIGATÓRIO para Google Scripts
            response = await client.post(
                GOOGLE_SCRIPT_URL,
                json=payload,
                follow_redirects=True 
            )
            
        if response.status_code == 200:
            return ContactResponse(
                success=True, 
                message="Recebemos seu contato!", 
                contact_id=payload['id']
            )
        else:
            logger.error(f"Google Error: {response.text}")
            return ContactResponse(success=False, message="Erro ao salvar no Google Sheets.")

    except Exception as e:
        logger.error(f"Erro interno: {e}")
        return ContactResponse(success=False, message="Erro interno do servidor.")

# Registrar rotas
app.include_router(api_router)