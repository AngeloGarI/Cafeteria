from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox
import sqlite3

class InventoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de inventario")
        self.resize(500, 400)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.name_input = QLineEdit()
        self.name.input.setPlaceholderText("Nombre del producto")
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Cantidad")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Precio")

        self.add_btn = QPushButton("Agregar")
        self.add_btn.clicked.connect(self.add_item)

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.qty_input)
        form_layout.addWidget(self.price_input)
        form_layout.addWidget(self.add_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Nombre", "Cantidad", "Precio"])

        layout.addLayout(form_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def add_item(self):
        nombre = self.name_input.text()
        cantidad = self.qty_input.text()
        precio = self.price_input.text()

        if not nombre or not cantidad or not precio:
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return

        conn = sqlite3.connect("cafeteria.db")
        c = conn.cursor()
        c.execute("INSERT INTO inventario (nombre, cantidad, precio) VALUES (?, ?, ?)",
                  (nombre, cantidad, precio))
        conn.commit()
        conn.close()

        self.load_data()
        self.name_input.clear()
        self.qty_input.clear()
        self.price_input.clear()

    def load_data(self):
        conn = sqlite3.connect("cafeteria.db")
        c = conn.cursor()
        c.execute("SELECT nombre, cantidad, precio FROM inventario")
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))