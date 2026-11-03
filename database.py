# Archivo: database.py
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "290408",   # Tu contraseña configurada en MySQL Workbench
}
DB_NAME = "geoluz_db"


def obtener_conexion():
    """Devuelve una conexión a geoluz_db, o None si MySQL no está disponible."""
    try:
        return mysql.connector.connect(**DB_CONFIG, database=DB_NAME)
    except mysql.connector.Error as err:
        print(f"❌ No se pudo conectar a MySQL: {err}")
        return None


def inicializar_base_datos():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                username VARCHAR(50) PRIMARY KEY,
                password VARCHAR(255) NOT NULL,
                nombre_completo VARCHAR(100) NOT NULL,
                proveedor VARCHAR(30) NOT NULL DEFAULT 'Local'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reportes (
                id_reporte VARCHAR(50) PRIMARY KEY,
                usuario VARCHAR(100) NOT NULL,
                telefono VARCHAR(30) NOT NULL,
                comarca_ubicacion VARCHAR(150) NOT NULL,
                tipo_falla VARCHAR(100) NOT NULL,
                descripcion TEXT NOT NULL,
                estado VARCHAR(50) NOT NULL,
                fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # MIGRACIÓN: si la tabla ya existía sin la columna fecha_hora, se agrega
        # (los reportes antiguos quedan con la fecha/hora del momento de la migración).
        cursor.execute("SHOW COLUMNS FROM reportes LIKE 'fecha_hora'")
        if cursor.fetchone() is None:
            cursor.execute(
                "ALTER TABLE reportes ADD COLUMN fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"
            )

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Base de datos 'geoluz_db' e infraestructura configuradas exitosamente.")
    except mysql.connector.Error as err:
        print(f"❌ Error al conectar o inicializar MySQL: {err}")


def agregar_usuario(username, password, nombre_completo, proveedor="Local"):
    conn = obtener_conexion()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO usuarios (username, password, nombre_completo, proveedor)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                password=VALUES(password),
                nombre_completo=VALUES(nombre_completo),
                proveedor=VALUES(proveedor)
        """
        cursor.execute(sql, (username, password, nombre_completo, proveedor))
        conn.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"❌ Error al guardar usuario en MySQL: {err}")
    finally:
        conn.close()


if __name__ == "__main__":
    inicializar_base_datos()
    agregar_usuario("admin", "admin123", "Juan Carlos Castillo", "Local")
    agregar_usuario("supervisor", "geo2026", "Ing. Operaciones Georeferenciadas", "Local")