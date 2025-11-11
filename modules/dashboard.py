from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
import sqlite3
from datetime import datetime

class DashboardWindow(QWidget):
    def __init__(self, rol, usuario_actual):
        super().__init__()
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.setup_ui()
        self.load_stats()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.title_label = QLabel("📈 Dashboard Diario")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.total_sales_today_label = QLabel("Ventas de Hoy: Calculando...")
        self.total_sales_today_label.setStyleSheet("font-size: 14px; margin: 5px;")
        layout.addWidget(self.total_sales_today_label)

        self.products_sold_today_label = QLabel("Productos Vendidos Hoy: Calculando...")
        self.products_sold_today_label.setStyleSheet("font-size: 14px; margin: 5px;")
        layout.addWidget(self.products_sold_today_label)

        self.top_product_today_label = QLabel("Producto Más Vendido Hoy: Calculando...")
        self.top_product_today_label.setStyleSheet("font-size: 14px; margin: 5px;")
        layout.addWidget(self.top_product_today_label)

        self.inventory_count_label = QLabel("Productos en Inventario: Calculando...")
        self.inventory_count_label.setStyleSheet("font-size: 14px; margin: 5px;")
        layout.addWidget(self.inventory_count_label)

        self.low_stock_alert_label = QLabel("Alertas de Stock Bajo: Calculando...")
        self.low_stock_alert_label.setStyleSheet("font-size: 14px; margin: 5px;")
        layout.addWidget(self.low_stock_alert_label)

        self.setLayout(layout)

    def load_stats(self):
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            conn = sqlite3.connect("cafeteria.db")
            c = conn.cursor()

            if self.rol != "admin":
                c.execute("SELECT SUM(total), SUM(cantidad) FROM ventas WHERE fecha LIKE ? AND usuario = ?", (f"{today}%", self.usuario_actual))
            else:
                c.execute("SELECT SUM(total), SUM(cantidad) FROM ventas WHERE fecha LIKE ?", (f"{today}%",))
            sales_data = c.fetchone()
            total_sales_today = sales_data[0] or 0
            products_sold_today = sales_data[1] or 0
            self.total_sales_today_label.setText(f"Ventas de Hoy: Q{total_sales_today:.2f}")
            self.products_sold_today_label.setText(f"Productos Vendidos Hoy: {products_sold_today}")

            # Producto más vendido hoy
            if self.rol != "admin":
                c.execute("SELECT producto, SUM(cantidad) as total FROM ventas WHERE fecha LIKE ? AND usuario = ? GROUP BY producto ORDER BY total DESC LIMIT 1", (f"{today}%", self.usuario_actual))
            else:
                c.execute("SELECT producto, SUM(cantidad) as total FROM ventas WHERE fecha LIKE ? GROUP BY producto ORDER BY total DESC LIMIT 1", (f"{today}%",))
            top_today = c.fetchone()
            if top_today:
                self.top_product_today_label.setText(f"Producto Más Vendido Hoy: {top_today[0]} ({top_today[1]} unidades)")
            else:
                self.top_product_today_label.setText("Producto Más Vendido Hoy: Ninguno")

            c.execute("SELECT COUNT(*) FROM inventario")
            inventory_count = c.fetchone()[0]
            self.inventory_count_label.setText(f"Productos en Inventario: {inventory_count}")
            c.execute("SELECT COUNT(*) FROM inventario WHERE cantidad <= 5")
            low_stock_count = c.fetchone()[0]
            self.low_stock_alert_label.setText(f"Alertas de Stock Bajo: {low_stock_count} productos (<=5)")

            conn.close()
        except Exception as e:
            self.total_sales_today_label.setText(f"Error: {e}")
