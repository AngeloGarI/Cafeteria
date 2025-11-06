import sqlite3
import hashlib

def init_db():
    try:
        conn = sqlite3.connect("cafeteria.db")
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                contrasena TEXT NOT NULL,
                rol TEXT NOT NULL
            );
        """)

        c.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", ("admin",))
        if c.fetchone()[0] == 0:
            hashed_password = hashlib.sha256("1234".encode()).hexdigest()
            c.execute("""
                INSERT INTO usuarios (usuario, contrasena, rol)
                VALUES (?, ?, ?)
            """, ("admin", hashed_password, "admin"))

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
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

if __name__ == "__main__":
    init_db()