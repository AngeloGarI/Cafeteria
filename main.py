import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import sqlite3
import logging
import shutil
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from ui.login_window import LoginWindow

def setup_database():
    db_path = "cafeteria.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT UNIQUE NOT NULL,
                    contrasena TEXT NOT NULL,
                    rol TEXT NOT NULL
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS inventario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto TEXT UNIQUE NOT NULL,
                    categoria TEXT,
                    cantidad INTEGER NOT NULL,
                    precio REAL NOT NULL,
                    fecha_vencimiento TEXT
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto TEXT NOT NULL,
                    cantidad INTEGER NOT NULL,
                    total REAL NOT NULL,
                    fecha TEXT NOT NULL,
                    usuario TEXT NOT NULL  -- Nueva columna para rastrear quién vendió
                )''')

    try:
        c.execute("ALTER TABLE ventas ADD COLUMN usuario TEXT DEFAULT 'admin'")
    except sqlite3.OperationalError:
        pass

    # Índices para rendimiento
    c.execute("CREATE INDEX IF NOT EXISTS idx_producto ON inventario(producto)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_fecha ON inventario(fecha_vencimiento)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_venta_fecha ON ventas(fecha)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_venta_usuario ON ventas(usuario)")

    conn.commit()
    conn.close()

def setup_logging():
    logging.basicConfig(
        filename="cafeteria.log",
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def backup_database():
    db_path = "cafeteria.db"
    if os.path.exists(db_path):
        backup_path = f"backup_{datetime.now().strftime('%Y%m%d')}.db"
        shutil.copy(db_path, backup_path)
        print(f"Backup creado: {backup_path}")

if __name__ == "__main__":
    setup_logging()
    setup_database()
    backup_database()

    app = QApplication(sys.argv)
    try:
        with open("ui/styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

    window = LoginWindow()
    window.show()
    sys.exit(app.exec())