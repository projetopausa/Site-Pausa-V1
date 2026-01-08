import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connection():
    # Use a mesma URL do Render
    MONGO_URL = "mongodb+srv://pausa_admin:61hWYSuOt6olPNG4@portal-pausa-cluster.hxey96a.mongodb.net/portal_pausa_db?retryWrites=true&w=majority&appName=portal-pausa-cluster&tls=true&tlsAllowInvalidCertificates=true"
    
    print("Testando conexão com MongoDB Atlas...")
    
    try:
        client = AsyncIOMotorClient(
            MONGO_URL,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=15000,
            tls=True,
            tlsAllowInvalidCertificates=True
        )
        
        # Testar conexão
        await client.admin.command('ping')
        print("✅ Conexão bem-sucedida!")
        
        # Listar databases
        dbs = await client.list_database_names()
        print(f"Databases: {dbs}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
    
    #comentario de alguma coisa
    