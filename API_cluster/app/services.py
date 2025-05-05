# app/services.py
import os
import sys
import logging
import psycopg2
# from celery.result import AsyncResult
from app.models import FrameCharacteristics, Alert

# Configurar el logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_to_postgres():
    """
    Establece conexión con la base de datos PostgreSQL utilizando variables de entorno
    o valores predeterminados.
    
    Returns:
        Conexión a la base de datos PostgreSQL
    """
    try:
        # Obtener parámetros de conexión de variables de entorno o usar valores predeterminados
        host = os.environ.get("DB_HOST", "postgres")
        port = os.environ.get("DB_PORT", "5432")
        user = os.environ.get("DB_USER", "postgres")
        password = os.environ.get("DB_PASSWORD", "postgres")
        dbname = os.environ.get("DB_NAME", "videodata")
        
        # Establecer la conexión
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )
        logger.info("Conexión exitosa a PostgreSQL.")
        return conn
    except Exception as e:
        logger.error(f"Error al conectar con PostgreSQL: {e}")
        return None

def execute_query(cursor, query):
    """
    Ejecuta una consulta SQL en PostgreSQL.
    
    Args:
        cursor: Cursor de la conexión PostgreSQL
        query: Consulta SQL a ejecutar
        
    Returns:
        Resultados de la consulta o lista vacía en caso de error
    """
    try:
        # Ejecutar la consulta
        logger.info(f"Ejecutando consulta: {query}")
        cursor.execute(query)
        # Obtener los resultados
        resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        logger.error(f"Error al ejecutar la consulta: {e}")
        return []

def start_frame_processing(frame: FrameCharacteristics):
    """
    Procesa una solicitud de análisis de frame según sus características.
    Ejecuta consultas SQL en PostgreSQL según el tipo de frame solicitado.
    
    Args:
        frame: Objeto FrameCharacteristics con los parámetros de consulta
        
    Returns:
        Lista de resultados formateados según el tipo de consulta
    """
    try:
        # Conectar a PostgreSQL
        conn = connect_to_postgres()
        if not conn:
            return {"message": "Error de conexión a la base de datos"}
            
        cursor = conn.cursor()

        # Construir la consulta según el tipo de frame
        query = ''

        if frame.type == 1:
            # Consulta para escenarios (Tipo 1)
            query = f"SELECT video_name FROM scenarios WHERE environment_type = '{frame.environment_type}'"

        elif frame.type == 2:
            # Consulta para objetos (Tipo 2)
            query = f"SELECT video_name, sec FROM objects WHERE object_name = '{frame.object_name}'"

            # Agregar filtros opcionales
            if frame.color:
                query += f" AND color = '{frame.color}'"

            if frame.proximity:
                query += f" AND proximity = '{frame.proximity}'"

        elif frame.type == 3:   
            # Consulta para contar objetos por video (Tipo 3)
            query = f"SELECT video_name, sec, COUNT(*) AS object_count FROM objects WHERE object_name = '{frame.object_name}' GROUP BY video_name, sec ORDER BY object_count DESC"
    
        # Si no se ha construido una consulta válida
        if not query:
            logger.error(f"Tipo de frame no reconocido: {frame.type}")
            return {"message": "Tipo de consulta no válido"}

        # Obtener los resultados de la consulta
        resultados = execute_query(cursor, query)

        if resultados:
            logger.info(f"Se encontraron {len(resultados)} resultados")
            for fila in resultados:
                logger.info(f"Resultado: {fila}")
        else:
            logger.info("No se encontraron resultados.")

        # Cerrar la conexión a PostgreSQL
        cursor.close()
        conn.close()

        # Formatear el resultado en JSON según el tipo de consulta
        response_data = []
        
        if frame.type == 1:
            # Formato para consulta tipo 1 (escenarios)
            for row in resultados:
                response_data.append({
                    "video_name": row[0]
                })

        elif frame.type == 2:
            # Formato para consulta tipo 2 (objetos)
            for row in resultados:
                response_data.append({
                    "video_name": row[0],
                    "sec": row[1],
                })

        elif frame.type == 3:
            # Formato para consulta tipo 3 (conteo de objetos)
            for row in resultados:
                response_data.append({
                    "video_name": row[0],
                    "sec": row[1],
                    "object_count": row[2]
                })

        return response_data
    
    except Exception as e:
        logger.error(f"Error al procesar el frame: {e}")
        return {"message": "Error en el procesamiento", "error": str(e)}

# def get_frame_task_status(task_id: str):
#     """
#     Consulta el estado de la tarea de procesamiento de un frame
    
#     Args:
#         task_id: Identificador de la tarea Celery
        
#     Returns:
#         Diccionario con el estado actual de la tarea
#     """
#     task = AsyncResult(task_id)

#     if task.state == 'PENDING':
#         return {"status": "En proceso"}
#     elif task.state == 'SUCCESS':
#         return {"status": "Completado", "result": task.result}
#     elif task.state == 'FAILURE':
#         return {"status": "Fallido", "error": str(task.result)}
#     return {"status": "Estado desconocido"}


def execute_alerts(alerts):
    """
    Ejecuta las alertas recibidas, ejecutando las consultas SQL asociadas en la base de datos.

    Args:
        alerts: Lista de alertas con SQL asociado

    Returns:
        Resultado de las alertas procesadas.
    """
    results = []
    conn = connect_to_postgres()
    if not conn:
        return {"message": "Error de conexión a la base de datos"}

    cursor = conn.cursor()

    try:
        for alert in alerts:
            logger.info(f"⚠️ Ejecutando alerta: {alert.alert}")
            logger.info(f"📄 SQL: {alert.sql}")
            result = execute_query(cursor, alert.sql)
            results.append({
                "alert": alert.alert,
                "sql": alert.sql,
                "result": result
            })
        
        # Cerrar la conexión después de procesar todas las alertas
        conn.close()

        return {"results": results}

    except Exception as e:
        logger.error(f"Error al ejecutar las alertas: {e}")
        return {"message": "Error al procesar las alertas", "error": str(e)}