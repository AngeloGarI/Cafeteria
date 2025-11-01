from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
import sqlite3
import os
import traceback

class InventoryWindow(QWidget):
    def __init__(self, rol="admin"):
        super().__init__()
        self.setWindowTitle("Gestión de Inventario - Cafetería")
        self.resize(800, 500)
        self.rol = rol
        self.setup_ui()
        self.load_data_safe()
        self.check_low_stock_once()

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        btn_layout = QHBoxLayout()

        title = QLabel("Gestión de Inventario")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar producto...")
        self.search_input.textChanged.connect(self.filter_table)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del producto")
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Cantidad")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Precio (Q)")

        self.add_btn = QPushButton("Agregar")
        self.add_btn.clicked.connect(self.add_item_safe)
        self.update_btn = QPushButton("Actualizar")
        self.update_btn.clicked.connect(self.update_item_safe)
        self.delete_btn = QPushButton("Eliminar")
        self.delete_btn.clicked.connect(self.delete_item_safe)
        self.refresh_btn = QPushButton("Refrescar")  # Nuevo botón para recarga manual
        self.refresh_btn.clicked.connect(self.refresh_data)

        form_layout.addWidget(QLabel("Buscar:"))
        form_layout.addWidget(self.search_input)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.qty_input)
        form_layout.addWidget(self.price_input)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.refresh_btn)  # Agregado

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio (Q)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
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
        c.execute("SELECT producto, cantidad, precio FROM inventario ORDER BY producto ASC")
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                if j in [1, 2]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(i, j, item)

    def filter_table(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                self.table.setRowHidden(row, search_text not in item.text().lower())

    def add_item_safe(self):
        try:
            self.add_item()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo agregar el producto:\n{e}")

    def add_item(self):
        if self.rol != "admin":
            QMessageBox.warning(self, "Acceso Denegado", "Solo administradores pueden agregar productos.")
            return

        nombre = self.name_input.text().strip()
        cantidad = self.qty_input.text().strip()
        precio = self.price_input.text().strip()

        if not nombre or not cantidad or not precio:
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return

        try:
            cantidad = int(cantidad)
            precio = float(precio)
            if cantidad <= 0 or precio <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Cantidad y precio deben ser valores positivos válidos")
            return

        conn = sqlite3.connect(self.get_db_path())
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM inventario WHERE producto = ?", (nombre,))
        if c.fetchone()[0] > 0:
            QMessageBox.warning(self, "Duplicado", f"El producto '{nombre}' ya existe en el inventario.")
            conn.close()
            return

        c.execute("INSERT INTO inventario (producto, cantidad, precio) VALUES (?, ?, ?)",
                  (nombre, cantidad, precio))
        conn.commit()
        conn.close()

        self.load_data_safe()
        self.clear_inputs()

    def update_item_safe(self):
        try:
            self.update_item()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el producto:\n{e}")

    def update_item(self):
        if self.rol != "admin":
            QMessageBox.warning(self, "Acceso Denegado", "Solo administradores pueden actualizar productos.")
            return

        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Selecciona un producto para actualizar")
            return

        nueva_cantidad = self.qty_input.text().strip()
        nuevo_precio = self.price_input.text().strip()

        if not nueva_cantidad or not nuevo_precio:
            QMessageBox.warning(self, "Error", "Ingresa cantidad y precio en los campos")
            return

        try:
            nueva_cantidad = int(nueva_cantidad)
            nuevo_precio = float(nuevo_precio)
            if nueva_cantidad < 0 or nuevo_precio <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Valores inválidos")
            return

        nombre = self.table.item(row, 0).text()
        conn = sqlite3.connect(self.get_db_path())
        c = conn.cursor()
        c.execute("UPDATE inventario SET cantidad = ?, precio = ? WHERE producto = ?",
                  (nueva_cantidad, nuevo_precio, nombre))
        conn.commit()
        conn.close()

        self.load_data_safe()
        self.clear_inputs()
        QMessageBox.information(self, "Actualizado", f"'{nombre}' fue actualizado correctamente.")

    def delete_item_safe(self):
        try:
            self.delete_item()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el producto:\n{e}")

    def delete_item(self):
        if self.rol != "admin":
            QMessageBox.warning(self, "Acceso Denegado", "Solo administradores pueden eliminar productos.")
            return

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

    def clear_inputs(self):
        self.name_input.clear()
        self.qty_input.clear()
        self.price_input.clear()

    def check_low_stock_once(self):
        conn = sqlite3.connect(self.get_db_path())
        c = conn.cursor()
        c.execute("SELECT producto, cantidad FROM inventario WHERE cantidad <= 5")
        low_stock = c.fetchall()
        conn.close()

        if low_stock:
            mensaje = "\n".join([f"• {p} (stock: {q})" for p, q in low_stock])
            QMessageBox.warning(self, "Stock bajo", f"Productos con poco stock:\n{mensaje}")

    def refresh_data(self):
        # Método para recarga manual/rápida
        self.load_data_safe()
        QMessageBox.information(self, "Refrescado", "Datos del inventario actualizados.")