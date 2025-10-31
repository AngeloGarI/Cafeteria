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
        self.resize(700, 400)
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

        # Botones
        self.add_btn = QPushButton("Agregar")
        self.add_btn.clicked.connect(self.add_item_safe)
        self.delete_btn = QPushButton("Eliminar seleccionado")
        self.delete_btn.clicked.connect(self.delete_item_safe)

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.qty_input)
        form_layout.addWidget(self.price_input)
        form_layout.addWidget(self.add_btn)
        form_layout.addWidget(self.delete_btn)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio"])

        layout.addLayout(form_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def get_db_path(self):
        db_path = os.path.join(os.path.dirname(__file__), "..", "cafeteria.db")
        return os.path.abspath(db_path)

    def load_data_safe(self):
        try:
            self.load_data()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error al cargar inventario:\n{e}")

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

        try:
            cantidad = int(cantidad)
            precio = float(precio)
        except ValueError:
            QMessageBox.warning(self, "Error", "Cantidad y precio deben ser números")
            return

        # Validación extra: cantidad y precio deben ser mayores que 0
        if cantidad <= 0:
            QMessageBox.warning(self, "Error", "La cantidad debe ser mayor que 0")
            return
        if precio <= 0:
            QMessageBox.warning(self, "Error", "El precio debe ser mayor que 0")
            return

        conn = sqlite3.connect(self.get_db_path())
        c = conn.cursor()
        c.execute("INSERT INTO inventario (producto, cantidad, precio) VALUES (?, ?, ?)",
                  (nombre, cantidad, precio))
        conn.commit()
        conn.close()

        self.load_data_safe()
        self.name_input.clear()
        self.qty_input.clear()
        self.price_input.clear()

    def delete_item_safe(self):
        try:
            self.delete_item()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el producto:\n{e}")

    def delete_item(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Selecciona un producto para eliminar")
            return

        producto = self.table.item(row, 0).text()
        confirmar = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Seguro que deseas eliminar '{producto}' del inventario?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmar == QMessageBox.StandardButton.No:
            return

        conn = sqlite3.connect(self.get_db_path())
        c = conn.cursor()
        c.execute("DELETE FROM inventario WHERE producto = ?", (producto,))
        conn.commit()
        conn.close()

        self.load_data_safe()
        QMessageBox.information(self, "Eliminado", f"'{producto}' fue eliminado del inventario.")
