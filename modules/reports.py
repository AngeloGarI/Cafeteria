from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
import pandas as pd
import sqlite3

class ReportsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reportes")
        self.resize(400, 300)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Generando reporte a Excel...."))
        self.setLayout(layout)
        self.export_excel()

    def export_excel(self):
        conn = sqlite3.connect("cafeteria.db")
        df = pd.read_sql_query("SELECT * FROM inventario", conn)
        conn.close()
        df.to_excel("reporte_inventario.xlsx", index=False)