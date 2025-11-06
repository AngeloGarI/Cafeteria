from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
import sqlite3
from datetime import datetime

class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_stats()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.total_sales_label = QLabel("Total Ventas (Este Mes): Calculando...")
        self.inventory_count_label = QLabel("Productos en Inventario: Calculando...")
        self.top_product_label = QLabel("Producto Más Vendido: Calculando...")
        layout.addWidget(self.total_sales_label)
        layout.addWidget(self.inventory_count_label)
        layout.addWidget(self.top_product_label)
        self.setLayout(layout)

    def load_stats(self):
        try:
            conn = sqlite3.connect("cafeteria.db")
            c = conn.cursor()
            # Total ventas este mes
            current_month = datetime.now().strftime("%Y-%m")
            c.execute("SELECT SUM(total) FROM ventas WHERE fecha LIKE ?", (f"{current_month}%",))
            total_sales = c.fetchone()[0] or 0
            self.total_sales_label.setText(f"Total Ventas (Este Mes): Q{total_sales:.2f}")
            # Conteo inventario
            c.execute("SELECT COUNT(*) FROM inventario")
            inventory_count = c.fetchone()[0]
            self.inventory_count_label.setText(f"Productos en Inventario: {inventory_count}")
            # Producto más vendido
            c.execute("SELECT producto, SUM(cantidad) as total FROM ventas GROUP BY producto ORDER BY total DESC LIMIT 1")
            top = c.fetchone()
            if top:
                self.top_product_label.setText(f"Producto Más Vendido: {top[0]} ({top[1]} unidades)")
            conn.close()
        except Exception as e:
            self.total_sales_label.setText(f"Error: {e}")