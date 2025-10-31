import sqlite3
import hashlib  # Agregado para hashing de contraseñas

def init_db():
    try:  # Agregado: Manejo de errores para evitar crashes
        conn = sqlite3.connect("cafeteria.db")
        c = conn.cursor()

        # Crear tabla usuarios si no existe (agregado para claridad)
        c.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                contrasena TEXT NOT NULL,
                rol TEXT NOT NULL
            );
        """)

        # Insertar usuario admin por defecto si no existe (con hash)
        c.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", ("admin",))
        if c.fetchone()[0] == 0:
            hashed_password = hashlib.sha256("1234".encode()).hexdigest()  # Hash de la contraseña por defecto
            c.execute("""
                INSERT INTO usuarios (usuario, contrasena, rol)
                VALUES (?, ?, ?)
            """, ("admin", hashed_password, "admin"))

        # Tabla de inventario
        c.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto TEXT NOT NULL,
                categoria TEXT,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL,
                fecha_vencimiento TEXT
            );
        """)

        # Tabla de ventas
        c.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                total REAL NOT NULL,
                fecha TEXT NOT NULL
            );
        """)

        conn.commit()
        conn.close()
        print("Base de datos creada correctamente ✅")
    except Exception as e:  # Agregado: Capturar errores
        print(f"Error al inicializar la base de datos: {e}")

if __name__ == "__main__":
    init_db()
