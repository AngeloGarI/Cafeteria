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

        c.execute("PRAGMA table_info(ventas)")
        columns = [col[1] for col in c.fetchall()]
        if "usuario" not in columns:
            print("Migrando tabla ventas para agregar columna usuario...")
            c.execute("CREATE TABLE IF NOT EXISTS ventas_temp AS SELECT * FROM ventas")
            c.execute("""
                CREATE TABLE ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto TEXT NOT NULL,
                    cantidad INTEGER NOT NULL,
                    total REAL NOT NULL,
                    fecha TEXT NOT NULL,
                    usuario TEXT NOT NULL DEFAULT 'admin'
                );
            """)
            # Migrar datos
            c.execute("INSERT INTO ventas (producto, cantidad, total, fecha) SELECT producto, cantidad, total, fecha FROM ventas_temp")
            c.execute("DROP TABLE ventas_temp")
            print("Migración completada.")

        # Crear tabla ventas si no existe (con columna usuario)
        c.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                total REAL NOT NULL,
                fecha TEXT NOT NULL,
                usuario TEXT NOT NULL
            );
        """)

        c.execute("CREATE INDEX IF NOT EXISTS idx_producto ON inventario(producto)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_fecha ON inventario(fecha_vencimiento)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_venta_fecha ON ventas(fecha)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_venta_usuario ON ventas(usuario)")

        conn.commit()
        conn.close()
        print("Base de datos inicializada correctamente ✅")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

if __name__ == "__main__":
    init_db()