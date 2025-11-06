from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QDialog, QFormLayout
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
import sqlite3
import hashlib
from Cafeteria.ui.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Cafetería")
        self.resize(500, 450)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.attempts = 0
        self.max_attempts = 3
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_title = QLabel("LOGIN")
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #8B5E3C; margin-bottom: 10px;")
        layout.addWidget(login_title)

        logo_label = QLabel()
        logo_pixmap = QPixmap("ui/assets/Login.jpg").scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Nombre de usuario")
        self.input_user.setStyleSheet("padding: 10px; font-size: 14px; border: 1px solid #BDBDBD; border-radius: 5px;")
        self.input_user.returnPressed.connect(self.check_login)
        layout.addWidget(self.input_user)

        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Contraseña")
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.setStyleSheet("padding: 10px; font-size: 14px; border: 1px solid #BDBDBD; border-radius: 5px;")
        self.input_pass.addAction(QIcon("ui/assets/lock.png"), QLineEdit.ActionPosition.TrailingPosition)
        self.input_pass.returnPressed.connect(self.check_login)
        layout.addWidget(self.input_pass)

        self.button_login = QPushButton("Ingresar")
        self.button_login.setStyleSheet("""
            background-color: #8B5E3C;  /* Café */
            color: white;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 8px;
        """)
        self.button_login.clicked.connect(self.check_login)
        layout.addWidget(self.button_login)

        self.button_forgot = QPushButton("¿Olvidaste tu contraseña?")
        self.button_forgot.setStyleSheet("color: #2196F3; border: none; text-decoration: underline;")
        self.button_forgot.clicked.connect(self.forgot_password)
        layout.addWidget(self.button_forgot)

        self.setLayout(layout)

    def check_login(self):
        usuario = self.input_user.text().strip()
        contrasena = self.input_pass.text().strip()

        if not usuario or not contrasena:
            QMessageBox.warning(self, "Error", "Completa todos los campos.")
            return

        if self.attempts >= self.max_attempts:
            QMessageBox.warning(self, "Bloqueado", "Demasiados intentos fallidos. Intenta más tarde.")
            return

        if not usuario.isalnum():
            QMessageBox.warning(self, "Error", "Usuario inválido.")
            return

        try:
            conn = sqlite3.connect("cafeteria.db")
            c = conn.cursor()
            hashed_contrasena = hashlib.sha256(contrasena.encode()).hexdigest()
            c.execute("SELECT rol FROM usuarios WHERE usuario = ? AND contrasena = ?", (usuario, hashed_contrasena))
            result = c.fetchone()
            conn.close()

            if result:
                rol = result[0]
                if rol not in ["admin", "empleado"]:
                    QMessageBox.warning(self, "Error", "Rol no autorizado.")
                    return
                self.open_main_window(rol)
            else:
                self.attempts += 1
                remaining = self.max_attempts - self.attempts
                QMessageBox.warning(self, "Error", f"Usuario o contraseña incorrectos. Intentos restantes: {remaining}")
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