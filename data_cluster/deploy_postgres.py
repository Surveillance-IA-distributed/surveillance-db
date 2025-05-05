#!/usr/bin/env python
import os
import psycopg2
import sys
import time

# Función para conectarse a PostgreSQL y crear la base de datos si no existe
def create_database_if_not_exists(host, port, user, password, dbname):
    """
    Verifica si la base de datos existe y la crea si no existe.
    Se conecta primero a la base de datos 'postgres' (predeterminada).
    """
    try:
        # Primero, conectarse a la base de datos 'postgres' (que siempre existe)
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="postgres"  # Conectar a la base de datos por defecto
        )
        conn.autocommit = True  # Importante para poder crear la base de datos
        cursor = conn.cursor()
        
        # Verificar si la base de datos ya existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"La base de datos '{dbname}' no existe. Creándola...")
            # SQL para crear la base de datos
            cursor.execute(f"CREATE DATABASE {dbname}")
            print(f"Base de datos '{dbname}' creada exitosamente.")
        else:
            print(f"La base de datos '{dbname}' ya existe.")
            
        # Cerrar la conexión a 'postgres'
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")
        return False

# Función para conectarse a PostgreSQL
def connect_to_postgres(host, port, user, password, dbname):
    """
    Establece conexión con la base de datos PostgreSQL.
    Reintenta la conexión varias veces en caso de fallo inicial.
    """
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=dbname
            )
            print("Conexión exitosa a PostgreSQL.")
            return conn
        except Exception as e:
            retry_count += 1
            print(f"Intento {retry_count}/{max_retries}: Error al conectar con PostgreSQL: {e}")
            if retry_count >= max_retries:
                print("Se alcanzó el número máximo de intentos. Saliendo...")
                sys.exit(1)
            print(f"Reintentando en 5 segundos...")
            time.sleep(5)

# Función para ejecutar consultas
def execute_query(cursor, query, fetch=True):
    """
    Ejecuta una consulta SQL en PostgreSQL.
    
    Args:
        cursor: Cursor de la conexión PostgreSQL
        query: Consulta SQL a ejecutar
        fetch: Booleano que indica si se deben obtener resultados
        
    Returns:
        Resultados de la consulta si fetch=True, lista vacía en caso contrario
    """
    try:
        print(f"Ejecutando consulta:\n{query}")
        cursor.execute(query)
        print("Consulta ejecutada exitosamente.")
        if fetch:
            try:
                # Intentar obtener resultados
                results = cursor.fetchall()
                return results
            except psycopg2.ProgrammingError:
                # Si no hay resultados que devolver
                return []
        return []
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return []

# Función para crear las tablas
def create_tables(cursor):
    """
    Crea las tablas necesarias en la base de datos PostgreSQL si no existen.
    """
    table_queries = [
        """
        CREATE TABLE IF NOT EXISTS objects (
            object_name VARCHAR(255),
            video_name VARCHAR(255),
            x1 INT,
            y1 INT,
            x2 INT,
            y2 INT,
            color VARCHAR(255),
            proximity VARCHAR(255),
            sec INT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS scenarios (
            video_name VARCHAR(255),
            environment_type VARCHAR(255),
            description TEXT,
            weather VARCHAR(255),
            time_of_day VARCHAR(255),
            terrain VARCHAR(255),
            crowd_level VARCHAR(255),
            lighting VARCHAR(255)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS features (
            video_name VARCHAR(255),
            sec INT,
            object_name VARCHAR(255),
            description TEXT,
            color1 VARCHAR(255),
            color2 VARCHAR(255),
            size VARCHAR(255),
            orientation VARCHAR(255),
            type VARCHAR(255)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS objects_new (
            object_name VARCHAR(255),
            video_name VARCHAR(255),
            x1 INT,
            y1 INT,
            x2 INT,
            y2 INT,
            color VARCHAR(255),
            proximity VARCHAR(255),
            sec INT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS scenarios_new (
            video_name VARCHAR(255),
            environment_type VARCHAR(255),
            description TEXT,
            weather VARCHAR(255),
            time_of_day VARCHAR(255),
            terrain VARCHAR(255),
            crowd_level VARCHAR(255),
            lighting VARCHAR(255)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS features_new (
            video_name VARCHAR(255),
            sec INT,
            object_name VARCHAR(255),
            description TEXT,
            color1 VARCHAR(255),
            color2 VARCHAR(255),
            size VARCHAR(255),
            orientation VARCHAR(255),
            type VARCHAR(255)
        )
        """
    ]
    for query in table_queries:
        execute_query(cursor, query, fetch=False)

# Función para cargar datos de muestra
def insert_sample_data(cursor):
    """
    Inserta datos de muestra en las tablas para pruebas.
    """
    # Datos de muestra para la tabla objects
    objects_data = [
        """
        INSERT INTO objects (object_name, video_name, x1, y1, x2, y2, color, proximity, sec)
        VALUES ('tree', 'video1', 86, 890, 190, 190, '83, 127, 138', 'near', 123)
        """,
        """
        INSERT INTO objects (object_name, video_name, x1, y1, x2, y2, color, proximity, sec)
        VALUES ('person', 'video1', 120, 450, 200, 700, '255, 0, 0', 'middle', 45)
        """,
        """
        INSERT INTO objects (object_name, video_name, x1, y1, x2, y2, color, proximity, sec)
        VALUES ('car', 'video2', 300, 200, 500, 350, '0, 0, 255', 'far', 60)
        """,
        """
        INSERT INTO objects (object_name, video_name, x1, y1, x2, y2, color, proximity, sec)
        VALUES ('umbrella', 'parking_lot_video_1', 150, 300, 180, 350, '0, 0, 0', 'near', 30)
        """
    ]
    
    # Datos de muestra para la tabla scenarios
    scenarios_data = [
        """
        INSERT INTO scenarios (video_name, environment_type, description, weather, time_of_day, terrain, crowd_level, lighting)
        VALUES ('video1', 'street', 'Una calle concurrida con tráfico', 'sunny', 'day', 'paved', 'high', 'natural')
        """,
        """
        INSERT INTO scenarios (video_name, environment_type, description, weather, time_of_day, terrain, crowd_level, lighting)
        VALUES ('video2', 'highway', 'Autopista con vehículos a alta velocidad', 'cloudy', 'day', 'paved', 'medium', 'natural')
        """,
        """
        INSERT INTO scenarios (video_name, environment_type, description, weather, time_of_day, terrain, crowd_level, lighting)
        VALUES ('parking_lot_video_1', 'parking_lot', 'Estacionamiento con varios coches aparcados', 'rainy', 'day', 'paved', 'low', 'natural')
        """
    ]
    
    # Datos de muestra para la tabla features
    features_data = [
        """
        INSERT INTO features (video_name, sec, object_name, description, color1, color2, size, orientation, type)
        VALUES ('video1', 30, 'person', 'Persona con ropa azul caminando', 'blue', 'black', 'medium', 'frontal', 'pedestrian')
        """,
        """
        INSERT INTO features (video_name, sec, object_name, description, color1, color2, size, orientation, type)
        VALUES ('video2', 45, 'car', 'Coche compacto blanco', 'white', '', 'medium', 'lateral', 'sedan')
        """,
        """
        INSERT INTO features (video_name, sec, object_name, description, color1, color2, size, orientation, type)
        VALUES ('parking_lot_video_1', 60, 'umbrella', 'Paraguas negro abierto', 'black', '', 'small', 'top', 'accessory')
        """
    ]
    
    # Insertar datos de muestra
    print("Insertando datos de muestra en la tabla 'objects'...")
    for query in objects_data:
        execute_query(cursor, query, fetch=False)
        
    print("Insertando datos de muestra en la tabla 'scenarios'...")
    for query in scenarios_data:
        execute_query(cursor, query, fetch=False)
        
    print("Insertando datos de muestra en la tabla 'features'...")
    for query in features_data:
        execute_query(cursor, query, fetch=False)

# Función para cargar datos desde archivos CSV
def load_data_from_csv(cursor, table_name, file_path):
    """
    Carga datos desde un archivo CSV a una tabla PostgreSQL.
    
    Args:
        cursor: Cursor de la conexión PostgreSQL
        table_name: Nombre de la tabla donde cargar los datos
        file_path: Ruta al archivo CSV
    """
    if not os.path.exists(file_path):
        print(f"El archivo {file_path} no existe. Cargando datos de muestra en su lugar.")
        return False
    
    try:
        with open(file_path, 'r') as f:
            # Preparar para saltar la primera línea (encabezado)
            next(f)
            # Usar copy_expert para cargar los datos CSV directamente
            cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV", f)
        print(f"Datos cargados exitosamente en la tabla '{table_name}' desde '{file_path}'.")
        return True
    except Exception as e:
        print(f"Error al cargar datos en la tabla {table_name} desde CSV: {e}")
        return False

# Función principal
def main():
    """
    Función principal que configura la base de datos PostgreSQL.
    
    1. Establece conexión con PostgreSQL
    2. Crea las tablas necesarias
    3. Carga datos de archivos CSV si están disponibles, o inserta datos de muestra
    4. Ejecuta consultas de prueba
    """
    # Parámetros de conexión
    host = os.environ.get("DB_HOST", "postgres")  # Nombre del servicio en Docker
    port = int(os.environ.get("DB_PORT", "5432"))
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "postgres")
    dbname = os.environ.get("DB_NAME", "videodata")

    # Rutas relativas de los archivos CSV
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_files = {
        "objects": os.path.join(base_dir, "data_sd", "objects_data.csv"),
        "scenarios": os.path.join(base_dir, "data_sd", "scenarios_data.csv"),
        "features": os.path.join(base_dir, "data_sd", "features_data.csv"),
    }

    # Intentar crear la base de datos si no existe
    print("Verificando si la base de datos existe...")
    if not create_database_if_not_exists(host, port, user, password, dbname):
        print("No se pudo crear la base de datos. Saliendo...")
        sys.exit(1)

    # Conectar a PostgreSQL
    print(f"Conectando a la base de datos '{dbname}'...")
    conn = connect_to_postgres(host, port, user, password, dbname)
    conn.autocommit = True  # Importante para que los cambios se apliquen inmediatamente
    cursor = conn.cursor()

    # Crear tablas
    print("Creando tablas...")
    create_tables(cursor)

    # Verificar si se pueden cargar datos desde archivos CSV
    csv_data_loaded = False
    
    # Cargar datos en las tablas desde archivos CSV si existen
    print("Intentando cargar datos desde archivos CSV...")
    for table, file_path in data_files.items():
        if load_data_from_csv(cursor, table, file_path):
            csv_data_loaded = True
    
    # Si no se cargaron datos desde CSV, insertar datos de muestra
    if not csv_data_loaded:
        print("No se encontraron archivos CSV válidos. Insertando datos de muestra...")
        insert_sample_data(cursor)

    # Consultas de prueba
    test_queries = [
        "SELECT * FROM objects LIMIT 10",
        "SELECT * FROM scenarios LIMIT 10",
        "SELECT * FROM features LIMIT 10"
    ]
    
    print("\n----- VERIFICACIÓN DE DATOS -----")
    for query in test_queries:
        results = execute_query(cursor, query)
        if results:
            print(f"\nResultados de la consulta ({query.strip()}):")
            for row in results:
                print(row)
        else:
            print(f"\nNo se encontraron resultados para la consulta: {query.strip()}")

    # Cerrar conexión
    print("\n----- FINALIZANDO INICIALIZACIÓN DE LA BASE DE DATOS -----")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()