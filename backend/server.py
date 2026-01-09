from fastapi import FastAPI, APIRouter, HTTPException, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import httpx
from fastapi.responses import JSONResponse  # ADICIONE ESTA LINHA

# Configurar logging primeiro
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# URL do seu Google Apps Script Web App (COLE A NOVA URL AQUI DEPOIS DO DEPLOY CORRETO)
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwLndrbygG7Je7C7htmrf_9AMCwgKy6sXRuckAW6RVUXv1hQwlQbIWwjpKDe1xZkkrc/exec"
# Create the main app
app = FastAPI(
    title="Portal Pausa API",
    version="1.0.0",
    description="API Backend para o Portal Pausa - Saúde Feminina",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS PRIMEIRO, antes de criar o router
cors_origins = os.environ.get('CORS_ORIGINS', '*').split(',') if os.environ.get('CORS_ORIGINS', '*') != '*' else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # Cache de preflight por 10 minutos
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Modelo do formulário de contato
class ContactForm(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Como gostaria de ser chamada?")
    whatsapp: str = Field(..., description="WhatsApp para contato no formato (DDD) 9XXXX-XXXX")
    acceptCommunication: bool = Field(default=False, description="Aceita receber comunicações")

class ContactResponse(BaseModel):
    success: bool
    message: str
    contact_id: Optional[str] = None

# ========== ROTAS DO APP (sem prefixo) ==========
@app.get("/")
async def root():
    return {
        "message": "Portal Pausa API está funcionando!",
        "status": "online",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "api_docs": "/docs",
            "api_redoc": "/redoc",
            "health": "/health",
            "status": "/status",
            "api_root": "/api/",
            "api_health": "/api/health",
            "api_contact": "/api/contact"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint para monitoramento"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "Portal Pausa Backend",
        "environment": os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'local'),
        "version": "1.0.0",
        "database": "google_sheets"
    }

@app.get("/status")
async def status():
    """Endpoint simples de status"""
    return {
        "status": "online",
        "service": "Portal Pausa API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "documentation": "/docs"
    }

# ========== ROTAS DA API (com prefixo /api) ==========
@api_router.get("/")
async def api_root():
    return {
        "message": "Portal Pausa API",
        "version": "1.0.0",
        "endpoints": [
            "GET    /health",
            "GET    /status",
            "POST   /status",
            "POST   /contact"
        ]
    }

@api_router.get("/health")
async def api_health():
    """Health check específico da API"""
    return {
        "api": "running",
        "database": "google_sheets",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": "unknown"
    }

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    """Cria um novo registro de status check"""
    try:
        status_dict = input.model_dump()
        status_obj = StatusCheck(**status_dict)
        
        logger.info(f"✅ Status check recebido: {status_obj.client_name}")
        return status_obj
            
    except Exception as e:
        logger.error(f"❌ Erro em /status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)[:100]}")

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    """Retorna todos os status checks (simulado)"""
    try:
        return []
        
    except Exception as e:
        logger.error(f"❌ Erro em GET /status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)[:100]}")

# ADICIONE ESTA ROTA OPTIONS ESPECÍFICA
@api_router.options("/contact")
async def options_contact(request: Request):
    """Endpoint específico para requisições OPTIONS (preflight CORS)"""
    # Retorna uma resposta vazia com os headers CORS apropriados
    headers = {
        "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Max-Age": "600"  # 10 minutos
    }
    return JSONResponse(content={}, headers=headers)

@api_router.post("/contact", response_model=ContactResponse)
async def submit_contact_form(contact: ContactForm, request: Request):
    """Endpoint para receber formulário de contato e salvar no Google Sheets"""
    
    logger.info(f"📥 Recebendo contato de: {contact.name}")
    
    try:
        # Log dos dados recebidos
        logger.info(f"📋 Dados recebidos - Nome: {contact.name}, WhatsApp: {contact.whatsapp}, Aceita comunicação: {contact.acceptCommunication}")
        
        # Validação do WhatsApp
        whatsapp_clean = ''.join(filter(str.isdigit, contact.whatsapp))
        if len(whatsapp_clean) < 10:
            logger.warning(f"⚠️ WhatsApp inválido: {contact.whatsapp}")
            return ContactResponse(
                success=False,
                message="Por favor, insira um número de WhatsApp válido no formato (DDD) 9XXXX-XXXX.",
                contact_id=None
            )
        
        # Preparar os dados para enviar ao Google Sheets
        contact_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Dados que serão enviados para o Google Sheets
        sheet_data = {
            "id": contact_id,
            "timestamp": timestamp,
            "name": contact.name,
            "whatsapp": contact.whatsapp,
            "whatsapp_clean": whatsapp_clean,
            "acceptCommunication": "Sim" if contact.acceptCommunication else "Não",
            "source": "portal_pausa_website"
        }
        
        # Enviar dados para o Google Sheets via Google Apps Script
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GOOGLE_SCRIPT_URL,
                json=sheet_data,
                headers={"Content-Type": "application/json"},
                follow_redirects=True  # IMPORTANTE: Segue redirecionamentos
            )
        
        # Verificar a resposta do Google Apps Script
        if response.status_code == 200:
            try:
                response_data = response.json()
                
                if response_data.get("result") == "success":
                    logger.info(f"✅ Contato salvo no Google Sheets! ID: {contact_id}")
                    
                    return ContactResponse(
                        success=True, 
                        message="Obrigada por se cadastrar! Entraremos em contato em breve. 💜",
                        contact_id=contact_id
                    )
                else:
                    error_msg = response_data.get("error", "Erro desconhecido do Google Sheets")
                    logger.error(f"❌ Google Sheets respondeu com erro: {error_msg}")
                    return ContactResponse(
                        success=False,
                        message="Desculpe, ocorreu um erro ao salvar seus dados. Tente novamente.",
                        contact_id=None
                    )
            except:
                # Se não for JSON válido, pode ser um redirecionamento
                logger.error(f"❌ Resposta inválida do Google Sheets: {response.text[:100]}")
                return ContactResponse(
                    success=False,
                    message="Serviço temporariamente indisponível. Tente novamente em alguns instantes.",
                    contact_id=None
                )
        else:
            logger.error(f"❌ Falha na comunicação com Google Sheets. Status: {response.status_code}")
            logger.error(f"❌ Resposta: {response.text[:200]}")
            return ContactResponse(
                success=False,
                message="Desculpe, serviço temporariamente indisponível. Tente novamente em alguns instantes.",
                contact_id=None
            )
            
    except httpx.TimeoutException:
        logger.error("⏰ Timeout ao tentar conectar com Google Sheets")
        return ContactResponse(
            success=False,
            message="O serviço está demorando para responder. Por favor, tente novamente.",
            contact_id=None
        )
    except Exception as e:
        logger.error(f"💥 Erro no endpoint /contact: {str(e)}", exc_info=True)
        return ContactResponse(
            success=False,
            message="Desculpe, ocorreu um erro interno. Por favor, tente novamente mais tarde.",
            contact_id=None
        )

# Include the router in the main app
app.include_router(api_router)

# Event handlers
@app.on_event("startup")
async def startup_event():
    """Inicia a aplicação"""
    logger.info("🚀 Iniciando Portal Pausa Backend (Google Sheets)...")
    logger.info("✅ Aplicação pronta para receber requisições")

# Adiciona middleware de logging
@app.middleware("http")
async def log_requests(request, call_next):
    """Middleware para log de todas as requisições"""
    start_time = datetime.now(timezone.utc)
    
    request_id = str(uuid.uuid4())[:8]
    
    logger.info(f"📥 [{request_id}] {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        logger.info(f"📤 [{request_id}] {request.method} {request.url.path} - Status: {response.status_code} - Tempo: {process_time:.2f}ms")
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        return response
        
    except Exception as e:
        process_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        logger.error(f"💥 [{request_id}] {request.method} {request.url.path} - Erro: {str(e)} - Tempo: {process_time:.2f}ms")
        raise