from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QDialog, QFormLayout
import sqlite3
import hashlib  # Para hashing de contraseñas (seguridad básica)
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
        self.label_pass = QLabel("Contraseña:")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.button_login = QPushButton("Ingresar")
        self.button_login.clicked.connect(self.check_login)

        # Agregar botón para "Olvidé mi contraseña" (nueva línea)
        self.button_forgot = QPushButton("Olvidé mi contraseña")
        self.button_forgot.clicked.connect(self.forgot_password)

        layout.addWidget(self.label_user)
        layout.addWidget(self.input_user)
        layout.addWidget(self.label_pass)
        layout.addWidget(self.input_pass)
        layout.addWidget(self.button_login)
        layout.addWidget(self.button_forgot)  # Agregar al layout (nueva línea)
        self.setLayout(layout)

    def check_login(self):
        user = self.input_user.text().strip()  # Agregué .strip() para mejor validación
        password = self.input_pass.text().strip()

        # Validación básica: Campos no vacíos (opcional, pero recomendado)
        if not user or not password:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos")
            return

        try:
            conn = sqlite3.connect("cafeteria.db")
            c = conn.cursor()
            # Usar hashing para comparar (seguridad mejorada)
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            c.execute("SELECT rol FROM usuarios WHERE usuario = ? AND contrasena=? ", (user, hashed_password))
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
                self.input_pass.clear()  # Limpiar contraseña por seguridad
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al conectar con la base de datos:\n{e}")

    # Nuevo método para manejar "Olvidé mi contraseña"
    def forgot_password(self):
        dialog = ForgotPasswordDialog()
        dialog.exec()


# Nueva clase para el diálogo de cambio de contraseña
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
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return

        try:
            conn = sqlite3.connect("cafeteria.db")
            c = conn.cursor()
            # Verificar si el usuario existe
            c.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", (user,))
            if c.fetchone()[0] == 0:
                QMessageBox.warning(self, "Error", "Usuario no encontrado")
                conn.close()
                return

            # Hash de la nueva contraseña y actualizar
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
            c.execute("UPDATE usuarios SET contrasena = ? WHERE usuario = ?", (hashed_new_password, user))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Éxito", "Contraseña cambiada correctamente")
            self.accept()  # Cerrar el diálogo
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cambiar contraseña:\n{e}")