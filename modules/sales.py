from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import sqlite3
import os
import pandas as pd
import traceback
from datetime import datetime, timedelta

class SalesWindow(QWidget):
    def __init__(self, usuario_actual="admin"):  # Recibe usuario actual
        super().__init__()
        self.setWindowTitle("Ventas - Cafetería")
        self.resize(700, 400)
        self.usuario_actual = usuario_actual  # Guardar usuario
        self.setup_ui()
        self.load_products_safe()
        self.load_sales_safe()

    def setup_ui(self):
        layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title = QLabel("Ventas")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title)
        title_layout.addStretch()

        image_label = QLabel()
        image_pixmap = QPixmap("ui/assets/Logo.png").scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
        image_label.setPixmap(image_pixmap)
        title_layout.addStretch()
        title_layout.addWidget(image_label)
        layout.addLayout(title_layout)

        form_layout = QHBoxLayout()
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        self.product_combo.setToolTip("Selecciona o escribe el producto a vender")
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Cantidad")
        self.qty_input.setToolTip("Ingresa la cantidad a vender (número positivo)")
        self.add_btn = QPushButton("Registrar Venta")
        self.add_btn.clicked.connect(self.add_sale_safe)
        self.add_btn.setToolTip("Registra la venta y actualiza inventario")

        form_layout.addWidget(QLabel("Producto:"))
        form_layout.addWidget(self.product_combo)
        form_layout.addWidget(QLabel("Cantidad:"))
        form_layout.addWidget(self.qty_input)
        form_layout.addWidget(self.add_btn)

        filter_layout = QHBoxLayout()
        self.date_filter_combo = QComboBox()
        self.date_filter_combo.addItems(["Todas", "Hoy", "Esta Semana", "Este Mes"])
        self.date_filter_combo.currentTextChanged.connect(self.filter_sales_by_date)
        self.date_filter_combo.setToolTip("Filtra ventas por período de fecha")
        filter_layout.addWidget(QLabel("Filtrar por fecha:"))
        filter_layout.addWidget(self.date_filter_combo)

        self.export_btn = QPushButton("Exportar Ventas a Excel")
        self.export_btn.clicked.connect(self.export_sales_safe)
        self.export_btn.setToolTip("Exporta las ventas filtradas a un archivo Excel")

        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(table_container)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Total", "Fecha", "Usuario"])
        self.table.setAlternatingRowColors(True)

        table_layout.addWidget(self.table)

        layout.addLayout(form_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.export_btn)
        layout.addWidget(table_container)
        self.setLayout(layout)

    def get_db_path(self):
        db_path = os.path.join(os.path.dirname(__file__), "..", "cafeteria.db")
        return os.path.abspath(db_path)

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
        if len(producto) > 50 or not producto.replace(" ", "").isalnum():
            QMessageBox.warning(self, "Error", "Producto debe tener máximo 50 caracteres y solo letras, números o espacios.")
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

        c.execute("SELECT cantidad, precio FROM inventario WHERE producto = ?", (producto,))
        inv = c.fetchone()
        precio = 0.0
        if inv:
            stock, precio_unit = inv
            precio = precio_unit
            if cantidad > stock:
                QMessageBox.warning(self, "Error", f"No hay suficiente stock. Disponible: {stock}")
                conn.close()
                return
            new_stock = stock - cantidad
            c.execute("UPDATE inventario SET cantidad = ? WHERE producto = ?", (new_stock, producto))
        else:
            QMessageBox.warning(self, "Error", "Producto no encontrado en inventario")
            conn.close()
            return

        total = cantidad * precio
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO ventas (producto, cantidad, total, fecha, usuario) VALUES (?, ?, ?, ?, ?)",
                  (producto, cantidad, total, fecha, self.usuario_actual))
        conn.commit()
        conn.close()

        self.load_products_safe()
        self.load_sales_safe()
        self.qty_input.clear()

    def load_sales_safe(self):
        try:
            self.load_sales()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudieron cargar ventas:\n{e}")

    def load_sales(self):
        conn = sqlite3.connect(self.get_db_path())
        c = conn.cursor()
        if self.usuario_actual != "admin":
            c.execute("SELECT producto, cantidad, total, fecha, usuario FROM ventas WHERE usuario = ?", (self.usuario_actual,))
        else:
            c.execute("SELECT producto, cantidad, total, fecha, usuario FROM ventas")
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                if j in [1,2]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(i, j, item)
        self.table.resizeColumnsToContents()

    def filter_sales_by_date(self):
        filter_option = self.date_filter_combo.currentText()
        now = datetime.now()
        for row in range(self.table.rowCount()):
            date_item = self.table.item(row, 3)  # Fecha
            if date_item:
                try:
                    sale_date = datetime.strptime(date_item.text(), "%Y-%m-%d %H:%M:%S")
                    if filter_option == "Hoy":
                        show = sale_date.date() == now.date()
                    elif filter_option == "Esta Semana":
                        start_week = now - timedelta(days=now.weekday())
                        show = start_week.date() <= sale_date.date() <= now.date()
                    elif filter_option == "Este Mes":
                        show = sale_date.year == now.year and sale_date.month == now.month
                    else:
                        show = True
                    self.table.setRowHidden(row, not show)
                except ValueError:
                    self.table.setRowHidden(row, False)  # Muestra si fecha inválida

    def export_sales_safe(self):
        try:
            self.export_sales()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo exportar ventas:\n{e}")

    def export_sales(self):
        visible_rows = []
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                visible_rows.append(row_data)

        if not visible_rows:
            QMessageBox.warning(self, "Sin datos", "No hay ventas visibles para exportar.")
            return

        df = pd.DataFrame(visible_rows, columns=["Producto", "Cantidad", "Total", "Fecha", "Usuario"])
        suggested = "ventas_filtradas.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, "Guardar ventas filtradas", suggested, "Excel Files (*.xlsx)")
        if not path:
            return

        df.to_excel(path, index=False)
        QMessageBox.information(self, "Exportado", f"Ventas filtradas exportadas:\n{os.path.abspath(path)}")