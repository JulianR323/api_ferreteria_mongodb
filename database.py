from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

MONGODB_URL = config("MONGODB_URL", default="mongodb://localhost:27017")
DATABASE_NAME = config("DATABASE_NAME", default="ferreteria_db")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

coleccion_ferreteria = database["ferreteria"]

async def verificar_conexion():
    try:
        await client.admin.command("ping")
        print(f"Conexión exitosa a MONGODB - Base de datos: '{DATABASE_NAME}'")
    except Exception as e:
        print(f"Error al conectar a MONGODB: {e}")
