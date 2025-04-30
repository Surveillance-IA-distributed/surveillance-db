# app/logger_config.py
import logging
import os

def setup_logger(name):
    """
    Configura y devuelve un logger con el formato especificado.
    
    Args:
        name: Nombre del logger, generalmente __name__ del módulo
        
    Returns:
        Logger configurado
    """
    # Configuración de nivel de log desde variable de entorno o predeterminado INFO
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logging_level = getattr(logging, log_level, logging.INFO)
    
    # Formato del log: timestamp - nombre - nivel - mensaje
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configurar el logger
    logger = logging.getLogger(name)
    
    # Evitar duplicación de handlers si el logger ya está configurado
    if not logger.handlers:
        # Configurar el nivel del logger
        logger.setLevel(logging_level)
        
        # Crear un handler para la consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging_level)
        
        # Formato para el handler
        formatter = logging.Formatter(log_format)
        console_handler.setFormatter(formatter)
        
        # Agregar el handler al logger
        logger.addHandler(console_handler)
    
    return logger