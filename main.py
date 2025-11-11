import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import sqlite3
import logging
import shutil
import hashlib
import zipfile
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ui.login_window import LoginWindow
from database.db_init import init_db

def setup_logging():
    logging.basicConfig(
        filename="cafeteria.log",
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def backup_database():
    db_path = "cafeteria.db"
    if os.path.exists(db_path):
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(db_path, os.path.basename(db_path))
            print(f"Backup automático creado: {backup_path}")
        except Exception as e:
            print(f"Error en backup: {e}")

if __name__ == "__main__":
    setup_logging()
    init_db()
    backup_database()

    app = QApplication(sys.argv)
    try:
        with open("ui/styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

    backup_timer = QTimer()
    backup_timer.timeout.connect(backup_database)
    backup_timer.start(86400000)

    window = LoginWindow()
    window.show()
    sys.exit(app.exec())