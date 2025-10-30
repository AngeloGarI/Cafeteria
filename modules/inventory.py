from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox
)
import sqlite3
import os
import traceback

class InventoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de inventario")
        self.resize(600, 400)
        self.setup_ui()
        self.load_data_safe()

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        # Campos de entrada
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del producto")
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Cantidad")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Precio")

        # Botón Agregar
        self.add_btn = QPushButton("Agregar")
        self.add_btn.clicked.connect(self.add_item_safe)

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.qty_input)
        form_layout.addWidget(self.price_input)
        form_layout.addWidget(self.add_btn)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio"])

        layout.addLayout(form_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    # Versión segura de load_data
    def load_data_safe(self):
        try:
            self.load_data()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error al cargar inventario:\n{e}")


    def get_db_path(self):
        db_path = os.path.join(os.path.dirname(__file__), "..", "database", "cafeteria.db")
        return os.path.normpath(db_path)

    def load_data(self):
        conn = sqlite3.connect(self.get_db_path())
        c = conn.cursor()
        c.execute("SELECT producto, cantidad, precio FROM inventario")
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    # Versión segura de add_item
    def add_item_safe(self):
        try:
            self.add_item()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo agregar el producto:\n{e}")

    def add_item(self):
        nombre = self.name_input.text().strip()
        cantidad = self.qty_input.text().strip()
        precio = self.price_input.text().strip()

        if not nombre or not cantidad or not precio:
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return

        # Validación de números
        try:
            cantidad = int(cantidad)
            precio = float(precio)
        except ValueError:
            QMessageBox.warning(self, "Error", "Cantidad y precio deben ser números")
            return

        db_path = os.path.join(os.path.dirname(__file__), "..", "database", "cafeteria.db")
        db_path = os.path.normpath(db_path)

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("INSERT INTO inventario (producto, cantidad, precio) VALUES (?, ?, ?)",
                  (nombre, cantidad, precio))
        conn.commit()
        conn.close()

        self.load_data_safe()
        self.name_input.clear()
        self.qty_input.clear()
        self.price_input.clear()
