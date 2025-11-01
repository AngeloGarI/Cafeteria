from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QDialog, QFormLayout
import sqlite3
import hashlib  # Para hashing de contraseñas (seguridad)
from Cafeteria.ui.main_window import MainWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Cafeteria")
        self.resize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.label_user = QLabel("Usuario:")
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Ingresa tu usuario")
        self.label_pass = QLabel("Contraseña:")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.setPlaceholderText("Ingresa tu contraseña")
        self.button_login = QPushButton("Ingresar")
        self.button_login.clicked.connect(self.check_login)

        self.button_forgot = QPushButton("¿Olvidaste tu contraseña?")
        self.button_forgot.clicked.connect(self.forgot_password)

        layout.addWidget(self.label_user)
        layout.addWidget(self.input_user)
        layout.addWidget(self.label_pass)
        layout.addWidget(self.input_pass)
        layout.addWidget(self.button_login)
        layout.addWidget(self.button_forgot)
        self.setLayout(layout)

    def check_login(self):
        usuario = self.input_user.text().strip()
        contrasena = self.input_pass.text().strip()

        if not usuario or not contrasena:
            QMessageBox.warning(self, "Error", "Completa todos los campos.")
            return

        # Validación extra: Usuario alfanumérico
        if not usuario.isalnum():
            QMessageBox.warning(self, "Error", "Usuario inválido.")
            return

        try:
            conn = sqlite3.connect("cafeteria.db")
            c = conn.cursor()
            # Hashing para seguridad (algoritmo de encriptación)
            hashed_contrasena = hashlib.sha256(contrasena.encode()).hexdigest()
            c.execute("SELECT rol FROM usuarios WHERE usuario = ? AND contrasena = ?", (usuario, hashed_contrasena))
            result = c.fetchone()
            conn.close()

            if result:
                rol = result[0]
                # Validación de rol
                if rol not in ["admin", "empleado"]:
                    QMessageBox.warning(self, "Error", "Rol no autorizado.")
                    return
                self.open_main_window(rol)
            else:
                QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")
                self.input_pass.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Problema de conexión: {e}")

    def open_main_window(self, rol):
        self.main = MainWindow(rol)
        self.main.show()
        self.close()

    def forgot_password(self):
        dialog = ForgotPasswordDialog()
        dialog.exec()


class ForgotPasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cambiar Contraseña")
        self.resize(300, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        self.label_user = QLabel("Usuario:")
        self.input_user = QLineEdit()
        self.label_new_pass = QLabel("Nueva Contraseña:")
        self.input_new_pass = QLineEdit()
        self.input_new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.button_change = QPushButton("Cambiar")
        self.button_change.clicked.connect(self.change_password)

        layout.addRow(self.label_user, self.input_user)
        layout.addRow(self.label_new_pass, self.input_new_pass)
        layout.addRow(self.button_change)
        self.setLayout(layout)

    def change_password(self):
        user = self.input_user.text().strip()
        new_password = self.input_new_pass.text().strip()

        if not user or not new_password:
            QMessageBox.warning(self, "¡Ups!", "Completa todos los campos")
            return

        try:
            conn = sqlite3.connect("cafeteria.db")
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", (user,))
            if c.fetchone()[0] == 0:
                QMessageBox.warning(self, "¡Ups!", "Usuario no encontrado")
                conn.close()
                return

            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
            c.execute("UPDATE usuarios SET contrasena = ? WHERE usuario = ?", (hashed_new_password, user))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "¡Listo!", "Contraseña cambiada correctamente")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cambiar contraseña:\n{e}")
