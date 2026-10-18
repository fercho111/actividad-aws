import boto3
import json
from pymongo import MongoClient


# ================================
# CONFIGURACION
# ================================

SECRET_NAME = "rds!cluster-c54cc6c2-0c51-4182-9624-fb1da0e1624f"
REGION = "us-east-1"

# localhost porque conectamos via tunel SSH
HOST = "localhost"
PORT = 27017
TLS_CA_FILE = "global-bundle.pem"

DB_NAME = "punto3_db"
COLLECTION_NAME = "productos"


# ================================
# FUNCIONES
# ================================

def get_docdb_credentials():
    """Recuperar credenciales de DocumentDB desde Secrets Manager"""
    session = boto3.session.Session()
    client = session.client("secretsmanager", region_name=REGION)
    response = client.get_secret_value(SecretId=SECRET_NAME)
    secret = json.loads(response["SecretString"])
    print(f"Credenciales recuperadas de Secrets Manager para usuario: {secret['username']}")
    return secret["username"], secret["password"]


def connect_to_documentdb(username, password):
    """Conectar a DocumentDB a traves del tunel SSH"""
    client = MongoClient(
        host=HOST,
        port=PORT,
        username=username,
        password=password,
        tls=True,
        tlsCAFile=TLS_CA_FILE,
        tlsAllowInvalidHostnames=True,
        directConnection=True,
        retryWrites=False,
        serverSelectionTimeoutMS=5000,
    )

    # Verificar conexion
    result = client.admin.command("ping")
    print(f"Conexion exitosa a DocumentDB: {result}")
    return client


def insert_documents(collection):
    """Insertar 10 documentos de productos"""

    # Limpiar coleccion si ya existe
    collection.delete_many({})

    productos = [
        {"nombre": "Laptop",     "precio": 1200, "stock": 5,  "categoria": "electronica"},
        {"nombre": "Mouse",      "precio": 25,   "stock": 50, "categoria": "electronica"},
        {"nombre": "Teclado",    "precio": 80,   "stock": 30, "categoria": "electronica"},
        {"nombre": "Monitor",    "precio": 300,  "stock": 15, "categoria": "electronica"},
        {"nombre": "Silla",      "precio": 150,  "stock": 10, "categoria": "muebles"},
        {"nombre": "Escritorio", "precio": 350,  "stock": 8,  "categoria": "muebles"},
        {"nombre": "Lampara",    "precio": 45,   "stock": 25, "categoria": "iluminacion"},
        {"nombre": "Audifonos",  "precio": 60,   "stock": 40, "categoria": "electronica"},
        {"nombre": "Webcam",     "precio": 90,   "stock": 20, "categoria": "electronica"},
        {"nombre": "Microfono",  "precio": 120,  "stock": 12, "categoria": "electronica"},
    ]

    result = collection.insert_many(productos)
    print(f"\n{len(result.inserted_ids)} documentos insertados correctamente")
    return result


def query_with_filter(collection):
    """Busqueda con filtro: productos de electronica con precio menor a 100"""
    print("\n" + "=" * 60)
    print("CONSULTA 1: Filtro")
    print("Productos de categoria 'electronica' con precio < $100")
    print("=" * 60)

    results = collection.find(
        {"categoria": "electronica", "precio": {"$lt": 100}}
    )

    for doc in results:
        print(f"  - {doc['nombre']}: ${doc['precio']} (stock: {doc['stock']})")


def query_with_sort(collection):
    """Ordenacion: productos ordenados por precio descendente"""
    print("\n" + "=" * 60)
    print("CONSULTA 2: Ordenacion")
    print("Todos los productos ordenados por precio (mayor a menor)")
    print("=" * 60)

    results = collection.find().sort("precio", -1)

    for doc in results:
        print(f"  - {doc['nombre']}: ${doc['precio']} ({doc['categoria']})")


def query_with_aggregation(collection):
    """Agregacion: precio promedio y total de stock por categoria"""
    print("\n" + "=" * 60)
    print("CONSULTA 3: Agregacion")
    print("Precio promedio y stock total por categoria")
    print("=" * 60)

    pipeline = [
        {
            "$group": {
                "_id": "$categoria",
                "precio_promedio": {"$avg": "$precio"},
                "stock_total": {"$sum": "$stock"},
                "total_productos": {"$sum": 1},
            }
        },
        {"$sort": {"precio_promedio": -1}},
    ]

    results = collection.aggregate(pipeline)

    for doc in results:
        print(
            f"  - {doc['_id']}: "
            f"precio promedio ${doc['precio_promedio']:.2f}, "
            f"stock total {doc['stock_total']}, "
            f"{doc['total_productos']} productos"
        )


# ================================
# MAIN
# ================================

def main():
    print("=" * 60)
    print("PUNTO 3 - Amazon DocumentDB")
    print("=" * 60)

    # 1. Obtener credenciales de Secrets Manager
    username, password = get_docdb_credentials()

    # 2. Conectar a DocumentDB
    client = connect_to_documentdb(username, password)

    # 3. Crear base de datos y coleccion
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print(f"\nBase de datos: {DB_NAME}")
    print(f"Coleccion: {COLLECTION_NAME}")

    # 4. Insertar documentos
    insert_documents(collection)

    # 5. Consulta con filtro
    query_with_filter(collection)

    # 6. Consulta con ordenacion
    query_with_sort(collection)

    # 7. Consulta con agregacion
    query_with_aggregation(collection)

    # Cerrar conexion
    client.close()
    print("\n" + "=" * 60)
    print("Conexion cerrada. Fin del script.")
    print("=" * 60)


if __name__ == "__main__":
    main()
