
from gremlin_python.driver import client, serializer
import ssl


# ================================
# CONFIGURACION
# ================================

NEPTUNE_ENDPOINT = "wss://localhost:8182/gremlin"


# ================================
# CONEXION
# ================================

def get_client():
    """Conectar a Neptune via tunel SSH (localhost:8182)"""
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    c = client.Client(
        NEPTUNE_ENDPOINT,
        "g",
        ssl_options=ssl_context,
    )
    count = c.submit("g.V().count()").all().result()
    print(f"Conexion exitosa a Neptune. Vertices actuales: {count[0]}")
    return c


def run(c, query):
    """Ejecutar una consulta Gremlin y retornar resultados"""
    return c.submit(query).all().result()


def add_edge(c, src_label, src_name, edge_label, dst_label, dst_name):
    """Crear una arista entre dos vertices usando as/from pattern"""
    query = (
        f"g.V().has('{src_label}','nombre','{src_name}').as('a')"
        f".V().has('{dst_label}','nombre','{dst_name}')"
        f".addE('{edge_label}').from('a')"
    )
    return run(c, query)


# ================================
# CREAR GRAFO
# ================================

def clear_graph(c):
    """Eliminar todos los vertices y aristas existentes"""
    run(c, "g.V().drop()")
    print("Grafo limpiado")


def create_vertices(c):
    """Crear 11 vertices: 4 estudiantes, 3 profesores, 4 cursos"""

    print("\nCreando vertices...")

    # Estudiantes (4)
    students = [
        ("Ana",    "9-semestre", "Ing-Datos"),
        ("Carlos", "8-semestre", "Ing-Datos"),
        ("Maria",  "9-semestre", "Ing-Sistemas"),
        ("Pedro",  "7-semestre", "Ing-Sistemas"),
    ]
    for name, semester, program in students:
        run(c, f"g.addV('estudiante').property('nombre','{name}').property('semestre','{semester}').property('programa','{program}')")
        print(f"  + Estudiante: {name}")

    # Profesores (3)
    professors = [
        ("Dr-Lopez",    "Bases-de-Datos"),
        ("Dr-Garcia",   "Redes"),
        ("Dr-Martinez", "Inteligencia-Artificial"),
    ]
    for name, specialty in professors:
        run(c, f"g.addV('profesor').property('nombre','{name}').property('especialidad','{specialty}')")
        print(f"  + Profesor: {name}")

    # Cursos (4)
    courses = [
        ("BaseDatos",   "BD-101", 4),
        ("Redes",       "RED-201", 3),
        ("IA",          "IA-301", 4),
        ("IngDatos",    "ID-401", 3),
    ]
    for name, code, credits in courses:
        run(c, f"g.addV('curso').property('nombre','{name}').property('codigo','{code}').property('creditos',{credits})")
        print(f"  + Curso: {name}")

    total = run(c, "g.V().count()")[0]
    print(f"\nTotal vertices creados: {total}")


# Mapeo de nombres cortos a nombres legibles
DISPLAY_NAMES = {
    "BaseDatos": "Bases de Datos",
    "IngDatos": "Ingenieria de Datos",
    "IA": "Inteligencia Artificial",
    "Redes": "Redes",
    "Dr-Lopez": "Dr. Lopez",
    "Dr-Garcia": "Dr. Garcia",
    "Dr-Martinez": "Dr. Martinez",
}

def display(name):
    return DISPLAY_NAMES.get(name, name)


def create_edges(c):
    """Crear 16 aristas (relaciones) entre los vertices"""

    print("\nCreando relaciones...")

    # CURSA: estudiante -> curso (8 relaciones)
    cursa_edges = [
        ("Ana",    "BaseDatos"),
        ("Ana",    "IngDatos"),
        ("Carlos", "BaseDatos"),
        ("Carlos", "IA"),
        ("Maria",  "Redes"),
        ("Maria",  "IA"),
        ("Pedro",  "Redes"),
        ("Pedro",  "IngDatos"),
    ]
    for student, course in cursa_edges:
        add_edge(c, "estudiante", student, "CURSA", "curso", course)
        print(f"  + {student} --CURSA--> {display(course)}")

    # IMPARTE: profesor -> curso (4 relaciones)
    teaches_edges = [
        ("Dr-Lopez",    "BaseDatos"),
        ("Dr-Lopez",    "IngDatos"),
        ("Dr-Garcia",   "Redes"),
        ("Dr-Martinez", "IA"),
    ]
    for prof, course in teaches_edges:
        add_edge(c, "profesor", prof, "IMPARTE", "curso", course)
        print(f"  + {display(prof)} --IMPARTE--> {display(course)}")

    # AMIGO_DE: estudiante <-> estudiante (4 relaciones)
    friend_edges = [
        ("Ana",    "Carlos"),
        ("Ana",    "Maria"),
        ("Carlos", "Pedro"),
        ("Maria",  "Pedro"),
    ]
    for s1, s2 in friend_edges:
        add_edge(c, "estudiante", s1, "AMIGO_DE", "estudiante", s2)
        print(f"  + {s1} --AMIGO_DE--> {s2}")

    total = run(c, "g.E().count()")[0]
    print(f"\nTotal relaciones creadas: {total}")


# ================================
# CONSULTAS
# ================================


def query_1(c):
    """Consulta 1: Encontrar todos los cursos que Ana cursa y quien los imparte
    Recorrido: estudiante -CURSA-> curso <-IMPARTE- profesor
    """
    print("\n" + "=" * 60)
    print("CONSULTA 1: Cursos de Ana y sus profesores")
    print("Recorrido: Ana --CURSA--> curso <--IMPARTE-- profesor")
    print("=" * 60)

    courses = run(c,
        "g.V().has('estudiante','nombre','Ana')"
        ".out('CURSA').values('nombre')"
    )
    print(f"\n  Cursos que Ana cursa:")
    for course in courses:
        print(f"    - {display(course)}")

        profs = run(c,
            f"g.V().has('curso','nombre','{course}')"
            f".in('IMPARTE').values('nombre')"
        )
        for prof in profs:
            print(f"      Impartido por: {display(prof)}")


def query_2(c):
    """Consulta 2: Amigos de Carlos y los cursos que ellos toman
    Recorrido: estudiante -AMIGO_DE-> estudiante -CURSA-> curso
    (2 saltos de relacion)
    """
    print("\n" + "=" * 60)
    print("CONSULTA 2: Amigos de Carlos y sus cursos")
    print("Recorrido: Carlos --AMIGO_DE--> amigo --CURSA--> curso")
    print("=" * 60)

    friends = run(c,
        "g.V().has('estudiante','nombre','Carlos')"
        ".out('AMIGO_DE').values('nombre')"
    )

    print(f"\n  Amigos de Carlos:")
    for friend in friends:
        courses = run(c,
            f"g.V().has('estudiante','nombre','{friend}')"
            f".out('CURSA').values('nombre')"
        )
        print(f"    - {display(friend)} cursa:")
        for course in courses:
            print(f"        * {display(course)}")


def query_3(c):
    """Consulta 3: Para cada curso, contar cuantos estudiantes lo cursan
    y mostrar el profesor. Ordenar por cantidad de estudiantes.
    Recorrido: curso <-CURSA- estudiante, curso <-IMPARTE- profesor
    """
    print("\n" + "=" * 60)
    print("CONSULTA 3: Popularidad de cursos (estudiantes por curso)")
    print("Recorrido: curso <--CURSA-- estudiantes, curso <--IMPARTE-- profesor")
    print("=" * 60)

    courses = run(c, "g.V().hasLabel('curso').values('nombre')")

    results = []
    for course in courses:
        student_count = run(c,
            f"g.V().has('curso','nombre','{course}')"
            f".in('CURSA').count()"
        )[0]

        students = run(c,
            f"g.V().has('curso','nombre','{course}')"
            f".in('CURSA').values('nombre')"
        )

        profs = run(c,
            f"g.V().has('curso','nombre','{course}')"
            f".in('IMPARTE').values('nombre')"
        )
        prof = display(profs[0]) if profs else "Sin asignar"

        results.append((display(course), student_count, [display(s) for s in students], prof))

    results.sort(key=lambda x: x[1], reverse=True)

    print()
    for course, count, students, prof in results:
        print(f"  {course} ({count} estudiantes) - Profesor: {prof}")
        for s in students:
            print(f"    - {s}")


# ================================
# MAIN
# ================================

def main():
    print("=" * 60)
    print("PUNTO 4 - Amazon Neptune")
    print("=" * 60)

    # Conectar
    c = get_client()

    # Limpiar grafo
    clear_graph(c)

    # Crear vertices y aristas
    create_vertices(c)
    create_edges(c)

    # Ejecutar consultas
    query_1(c)
    query_2(c)
    query_3(c)

    # Cerrar
    c.close()
    print("\n" + "=" * 60)
    print("Conexion cerrada. Fin del script.")
    print("=" * 60)


if __name__ == "__main__":
    main()
