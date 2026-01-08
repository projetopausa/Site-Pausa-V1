from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone

# Configurar logging primeiro
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with better error handling and compatibility
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'portal_pausa_db')

# Configurações para melhor compatibilidade
mongo_kwargs = {
    'serverSelectionTimeoutMS': 10000,  # 10 segundos timeout
    'connectTimeoutMS': 15000,          # 15 segundos para conectar
    'socketTimeoutMS': 45000,           # 45 segundos para operações
    'maxPoolSize': 10,
    'minPoolSize': 1,
}

# Variáveis globais (serão inicializadas no startup)
client = None
db = None

async def connect_to_mongodb():
    """Conecta ao MongoDB com tratamento de erros"""
    global client, db
    
    try:
        logger.info(f"Tentando conectar ao MongoDB: {mongo_url[:50]}...")
        
        # Remove credenciais do log por segurança
        safe_url = mongo_url
        if '@' in safe_url:
            parts = safe_url.split('@')
            safe_url = 'mongodb://***:***@' + parts[1] if len(parts) > 1 else safe_url
        
        logger.info(f"URL MongoDB (segura): {safe_url}")
        
        client = AsyncIOMotorClient(mongo_url, **mongo_kwargs)
        
        # Testa conexão imediatamente
        await client.admin.command('ping')
        
        db = client[db_name]
        logger.info(f"✅ Conectado com sucesso ao MongoDB! Database: {db_name}")
        
        # Cria collections se não existirem
        collections = await db.list_collection_names()
        logger.info(f"Collections disponíveis: {collections}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao MongoDB: {e}")
        
        # Tenta conexão alternativa se for URL SRV
        if 'mongodb+srv://' in mongo_url:
            logger.info("Tentando conexão alternativa sem SRV...")
            try:
                # Converte URL SRV para normal (apenas para log)
                alt_url = mongo_url.replace('mongodb+srv://', 'mongodb://')
                alt_url = alt_url.replace('/?', '/portal_pausa_db?')
                logger.info(f"URL alternativa: {alt_url[:60]}...")
            except:
                pass
        
        # Permite que o app inicie mesmo sem DB (para debug)
        client = None
        db = None
        return False

# Create the main app without a prefix
app = FastAPI(title="Portal Pausa API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class ContactForm(BaseModel):
    name: str
    whatsapp: str
    acceptCommunication: bool = False

class ContactResponse(BaseModel):
    success: bool
    message: str
    contact_id: Optional[str] = None

# Health check endpoint
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
            "api_root": "/api/",
            "api_contact": "/api/contact"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint para monitoramento"""
    db_status = "disconnected"
    
    if client is not None:
        try:
            await client.admin.command('ping')
            db_status = "connected"
        except:
            db_status = "error"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "Portal Pausa Backend"
    }

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def api_root():
    return {
        "message": "Portal Pausa API",
        "version": "1.0.0",
        "endpoints": [
            "GET    /status",
            "POST   /status",
            "POST   /contact"
        ]
    }

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    if db is None:
        raise HTTPException(status_code=503, detail="Database não disponível")
    
    try:
        status_dict = input.model_dump()
        status_obj = StatusCheck(**status_dict)
        
        # Convert to dict and serialize datetime to ISO string for MongoDB
        doc = status_obj.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        
        result = await db.status_checks.insert_one(doc)
        
        if result.inserted_id:
            return status_obj
        else:
            raise HTTPException(status_code=500, detail="Erro ao salvar status")
            
    except Exception as e:
        logger.error(f"Erro em /status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    if db is None:
        raise HTTPException(status_code=503, detail="Database não disponível")
    
    try:
        # Exclude MongoDB's _id field from the query results
        status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
        
        # Convert ISO string timestamps back to datetime objects
        for check in status_checks:
            if isinstance(check['timestamp'], str):
                check['timestamp'] = datetime.fromisoformat(check['timestamp'])
        
        return status_checks
        
    except Exception as e:
        logger.error(f"Erro em GET /status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@api_router.post("/contact", response_model=ContactResponse)
async def submit_contact_form(contact: ContactForm):
    """Endpoint para receber formulário de contato do Portal Pausa"""
    
    if db is None:
        logger.error("Tentativa de acesso ao endpoint /contact com database não disponível")
        raise HTTPException(
            status_code=503, 
            detail="Serviço temporariamente indisponível. Tente novamente em alguns instantes."
        )
    
    try:
        logger.info(f"Recebendo contato: {contact.name} - {contact.whatsapp[:10]}...")
        
        # Validação adicional do WhatsApp
        whatsapp_clean = ''.join(filter(str.isdigit, contact.whatsapp))
        if len(whatsapp_clean) < 10:
            raise HTTPException(
                status_code=400, 
                detail="Número de WhatsApp inválido. Use o formato (XX) XXXXX-XXXX"
            )
        
        contact_dict = contact.model_dump()
        contact_dict["id"] = str(uuid.uuid4())
        contact_dict["timestamp"] = datetime.now(timezone.utc)
        contact_dict["whatsapp_clean"] = whatsapp_clean
        
        # Formata timestamp para ISO string para MongoDB
        contact_dict_for_db = contact_dict.copy()
        contact_dict_for_db["timestamp"] = contact_dict["timestamp"].isoformat()
        
        # Salva no MongoDB
        result = await db.contacts.insert_one(contact_dict_for_db)
        
        if result.inserted_id:
            logger.info(f"Contato salvo com sucesso: {contact_dict['id']}")
            
            return ContactResponse(
                success=True, 
                message="Obrigada por se cadastrar! Entraremos em contato em breve. 💜",
                contact_id=contact_dict["id"]
            )
        else:
            logger.error("Falha ao inserir contato no MongoDB")
            raise HTTPException(
                status_code=500, 
                detail="Erro ao salvar seu contato. Por favor, tente novamente."
            )
            
    except HTTPException:
        raise  # Re-lança exceções HTTP já tratadas
    except Exception as e:
        logger.error(f"Erro no endpoint /contact: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="Desculpe, ocorreu um erro interno. Por favor, tente novamente mais tarde."
        )

# Include the router in the main app
app.include_router(api_router)

# Configure CORS
cors_origins = os.environ.get('CORS_ORIGINS', '*')
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=cors_origins.split(',') if cors_origins != '*' else ["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Event handlers
@app.on_event("startup")
async def startup_event():
    """Conecta ao MongoDB quando a aplicação inicia"""
    logger.info("🚀 Iniciando Portal Pausa Backend...")
    
    # Conecta ao MongoDB
    connected = await connect_to_mongodb()
    
    if not connected:
        logger.warning("⚠️  Aplicação iniciando SEM conexão com MongoDB")
        logger.warning("   Verifique a variável MONGO_URL e a conexão de rede")
    
    logger.info("✅ Aplicação pronta para receber requisições")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Fecha conexão com MongoDB ao desligar"""
    if client is not None:
        logger.info("Fechando conexão com MongoDB...")
        client.close()
        logger.info("✅ Conexão com MongoDB fechada")

# Adiciona middleware de logging
@app.middleware("http")
async def log_requests(request, call_next):
    """Middleware para log de todas as requisições"""
    start_time = datetime.now(timezone.utc)
    
    # Gera ID único para a requisição
    request_id = str(uuid.uuid4())[:8]
    
    logger.info(f"📥 [{request_id}] {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        logger.info(f"📤 [{request_id}] {request.method} {request.url.path} - Status: {response.status_code} - Tempo: {process_time:.2f}ms")
        
        # Adiciona headers de debug
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        return response
        
    except Exception as e:
        process_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        logger.error(f"💥 [{request_id}] {request.method} {request.url.path} - Erro: {str(e)} - Tempo: {process_time:.2f}ms")
        raise

# Test endpoint for MongoDB connectivity
@api_router.get("/test-db")
async def test_database():
    """Endpoint para testar conectividade com o MongoDB"""
    if db is None:
        return {
            "status": "error",
            "message": "Database não conectado",
            "mongo_url": mongo_url[:50] + "..." if len(mongo_url) > 50 else mongo_url,
            "environment": os.environ.get('RENDER', 'local')
        }
    
    try:
        # Testa ping
        await client.admin.command('ping')
        
        # Conta documentos
        contacts_count = await db.contacts.count_documents({})
        status_count = await db.status_checks.count_documents({})
        
        return {
            "status": "connected",
            "message": "✅ MongoDB conectado com sucesso!",
            "database": db_name,
            "collections": {
                "contacts": contacts_count,
                "status_checks": status_count
            },
            "environment": os.environ.get('RENDER', 'local')
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Erro ao conectar com MongoDB: {str(e)}",
            "database": db_name,
            "environment": os.environ.get('RENDER', 'local'),
            "mongo_url_preview": mongo_url[:30] + "..."
        }