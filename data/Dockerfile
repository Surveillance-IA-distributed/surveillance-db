# Dockerfile para el servicio de carga de datos
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias requeridas para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar psycopg2
RUN pip install --no-cache-dir psycopg2-binary

# Crear directorios necesarios
RUN mkdir -p data_sd

# Copiar script de inicialización de base de datos
COPY data_cluster/deploy_postgres.py .

# Copiar archivos de datos CSV (si existen)
COPY data_cluster/data_sd/ data_sd/

# Comando para ejecutar el script
CMD ["python", "deploy_postgres.py"]