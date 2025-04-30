# Dockerfile para el servicio API
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias requeridas para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de requisitos
COPY API_cluster/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Crear estructura de directorios
RUN mkdir -p app

# Copiar archivos de código fuente
COPY API_cluster/app/api.py app/
COPY API_cluster/app/models.py app/
COPY API_cluster/app/services.py app/
COPY API_cluster/app/tasks.py app/
COPY API_cluster/app/logger_config.py app/
COPY main.py .
COPY status.py .

# Hacer ejecutable el script de status
RUN chmod +x status.py

# Exponer puerto para la API
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]