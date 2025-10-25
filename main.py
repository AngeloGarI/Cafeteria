import sys
from PyQt6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from database.db_init import init_db

if __name__ == "__main__":
    init_db()  # crea base de datos si no existe
    app = QApplication(sys.argv)
    with open("ui/styles.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
