import sqlite3

def init_db():
    conn = sqlite3.connect("database/cafeteria.db")
    c = conn.cursor()

    # Tabla de usuarios
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL
        );
    """)

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

if __name__ == "__main__":
    init_db()
    print("Base de datos creada correctamente ✅")