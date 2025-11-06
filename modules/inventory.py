from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QDateEdit, QComboBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QDate
import sqlite3
import os
import traceback

class InventoryWindow(QWidget):
    def __init__(self, rol="admin"):
        super().__init__()
        self.setWindowTitle("Gestión de Inventario - Cafetería")
        self.resize(900, 500)
        self.rol = rol
        self.setup_ui()
        self.load_data_safe()

    def setup_ui(self):
        layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title = QLabel("Gestión de Inventario")
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
        btn_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar producto...")
        self.search_input.textChanged.connect(self.filter_table)
        self.search_input.setToolTip("Escribe para filtrar productos por nombre")

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todas", "Bebida", "Comida", "Otro"])
        self.filter_combo.currentTextChanged.connect(self.filter_table)
        self.filter_combo.setToolTip("Filtra productos por categoría")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del producto")
        self.name_input.setToolTip("Ingresa el nombre del producto (máx. 50 caracteres)")
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Categoría (ej. Bebidas)")
        self.category_input.setToolTip("Ingresa la categoría del producto")
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Cantidad")
        self.qty_input.setToolTip("Ingresa la cantidad (número positivo)")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Precio (Q)")
        self.price_input.setToolTip("Ingresa el precio en quetzales (número positivo)")
        self.expiry_input = QDateEdit()
        self.expiry_input.setCalendarPopup(True)
        self.expiry_input.setDate(QDate.currentDate())
        self.expiry_input.setToolTip("Selecciona la fecha de vencimiento")

        self.add_btn = QPushButton("Agregar")
        self.add_btn.clicked.connect(self.add_item_safe)
        self.add_btn.setToolTip("Agrega un nuevo producto al inventario")
        self.update_btn = QPushButton("Actualizar")
        self.update_btn.clicked.connect(self.update_item_safe)
        self.update_btn.setToolTip("Actualiza el producto seleccionado")
        self.delete_btn = QPushButton("Eliminar")
        self.delete_btn.clicked.connect(self.delete_item_safe)
        self.delete_btn.setToolTip("Elimina el producto seleccionado")
        self.refresh_btn = QPushButton("Refrescar")
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.refresh_btn.setToolTip("Recarga los datos del inventario")
        self.import_btn = QPushButton("Importar desde Excel")
        self.import_btn.clicked.connect(self.import_from_excel)

        form_layout.addWidget(QLabel("Buscar:"))
        form_layout.addWidget(self.search_input)
        form_layout.addWidget(QLabel("Categoría:"))
        form_layout.addWidget(self.filter_combo)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.category_input)
        form_layout.addWidget(self.qty_input)
        form_layout.addWidget(self.price_input)
        form_layout.addWidget(self.expiry_input)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.import_btn)

        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(table_container)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Producto", "Categoría", "Cantidad", "Precio (Q)", "Fecha Vencimiento"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        table_layout.addWidget(self.table)

        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(table_container)
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
        c.execute("SELECT producto, categoria, cantidad, precio, fecha_vencimiento FROM inventario ORDER BY producto ASC")
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val else "")
                if j in [2, 3]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(i, j, item)

    def filter_table(self):
        search_text = self.search_input.text().lower()
        category_filter = self.filter_combo.currentText().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            category_item = self.table.item(row, 1)
            if item and category_item:
                matches_search = search_text in item.text().lower()
                matches_category = category_filter == "todas" or category_filter == category_item.text().lower()
                self.table.setRowHidden(row, not (matches_search and matches_category))

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
        categoria = self.category_input.text().strip().title()
        cantidad = self.qty_input.text().strip()
        precio = self.price_input.text().strip()
        fecha_vencimiento = self.expiry_input.date().toString("yyyy-MM-dd")

        if not nombre or not cantidad or not precio:
            QMessageBox.warning(self, "Error", "Completa nombre, cantidad y precio")
            return
        if len(nombre) > 50 or not nombre.replace(" ", "").isalnum():
            QMessageBox.warning(self, "Error", "Nombre debe tener máximo 50 caracteres y solo letras, números o espacios.")
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
        c.execute("SELECT COUNT(*) FROM inventario WHERE producto COLLATE NOCASE = ?", (nombre,))
        if c.fetchone()[0] > 0:
            QMessageBox.warning(self, "Duplicado", f"El producto '{nombre}' ya existe en el inventario (ignorando mayúsculas).")
            conn.close()
            return

        c.execute("INSERT INTO inventario (producto, categoria, cantidad, precio, fecha_vencimiento) VALUES (?, ?, ?, ?, ?)",
                  (nombre, categoria or None, cantidad, precio, fecha_vencimiento))
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

        nueva_categoria = self.category_input.text().strip().title()
        nueva_cantidad = self.qty_input.text().strip()
        nuevo_precio = self.price_input.text().strip()
        nueva_fecha = self.expiry_input.date().toString("yyyy-MM-dd")

        if not nueva_cantidad or not nuevo_precio:
            QMessageBox.warning(self, "Error", "Ingresa cantidad y precio")
            return
        if len(nueva_categoria) > 50 or not nueva_categoria.replace(" ", "").isalnum():
            QMessageBox.warning(self, "Error", "Categoría debe tener máximo 50 caracteres y solo letras, números o espacios.")
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
        c.execute("UPDATE inventario SET categoria = ?, cantidad = ?, precio = ?, fecha_vencimiento = ? WHERE producto = ?",
                  (nueva_categoria or None, nueva_cantidad, nuevo_precio, nueva_fecha, nombre))
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
        self.category_input.clear()
        self.qty_input.clear()
        self.price_input.clear()
        self.expiry_input.setDate(QDate.currentDate())

    def refresh_data(self):
        self.load_data_safe()
        QMessageBox.information(self, "Refrescado", "Datos del inventario actualizados.")

    def import_from_excel(self):
        from PyQt6.QtWidgets import QFileDialog
        import pandas as pd
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Excel", "", "Excel Files (*.xlsx)")
        if path:
            try:
                df = pd.read_excel(path)
                conn = sqlite3.connect(self.get_db_path())
                c = conn.cursor()
                for _, row in df.iterrows():
                    producto = str(row.get("Producto", "")).strip()
                    categoria = str(row.get("Categoría", "")).strip().title()
                    cantidad = int(row.get("Cantidad", 0))
                    precio = float(row.get("Precio", 0.0))
                    # Validaciones
                    if producto and cantidad > 0 and precio > 0:
                        c.execute("INSERT OR IGNORE INTO inventario (producto, categoria, cantidad, precio) VALUES (?, ?, ?, ?)",
                                  (producto, categoria, cantidad, precio))
                conn.commit()
                conn.close()
                self.load_data_safe()
                QMessageBox.information(self, "Importado", "Datos importados correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al importar:\n{e}")
