import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from PyQt6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from database.db_init import init_db

if __name__ == "__main__":
    init_db()  # Inicializa DB si no existe
    app = QApplication(sys.argv)
    with open("ui/styles.qss", "r", encoding="utf-8") as f:  # Encoding UTF-8 para caracteres Unicode
        app.setStyleSheet(f.read())  # Carga estilos globales
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())