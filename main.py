# main.py
from fastapi import FastAPI
from app.api import router
import uvicorn
import os
from app.logger_config import setup_logger

# Configurar el logger
logger = setup_logger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title="API de Análisis de Video",
    description="API para consultar información sobre objetos y escenarios en videos",
    version="1.0.0"
)

# Incluir el router de la API
app.include_router(router)

@app.get("/")
async def root():
    """
    Endpoint raíz para verificar que la API está funcionando
    """
    return {"message": "API de Análisis de Video funcionando correctamente"}

@app.get("/healthcheck")
async def healthcheck():
    """
    Endpoint para verificar la salud de la API
    """
    return {"status": "healthy"}

# Iniciar la aplicación si se ejecuta directamente
if __name__ == "__main__":
    # Obtener puerto de variable de entorno o usar el predeterminado 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Configurar host para permitir conexiones externas en Docker
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Iniciando servidor en {host}:{port}")
    
    # Iniciar el servidor
    uvicorn.run(app, host=host, port=port)