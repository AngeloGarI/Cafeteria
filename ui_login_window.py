from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import sqlite3
from ui.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Cafeteria")
        self.resize(300, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.label_user = QLabel("Usuario:")
        self.input_user = QLineEdit()
        self.label_pass = QLabel("Contraseña:")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.button_login = QPushButton("Ingresar")
        self.button_login.clicked.connect(self.check_login)

        layout.addWidget(self.label_user)
        layout.addWidget(self.input_user)
        layout.addWidget(self.label_pass)
        layout.addWidget(self.input_pass)
        layout.addWidget(self.button_login)
        self.setLayout(layout)

    def check_login(self):
        user = self.input_user.text()
        password = self.input_pass.text()

        conn = sqlite3.connect("cafeteria.db")
        c = conn.cursor()
        c.execute("SELECT rol FROM usuarios WHERE usuario = ? AND contrasena=? ", (user, password))
        result = c.fetchone()
        conn.close()

        if result:
            rol = result[0]
            QMessageBox.information(self, "Acceso concedido", f"Bienvenido, {user}")
            self.main = MainWindow(rol)
            self.main.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos")