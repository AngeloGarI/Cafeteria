from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMenuBar, QMessageBox, QDialog, QFormLayout, QLineEdit, QComboBox, QPushButton, QLabel
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from Cafeteria.modules.inventory import InventoryWindow
from Cafeteria.modules.sales import SalesWindow
from Cafeteria.modules.reports import ReportsWindow
import sqlite3
import hashlib

class MainWindow(QMainWindow):
    def __init__(self, rol):
        super().__init__()
        self.setWindowTitle("Sistema de Cafetería - Profesional")
        self.resize(1000, 700)
        self.rol = rol
        self.animation = None
        self.setup_ui()
        self.setup_menu()
        self.animate_tabs()

    def setup_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #C8A97E; background: #F5F0E6; }
            QTabBar::tab { background: #8B5E3C; color: white; padding: 10px; border-radius: 5px; margin: 2px; }
            QTabBar::tab:selected { background: #A97455; }
            QTabBar::tab:hover { background: #6B4226; }
        """)

        self.inventory_tab = InventoryWindow(self.rol)
        self.sales_tab = SalesWindow()
        self.reports_tab = ReportsWindow()

        self.tabs.addTab(self.inventory_tab, QIcon("icons/inventory.png"), "Inventario")
        self.tabs.addTab(self.sales_tab, QIcon("icons/sales.png"), "Ventas")
        self.tabs.addTab(self.reports_tab, QIcon("icons/reports.png"), "Reportes")

        self.tabs.currentChanged.connect(self.on_tab_changed)

        if self.rol != "admin":
            self.tabs.setTabEnabled(0, False)
            access_label = QLabel("Acceso: Solo Ventas y Reportes")
            access_label.setStyleSheet("font-size: 14px; color: #3E2C1C; font-weight: bold; margin: 10px;")
            access_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sales_tab.layout().insertWidget(0, access_label)  # Agrega arriba en Ventas

        self.setCentralWidget(self.tabs)

    def on_tab_changed(self, index):
        if index == 0:
            self.inventory_tab.refresh_data()
        elif index == 1:
            self.sales_tab.load_products_safe()

    def setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Archivo")
        view_menu = menubar.addMenu("Vista")

        exit_action = QAction(QIcon("icons/exit.png"), "Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        if self.rol == "admin":
            create_user_action = QAction("Crear Usuario", self)
            create_user_action.triggered.connect(self.create_user)
            file_menu.addAction(create_user_action)

        theme_action = QAction("Cambiar Tema", self)
        theme_action.triggered.connect(lambda: QMessageBox.information(self, "Tema", "Función próximamente"))
        view_menu.addAction(theme_action)

    def animate_tabs(self):
        if self.animation is None:
            self.animation = QPropertyAnimation(self, b"windowOpacity")
            self.animation.setDuration(500)
            self.animation.setStartValue(0.0)
            self.animation.setEndValue(1.0)
            self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.animation.start()

    def create_user(self):
        dialog = CreateUserDialog()
        dialog.exec()

class CreateUserDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crear Nuevo Usuario")
        self.resize(300, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Nuevo usuario")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.setPlaceholderText("Contraseña")
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "empleado"])
        self.button_create = QPushButton("Crear")
        self.button_create.clicked.connect(self.create_user)

        layout.addRow("Usuario:", self.input_user)
        layout.addRow("Contraseña:", self.input_pass)
        layout.addRow("Rol:", self.role_combo)
        layout.addRow(self.button_create)
        self.setLayout(layout)

    def create_user(self):
        user = self.input_user.text().strip()
        password = self.input_pass.text().strip()
        rol = self.role_combo.currentText()

        if not user or not password:
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return

        if not user.isalnum():
            QMessageBox.warning(self, "Error", "Usuario debe ser alfanumérico")
            return

        try:
            conn = sqlite3.connect("cafeteria.db")
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", (user,))
            if c.fetchone()[0] > 0:
                QMessageBox.warning(self, "Error", "Usuario ya existe")
                conn.close()
                return

            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            c.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)", (user, hashed_password, rol))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Éxito", f"Usuario '{user}' creado con rol '{rol}'")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al crear usuario:\n{e}")