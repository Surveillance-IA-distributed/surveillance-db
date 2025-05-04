#!/usr/bin/env python3
import subprocess
import json
import time
import sys

def run_curl_command(url, method="GET", data=None, headers=None):
    """
    Ejecuta un comando curl y devuelve la respuesta
    
    Args:
        url: URL a la que hacer la petición
        method: Método HTTP (GET, POST, etc.)
        data: Datos a enviar en formato JSON (para POST, PUT)
        headers: Cabeceras HTTP
    
    Returns:
        dict: Respuesta de la API en formato JSON
    """
    cmd = ["curl", "-s", "-X", method]
    
    if headers:
        for key, value in headers.items():
            cmd.extend(["-H", f"{key}: {value}"])
    
    if data:
        cmd.extend(["-d", json.dumps(data)])
    
    cmd.append(url)
    
    print(f"Ejecutando: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error al ejecutar curl: {result.stderr}")
        return None
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Error al decodificar JSON: {result.stdout}")
        return result.stdout

def test_nest_backend():
    """Prueba los endpoints del backend NestJS"""
    base_url = "http://localhost:3000"
    headers = {"Content-Type": "application/json"}
    
    print("\n=== Probando Backend NestJS ===")
    
    # 1. Cargar datos
    print("\n1. Cargando datos a la base de datos...")
    response = run_curl_command(f"{base_url}/seeder/load-data", 
                               method="POST", 
                               headers=headers)
    print(f"Respuesta: {json.dumps(response, indent=2)}")
    
    # 2. Consultar objetos
    print("\n2. Consultando todos los objetos...")
    response = run_curl_command(f"{base_url}/seeder/objects", 
                               headers=headers)
    print(f"Objetos encontrados: {len(response) if isinstance(response, list) else 0}")
    
    # 3. Consultar escenarios
    print("\n3. Consultando todos los escenarios...")
    response = run_curl_command(f"{base_url}/seeder/scenarios", 
                               headers=headers)
    print(f"Escenarios encontrados: {len(response) if isinstance(response, list) else 0}")
    
    # 4. Consultar características
    print("\n4. Consultando todas las características...")
    response = run_curl_command(f"{base_url}/seeder/features", 
                               headers=headers)
    print(f"Características encontradas: {len(response) if isinstance(response, list) else 0}")
    
    # 5. Consultar objeto específico
    print("\n5. Consultando objeto 'person'...")
    response = run_curl_command(f"{base_url}/seeder/objects/person", 
                               headers=headers)
    print(f"Resultados para 'person': {len(response) if isinstance(response, list) else 0}")

def test_fastapi():
    """Prueba los endpoints de la API FastAPI"""
    base_url = "http://localhost:8000"
    headers = {"Content-Type": "application/json"}
    
    print("\n=== Probando API FastAPI ===")
    
    # 1. Consulta tipo 1 (escenarios)
    print("\n1. Consultando escenarios de tipo 'parking_lot'...")
    data = {
        "type": 1,
        "video_name": "",
        "environment_type": "parking_lot",
        "object_name": None,
        "color": None,
        "proximity": None
    }
    response = run_curl_command(f"{base_url}/receive_characteristics", 
                               method="POST", 
                               data=data, 
                               headers=headers)
    print(f"Respuesta: {json.dumps(response, indent=2)}")
    
    # 2. Consulta tipo 2 (objetos)
    print("\n2. Consultando objetos 'person'...")
    data = {
        "type": 2,
        "video_name": "",
        "environment_type": None,
        "object_name": "person",
        "color": None,
        "proximity": None
    }
    response = run_curl_command(f"{base_url}/receive_characteristics", 
                               method="POST", 
                               data=data, 
                               headers=headers)
    print(f"Respuesta: {json.dumps(response, indent=2)}")
    
    # 3. Consulta tipo 3 (conteo)
    print("\n3. Contando objetos 'car'...")
    data = {
        "type": 3,
        "video_name": "",
        "environment_type": None,
        "object_name": "car",
        "color": None,
        "proximity": None
    }
    response = run_curl_command(f"{base_url}/receive_characteristics", 
                               method="POST", 
                               data=data, 
                               headers=headers)
    print(f"Respuesta: {json.dumps(response, indent=2)}")

def main():
    """Función principal"""
    print("=== Iniciando pruebas de API ===")
    
    # Esperar a que los servicios estén disponibles
    print("Esperando 5 segundos para que los servicios estén listos...")
    time.sleep(5)
    
    # Probar el backend NestJS
    test_nest_backend()
    
    # Probar la API FastAPI
    test_fastapi()
    
    print("\n=== Pruebas completadas ===")

if __name__ == "__main__":
    main()