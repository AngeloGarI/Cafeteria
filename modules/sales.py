from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt
import sqlite3
import os
import pandas as pd
import traceback
from datetime import datetime

class SalesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventas - Cafetería")
        self.resize(700, 400)
        self.setup_ui()
        self.load_products_safe()
        self.load_sales_safe()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Fila de entradas
        form_layout = QHBoxLayout()
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)  # Permite escribir producto manual
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Cantidad")
        self.add_btn = QPushButton("Registrar Venta")
        self.add_btn.clicked.connect(self.add_sale_safe)

        form_layout.addWidget(QLabel("Producto:"))
        form_layout.addWidget(self.product_combo)
        form_layout.addWidget(QLabel("Cantidad:"))
        form_layout.addWidget(self.qty_input)
        form_layout.addWidget(self.add_btn)

        # Botón exportar ventas
        self.export_btn = QPushButton("Exportar Ventas a Excel")
        self.export_btn.clicked.connect(self.export_sales_safe)

        # Tabla de ventas
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Total", "Fecha"])
        self.table.setAlternatingRowColors(True)

        layout.addLayout(form_layout)
        layout.addWidget(self.export_btn)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def get_db_path(self):
        db_path = os.path.join(os.path.dirname(__file__), "..", "cafeteria.db")
        return os.path.abspath(db_path)

    # --- Cargar productos del inventario ---
    def load_products_safe(self):
        try:
            self.load_products()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudieron cargar productos:\n{e}")

    def load_products(self):
        conn = sqlite3.connect(self.get_db_path())
        c = conn.cursor()
        c.execute("SELECT producto FROM inventario WHERE cantidad > 0")
        rows = c.fetchall()
        conn.close()
        self.product_combo.clear()
        for row in rows:
            self.product_combo.addItem(row[0])

    # --- Registrar venta ---
    def add_sale_safe(self):
        try:
            self.add_sale()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo registrar la venta:\n{e}")

    def add_sale(self):
        producto = self.product_combo.currentText().strip()
        cantidad = self.qty_input.text().strip()

        if not producto or not cantidad:
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return

        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError("Cantidad debe ser positiva")
        except ValueError:
            QMessageBox.warning(self, "Error", "Cantidad debe ser un número entero positivo")
            return

        db_path = self.get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Verificar si producto existe en inventario y stock
        c.execute("SELECT cantidad, precio FROM inventario WHERE producto = ?", (producto,))
        inv = c.fetchone()
        precio = 0.0
        if inv:
            stock, precio_unit = inv
            precio = precio_unit
            if cantidad > stock:
                QMessageBox.warning(self, "Error", f"No hay suficiente stock ({stock} disponible)")
                conn.close()
                return
            # Descontar inventario
            new_stock = stock - cantidad
            c.execute("UPDATE inventario SET cantidad = ? WHERE producto = ?", (new_stock, producto))
        else:
            # Producto manual: pide precio
            text, ok = QInputDialog.getDouble(self, "Precio", f"Ingrese precio para '{producto}'", 0.0, 0.01)
            if not ok or text <= 0:
                QMessageBox.warning(self, "Error", "Precio inválido, venta cancelada")
                conn.close()
                return
            precio = text
            c.execute("INSERT INTO inventario (producto, cantidad, precio) VALUES (?, ?, ?)", (producto, 0, precio))

        total = cantidad * precio
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO ventas (producto, cantidad, total, fecha) VALUES (?, ?, ?, ?)",
                  (producto, cantidad, total, fecha))
        conn.commit()
        conn.close()

        self.load_products_safe()
        self.load_sales_safe()
        self.qty_input.clear()

    # --- Cargar ventas a la tabla ---
    def load_sales_safe(self):
        try:
            self.load_sales()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudieron cargar ventas:\n{e}")

    def load_sales(self):
        conn = sqlite3.connect(self.get_db_path())
        c = conn.cursor()
        c.execute("SELECT producto, cantidad, total, fecha FROM ventas")
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                if j in [1,2]:  # alinear cantidad y total a la derecha
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()

    # --- Exportar ventas a Excel ---
    def export_sales_safe(self):
        try:
            self.export_sales()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo exportar ventas:\n{e}")

    def export_sales(self):
        conn = sqlite3.connect(self.get_db_path())
        df = pd.read_sql_query("SELECT * FROM ventas", conn)
        conn.close()

        suggested = "ventas.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, "Guardar reporte de ventas", suggested, "Excel Files (*.xlsx)")
        if not path:
            return

        df.to_excel(path, index=False)
        QMessageBox.information(self, "Exportado", f"Reporte exportado:\n{os.path.abspath(path)}")
