#!/usr/bin/env python
import requests
import json
import sys
import time
import os
import argparse

def check_api_status(url, data, max_retries=3):
    """
    Verifica el estado de la API realizando una solicitud POST.
    
    Args:
        url: URL base de la API
        data: Datos JSON para enviar en la solicitud
        max_retries: Número máximo de intentos
        
    Returns:
        True si la API responde correctamente, False en caso contrario
    """
    for i in range(max_retries):
        try:
            # Construir la URL completa para la solicitud
            full_url = f"http://{url}/receive_characteristics"
            print(f"Intentando conectar a: {full_url}")
            print(f"Datos de la solicitud: {json.dumps(data, indent=2)}")
            
            # Realizar la solicitud POST a la API
            response = requests.post(
                full_url, 
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10  # Tiempo de espera de 10 segundos
            )
            
            # Registrar código de estado y respuesta
            print(f"\nCódigo de estado: {response.status_code}")
            
            try:
                # Intentar formatear la respuesta como JSON
                response_json = response.json()
                print(f"Respuesta: {json.dumps(response_json, indent=2)}")
            except json.JSONDecodeError:
                # Si la respuesta no es JSON válido
                print(f"Respuesta no es JSON válido: {response.text}")
            
            # Verificar si la solicitud fue exitosa (código 200)
            if response.status_code == 200:
                return True
            else:
                print(f"La API respondió con código de error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar con la API (intento {i+1}/{max_retries}): {e}")
            
        # Esperar antes de reintentar, excepto en el último intento
        if i < max_retries - 1:
            wait_time = 2 * (i + 1)  # Espera exponencial: 2, 4, 6... segundos
            print(f"Reintentando en {wait_time} segundos...")
            time.sleep(wait_time)
    
    return False

def main():
    """
    Función principal que verifica el estado de la API.
    """
    # Configurar parser de argumentos para permitir especificar la URL
    parser = argparse.ArgumentParser(description='Verificar el estado de la API de análisis de video')
    parser.add_argument('--url', type=str, default="localhost:8000",
                        help='URL de la API (por defecto: localhost:8000)')
    args = parser.parse_args()
    
    # URL de destino (desde argumentos o variable de entorno)
    url = os.environ.get("API_URL", args.url)
    
    print(f"=== Verificando estado de la API en {url} ===")
    
    # JSON_DATA01 (Tipo 1: Consulta por tipo de entorno)
    data = {
        "type": 1,
        "video_name": "parking_lot_video_1",
        "environment_type": "parking_lot",
        "object_name": None,
        "color": None,
        "proximity": None
    }
    
    # Verificar el estado de la API
    success = check_api_status(url, data)
    
    if success:
        print("\n✅ La API está funcionando correctamente.")
        sys.exit(0)
    else:
        print("\n❌ La API no está funcionando correctamente.")
        sys.exit(1)

if __name__ == "__main__":
    main()