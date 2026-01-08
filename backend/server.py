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

# MongoDB connection with SSL/TLS fix for Render.com
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'portal_pausa_db')

# Variáveis globais
client = None
db = None

async def connect_to_mongodb():
    """Conecta ao MongoDB com tratamento de erros e SSL/TLS fix"""
    global client, db
    
    try:
        logger.info(f"🚀 Tentando conectar ao MongoDB...")
        
        # Mostrar URL segura (sem senha) nos logs
        safe_url = mongo_url
        if '@' in safe_url:
            parts = safe_url.split('@')
            safe_url = 'mongodb://***:***@' + parts[1] if len(parts) > 1 else safe_url
        logger.info(f"📡 URL MongoDB: {safe_url}")
        
        # Configurações otimizadas para Render.com + MongoDB Atlas
        mongo_kwargs = {
            'serverSelectionTimeoutMS': 10000,
            'connectTimeoutMS': 15000,
            'socketTimeoutMS': 30000,
            'maxPoolSize': 10,
            'minPoolSize': 1,
            'retryWrites': True,
            'w': 'majority',
        }
        
        # FIX CRÍTICO: Configurar TLS para MongoDB Atlas (sem ssl_cert_reqs)
        if 'mongodb+srv://' in mongo_url or '.mongodb.net' in mongo_url:
            # Para MongoDB Atlas no Render, use apenas tls
            mongo_kwargs['tls'] = True
            mongo_kwargs['tlsAllowInvalidCertificates'] = True
            logger.info("🔐 Configurando conexão com TLS para MongoDB Atlas")
        
        client = AsyncIOMotorClient(mongo_url, **mongo_kwargs)
        
        # Testar conexão
        await client.admin.command('ping')
        
        db = client[db_name]
        logger.info(f"✅ Conectado com sucesso ao MongoDB! Database: {db_name}")
        
        # Verificar collections
        collections = await db.list_collection_names()
        logger.info(f"📊 Collections disponíveis: {collections}")
        
        # Criar collections se não existirem
        if 'contacts' not in collections:
            await db.create_collection('contacts')
            logger.info("📝 Collection 'contacts' criada")
        
        if 'status_checks' not in collections:
            await db.create_collection('status_checks')
            logger.info("📝 Collection 'status_checks' criada")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao MongoDB: {str(e)[:200]}")
        
        # Tentar conexão alternativa sem TLS (apenas para debug)
        try:
            logger.info("🔄 Tentando conexão alternativa sem TLS...")
            alt_kwargs = {
                'serverSelectionTimeoutMS': 5000,
                'connectTimeoutMS': 10000,
                'maxPoolSize': 5,
                'retryWrites': True,
                'w': 'majority',
            }
            
            # Remover TLS da URL
            alt_url = mongo_url.replace('&tls=true', '').replace('?tls=true', '?')
            alt_url = alt_url.replace('&tlsAllowInvalidCertificates=true', '')
            
            temp_client = AsyncIOMotorClient(alt_url, **alt_kwargs)
            await temp_client.admin.command('ping')
            temp_client.close()
            logger.info("⚠️  Conexão alternativa funcionou (sem TLS)")
            
        except Exception as alt_e:
            logger.error(f"❌ Conexão alternativa também falhou: {str(alt_e)[:100]}")
        
        # Permite que o app inicie mesmo sem DB
        client = None
        db = None
        return False

# Create the main app
app = FastAPI(
    title="Portal Pausa API",
    version="1.0.0",
    description="API Backend para o Portal Pausa - Saúde Feminina",
    docs_url="/docs",
    redoc_url="/redoc"
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

# Modelo CORRIGIDO: APENAS os campos que o frontend envia
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
            "api_contact": "/api/contact",
            "api_test_db": "/api/test-db"
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
        except Exception as e:
            logger.error(f"Erro no health check do MongoDB: {e}")
            db_status = f"error: {str(e)[:50]}"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "Portal Pausa Backend",
        "environment": os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'local'),
        "version": "1.0.0"
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
            "POST   /contact",
            "GET    /test-db"
        ]
    }

@api_router.get("/health")
async def api_health():
    """Health check específico da API"""
    db_status = "connected" if client else "disconnected"
    
    return {
        "api": "running",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": "unknown"
    }

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    """Cria um novo registro de status check"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database não disponível")
    
    try:
        status_dict = input.model_dump()
        status_obj = StatusCheck(**status_dict)
        
        doc = status_obj.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        
        result = await db.status_checks.insert_one(doc)
        
        if result.inserted_id:
            logger.info(f"✅ Status check salvo: {status_obj.client_name}")
            return status_obj
        else:
            raise HTTPException(status_code=500, detail="Erro ao salvar status")
            
    except Exception as e:
        logger.error(f"❌ Erro em /status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)[:100]}")

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    """Retorna todos os status checks"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database não disponível")
    
    try:
        cursor = db.status_checks.find({}, {"_id": 0})
        status_checks = await cursor.to_list(1000)
        
        for check in status_checks:
            if isinstance(check['timestamp'], str):
                try:
                    check['timestamp'] = datetime.fromisoformat(check['timestamp'].replace('Z', '+00:00'))
                except:
                    check['timestamp'] = datetime.now(timezone.utc)
        
        return status_checks
        
    except Exception as e:
        logger.error(f"❌ Erro em GET /status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)[:100]}")

@api_router.post("/contact", response_model=ContactResponse)
async def submit_contact_form(contact: ContactForm):
    """Endpoint para receber formulário de contato do Portal Pausa"""
    
    logger.info(f"📥 Recebendo contato de: {contact.name}")
    
    if db is None:
        logger.error("❌ Database não disponível para salvar contato")
        return ContactResponse(
            success=False,
            message="Serviço temporariamente indisponível. Por favor, tente novamente em alguns minutos.",
            contact_id=None
        )
    
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
        
        contact_dict = contact.model_dump()
        contact_dict["id"] = str(uuid.uuid4())
        contact_dict["timestamp"] = datetime.now(timezone.utc)
        contact_dict["whatsapp_clean"] = whatsapp_clean
        contact_dict["source"] = "portal_pausa_website"
        
        # Formatar para MongoDB
        contact_dict_for_db = contact_dict.copy()
        contact_dict_for_db["timestamp"] = contact_dict["timestamp"].isoformat()
        
        # Salvar no MongoDB
        result = await db.contacts.insert_one(contact_dict_for_db)
        
        if result.inserted_id:
            logger.info(f"✅ Contato salvo com sucesso! ID: {contact_dict['id']}")
            
            return ContactResponse(
                success=True, 
                message="Obrigada por se cadastrar! Entraremos em contato em breve. 💜",
                contact_id=contact_dict["id"]
            )
        else:
            logger.error("❌ Falha ao inserir contato no MongoDB (sem inserted_id)")
            return ContactResponse(
                success=False,
                message="Desculpe, ocorreu um erro ao salvar seu contato. Tente novamente.",
                contact_id=None
            )
            
    except Exception as e:
        logger.error(f"💥 Erro no endpoint /contact: {str(e)}", exc_info=True)
        return ContactResponse(
            success=False,
            message="Desculpe, ocorreu um erro interno. Por favor, tente novamente mais tarde.",
            contact_id=None
        )

# Test endpoint for MongoDB connectivity
@api_router.get("/test-db")
async def test_database():
    """Endpoint para testar conectividade com o MongoDB"""
    if db is None:
        return {
            "status": "error",
            "message": "Database não conectado",
            "mongo_url_preview": mongo_url[:50] + "..." if len(mongo_url) > 50 else mongo_url,
            "environment": os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'local'),
            "fix_suggestion": "Verifique a variável MONGO_URL e as configurações de TLS"
        }
    
    try:
        # Testar ping
        ping_result = await client.admin.command('ping')
        
        # Contar documentos
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
            "environment": os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'local')
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Erro ao conectar com MongoDB: {str(e)}",
            "database": db_name,
            "environment": os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'local'),
            "mongo_url_preview": mongo_url[:30] + "..."
        }

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