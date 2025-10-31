import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "database", "cafeteria.db")
print("Usando DB:", db_path)

conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("PRAGMA table_info(usuarios)")
print("Esquema de usuarios:")
for r in c.fetchall():
    print(r)
print("\nContenido de usuarios:")
c.execute("SELECT * FROM usuarios")
rows = c.fetchall()
for row in rows:
    print(row)
if not rows:
    print("-> No hay usuarios registrados.")
conn.close()
