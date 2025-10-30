import sqlite3

def init_db():
    conn = sqlite3.connect("cafeteria.db")
    c = conn.cursor()

    # Insertar usuario admin por defecto si no existe
    c.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", ("admin",))
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO usuarios (usuario, contrasena, rol)
            VALUES (?, ?, ?)
        """, ("admin", "1234", "admin"))

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