import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    #tabla de usuarios
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              usuario TEXT UNIQUE NOT NULL,
              contrasena TEXT NOT NULL,
              rol TEXT NOT NULL
        )
""")

    #usuario inicial
    c.execute("Select * From usuarios WHERE usuario = 'admin'")

    if not c.fetchone():
        c.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES ('admin', '1234', 'admin')")

        # Tabla de inventario
    c.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT,
                cantidad INTEGER,
                precio REAL
            )
        """)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Base de datos inicializada correctamente.")