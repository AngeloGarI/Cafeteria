from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMenuBar, QMessageBox, QDialog, QFormLayout, QLineEdit, QComboBox, QPushButton, QLabel
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QTimer
from Cafeteria.modules.inventory import InventoryWindow
from Cafeteria.modules.sales import SalesWindow
from Cafeteria.modules.reports import ReportsWindow
from Cafeteria.modules.dashboard import DashboardWindow
import sqlite3
import hashlib

class MainWindow(QMainWindow):
    def __init__(self, rol):
        super().__init__()
        self.setWindowTitle("Sistema de Cafetería - Profesional")
        self.resize(1000, 700)
        self.rol = rol
        self.animation = None
        self.dark_mode = False
        self.setup_ui()
        self.setup_menu()
        self.animate_tabs()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_alerts)
        self.timer.start(3600000)

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
        self.dashboard_tab = DashboardWindow()

        self.tabs.addTab(self.inventory_tab, QIcon("ui/assets/Inventario.jpg"), "Inventario")
        self.tabs.addTab(self.sales_tab, QIcon("ui/assets/Ventas.jpg"), "Ventas")
        self.tabs.addTab(self.reports_tab, QIcon("ui/assets/Reportes.jpg"), "Reportes")
        self.tabs.addTab(self.dashboard_tab, "Dashboard")

        self.tabs.currentChanged.connect(self.on_tab_changed)

        if self.rol != "admin":
            self.tabs.setTabEnabled(0, False)
            access_label = QLabel("Acceso: Solo Ventas y Reportes")
            access_label.setStyleSheet("font-size: 14px; color: #3E2C1C; font-weight: bold; margin: 10px;")
            access_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sales_tab.layout().insertWidget(0, access_label)

        self.setCentralWidget(self.tabs)

    def on_tab_changed(self, index):
        if index == 0:
            self.inventory_tab.refresh_data()
        elif index == 1:
            self.sales_tab.load_products_safe()
        elif index == 3:  # Dashboard
            self.dashboard_tab.load_stats()

    def setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Archivo")
        view_menu = menubar.addMenu("Vista")

        exit_action = QAction(QIcon("ui/assets/Salir.jpg"), "Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        if self.rol == "admin":
            create_user_action = QAction("Crear Usuario", self)
            create_user_action.triggered.connect(self.create_user)
            file_menu.addAction(create_user_action)

            reset_data_action = QAction("Restablecer Datos", self)
            reset_data_action.triggered.connect(self.reset_data)
            file_menu.addAction(reset_data_action)

        self.theme_action = QAction("Cambiar a Tema Oscuro", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)

    def toggle_theme(self):
        try:
            if self.dark_mode:
                with open("ui/styles.qss", "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
                self.theme_action.setText("Cambiar a Tema Oscuro")
                self.dark_mode = False
            else:
                with open("ui/styles_dark.qss", "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
                self.theme_action.setText("Cambiar a Tema Claro")
                self.dark_mode = True
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", "Archivo de estilos no encontrado. Verifica 'ui/styles.qss' o 'ui/styles_dark.qss'.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cambiar tema:\n{e}")

    def reset_data(self):
        reply1 = QMessageBox.question(self, "Confirmar Restablecimiento",
                                      "¿Estás seguro de vaciar inventario y ventas? Esto eliminará todos los datos.",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply1 == QMessageBox.StandardButton.Yes:
            reply2 = QMessageBox.question(self, "Última Confirmación",
                                          "Esto no se puede deshacer. ¿Continuar?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply2 == QMessageBox.StandardButton.Yes:
                try:
                    conn = sqlite3.connect("cafeteria.db")
                    c = conn.cursor()
                    c.execute("DELETE FROM inventario")
                    c.execute("DELETE FROM ventas")
                    conn.commit()
                    conn.close()
                    QMessageBox.information(self, "Restablecido", "Inventario y ventas han sido vaciados.")
                    self.inventory_tab.load_data_safe()
                    self.sales_tab.load_sales_safe()
                    self.reports_tab.load_data_safe("inventario")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo restablecer:\n{e}")

    def animate_tabs(self):
        if self.animation is None:
            self.animation = QPropertyAnimation(self, b"windowOpacity")
            self.animation.setDuration(500)
            self.animation.setStartValue(0.0)
            self.animation.setEndValue(1.0)
            self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.animation.start()

    def check_alerts(self):
        try:
            conn = sqlite3.connect("cafeteria.db")
            c = conn.cursor()
            # Stock bajo (<=5)
            c.execute("SELECT COUNT(*) FROM inventario WHERE cantidad <= 5")
            low_stock_count = c.fetchone()[0]
            # Vencimiento en 7 días
            from datetime import datetime, timedelta
            future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            c.execute("SELECT COUNT(*) FROM inventario WHERE fecha_vencimiento <= ?", (future_date,))
            expiring_count = c.fetchone()[0]
            conn.close()

            if low_stock_count > 0 or expiring_count > 0:
                msg = "Notificación Automática:\n"
                if low_stock_count > 0:
                    msg += f"- {low_stock_count} productos con stock bajo.\n"
                if expiring_count > 0:
                    msg += f"- {expiring_count} productos por vencer."
                QMessageBox.information(self, "Alerta", msg)
        except Exception as e:
            print(f"Error en alertas: {e}")  # O usa logging

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