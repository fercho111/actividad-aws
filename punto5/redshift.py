#!/usr/bin/env python3
"""
Punto 5 - Amazon Redshift
Sube datos a S3, crea tablas en Redshift, carga con COPY,
y ejecuta consultas con filtro, join y agregacion usando la Data API.
"""

import boto3
import time
import os

# ================================
# CONFIGURACION
# ================================

REGION = "us-east-1"
WORKGROUP_NAME = "punto5-workgroup"
DATABASE = "dev"
S3_BUCKET = "redshift-punto5-data"

SECRET_ARN = "arn:aws:secretsmanager:us-east-1:596953736802:secret:redshift!punto5-namespace-admin-N5Rw1y"
IAM_ROLE_ARN = "arn:aws:iam::596953736802:role/punto5-taller-aws"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


# ================================
# CLIENTES
# ================================

s3_client = boto3.client("s3", region_name=REGION)
redshift_data = boto3.client("redshift-data", region_name=REGION)


# ================================
# FUNCIONES AUXILIARES
# ================================

def upload_to_s3(local_file, s3_key):
    """Subir archivo a S3"""
    s3_client.upload_file(local_file, S3_BUCKET, s3_key)
    print(f"  Subido: {local_file} -> s3://{S3_BUCKET}/{s3_key}")


def execute_sql(sql, description=""):
    """Ejecutar SQL en Redshift via Data API y esperar resultado"""
    if description:
        print(f"\n  Ejecutando: {description}...")

    response = redshift_data.execute_statement(
        WorkgroupName=WORKGROUP_NAME,
        Database=DATABASE,
        SecretArn=SECRET_ARN,
        Sql=sql,
    )
    query_id = response["Id"]

    # Esperar a que termine
    while True:
        status = redshift_data.describe_statement(Id=query_id)
        state = status["Status"]
        if state == "FINISHED":
            break
        elif state == "FAILED":
            print(f"  ERROR: {status.get('Error', 'Unknown error')}")
            return None
        time.sleep(1)

    if description:
        print(f"  Completado: {description}")
    return query_id


def get_results(query_id):
    """Obtener resultados de una consulta ejecutada"""
    response = redshift_data.get_statement_result(Id=query_id)
    columns = [col["name"] for col in response["ColumnMetadata"]]
    rows = []
    for record in response["Records"]:
        row = []
        for field in record:
            # Extraer el valor del campo (puede ser stringValue, longValue, etc.)
            value = list(field.values())[0]
            row.append(value)
        rows.append(row)
    return columns, rows


def print_table(columns, rows, title=""):
    """Imprimir resultados como tabla"""
    if title:
        print(f"\n  {title}")
        print(f"  {'=' * 70}")

    # Calcular anchos
    widths = [len(c) for c in columns]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))

    # Header
    header = "  " + " | ".join(c.ljust(w) for c, w in zip(columns, widths))
    print(header)
    print("  " + "-+-".join("-" * w for w in widths))

    # Rows
    for row in rows:
        print("  " + " | ".join(str(v).ljust(w) for v, w in zip(row, widths)))

    print(f"  ({len(rows)} filas)")


# ================================
# PASO 1: SUBIR DATOS A S3
# ================================

def step_upload_data():
    """Subir archivos CSV a S3"""
    print("\n" + "=" * 60)
    print("PASO 1: Subir datos a S3")
    print("=" * 60)

    upload_to_s3(os.path.join(DATA_DIR, "productos.csv"), "productos.csv")
    upload_to_s3(os.path.join(DATA_DIR, "ventas.csv"), "ventas.csv")


# ================================
# PASO 2: CREAR TABLAS
# ================================

def step_create_tables():
    """Crear tablas en Redshift"""
    print("\n" + "=" * 60)
    print("PASO 2: Crear tablas en Redshift")
    print("=" * 60)

    # Drop si existen
    execute_sql("DROP TABLE IF EXISTS ventas", "DROP ventas")
    execute_sql("DROP TABLE IF EXISTS productos", "DROP productos")

    # Crear tabla productos
    execute_sql("""
        CREATE TABLE productos (
            producto_id INTEGER PRIMARY KEY,
            nombre VARCHAR(100),
            categoria VARCHAR(50),
            precio_unitario DECIMAL(10,2)
        )
    """, "CREATE productos")

    # Crear tabla ventas
    execute_sql("""
        CREATE TABLE ventas (
            venta_id INTEGER PRIMARY KEY,
            producto_id INTEGER,
            cantidad INTEGER,
            precio_total DECIMAL(10,2),
            fecha DATE
        )
    """, "CREATE ventas")


# ================================
# PASO 3: CARGAR DATOS CON COPY
# ================================

def step_load_data():
    """Cargar datos desde S3 usando COPY"""
    print("\n" + "=" * 60)
    print("PASO 3: Cargar datos con COPY desde S3")
    print("=" * 60)

    execute_sql(f"""
        COPY productos
        FROM 's3://{S3_BUCKET}/productos.csv'
        IAM_ROLE '{IAM_ROLE_ARN}'
        CSV
        IGNOREHEADER 1
        REGION '{REGION}'
    """, "COPY productos")

    execute_sql(f"""
        COPY ventas
        FROM 's3://{S3_BUCKET}/ventas.csv'
        IAM_ROLE '{IAM_ROLE_ARN}'
        CSV
        IGNOREHEADER 1
        REGION '{REGION}'
    """, "COPY ventas")

    # Verificar conteos
    qid = execute_sql("SELECT COUNT(*) as total FROM productos")
    cols, rows = get_results(qid)
    print(f"\n  Productos cargados: {rows[0][0]}")

    qid = execute_sql("SELECT COUNT(*) as total FROM ventas")
    cols, rows = get_results(qid)
    print(f"  Ventas cargadas: {rows[0][0]}")


# ================================
# PASO 4: CONSULTAS
# ================================

def step_queries():
    """Ejecutar consultas con filtro, join y agregacion"""
    print("\n" + "=" * 60)
    print("PASO 4: Ejecutar consultas")
    print("=" * 60)

    # ----- CONSULTA 1: FILTRO -----
    # Pregunta: Cuales son las ventas de productos de electronica
    # con precio total mayor a $100?
    print("\n" + "-" * 60)
    print("  CONSULTA 1: Filtro")
    print("  Pregunta: Ventas de electronica con precio total > $100")
    print("-" * 60)

    qid = execute_sql("""
        SELECT v.venta_id, p.nombre, v.cantidad, v.precio_total, v.fecha
        FROM ventas v
        JOIN productos p ON v.producto_id = p.producto_id
        WHERE p.categoria = 'electronica'
          AND v.precio_total > 100
        ORDER BY v.precio_total DESC
    """)
    cols, rows = get_results(qid)
    print_table(cols, rows, "Ventas de electronica con precio > $100")
    print("\n  Interpretacion: Se muestran las ventas mas grandes de")
    print("  productos electronicos. Las laptops dominan con $1200 por venta.")

    # ----- CONSULTA 2: JOIN -----
    # Pregunta: Detalle completo de cada venta con nombre de producto
    # y categoria
    print("\n" + "-" * 60)
    print("  CONSULTA 2: Join")
    print("  Pregunta: Detalle de ventas con info del producto")
    print("-" * 60)

    qid = execute_sql("""
        SELECT v.venta_id, p.nombre, p.categoria, v.cantidad,
               p.precio_unitario, v.precio_total, v.fecha
        FROM ventas v
        JOIN productos p ON v.producto_id = p.producto_id
        ORDER BY v.fecha, v.venta_id
    """)
    cols, rows = get_results(qid)
    print_table(cols, rows, "Detalle completo de ventas")
    print("\n  Interpretacion: Se combinan las tablas ventas y productos")
    print("  para tener el detalle completo de cada transaccion.")

    # ----- CONSULTA 3: AGREGACION -----
    # Pregunta: Cual es el ingreso total y cantidad de ventas por
    # categoria de producto?
    print("\n" + "-" * 60)
    print("  CONSULTA 3: Agregacion")
    print("  Pregunta: Ingreso total y cantidad de ventas por categoria")
    print("-" * 60)

    qid = execute_sql("""
        SELECT p.categoria,
               COUNT(v.venta_id) AS total_ventas,
               SUM(v.cantidad) AS unidades_vendidas,
               SUM(v.precio_total) AS ingreso_total,
               ROUND(AVG(v.precio_total), 2) AS ticket_promedio
        FROM ventas v
        JOIN productos p ON v.producto_id = p.producto_id
        GROUP BY p.categoria
        ORDER BY ingreso_total DESC
    """)
    cols, rows = get_results(qid)
    print_table(cols, rows, "Ingreso por categoria")
    print("\n  Interpretacion: Electronica es la categoria con mayor ingreso")
    print("  total, seguida por muebles. Iluminacion tiene el menor volumen.")


# ================================
# MAIN
# ================================

def main():
    print("=" * 60)
    print("PUNTO 5 - Amazon Redshift")
    print("=" * 60)

    step_upload_data()
    step_create_tables()
    step_load_data()
    step_queries()

    print("\n" + "=" * 60)
    print("Fin del script.")
    print("=" * 60)


if __name__ == "__main__":
    main()
