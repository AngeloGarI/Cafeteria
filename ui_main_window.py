from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
from modules.inventory import InventoryWindow
from modules.sales import SalesWindow
from modules.reports import ReportsWindow

class MainWindow(QMainWindow):
    def __init__(self, rol):
        super().__init__()
        self.setWindowTitle("Sistema de Cafeteria")
        self.resize(400, 300)
        self.rol = rol
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        self.btn_inventory = QPushButton("Inventario")
        self.btn_sales = QPushButton("Ventas")
        self.btn_reports = QPushButton("Reportes")

        self.btn_inventory.clicked.connect(self.open_inventory)
        self.btn_sales.clicked.connect(self.open_sales)
        self.btn_reports.clicked.connect(self.open_reports)

        layout.addWidget(self.btn_inventory)
        layout.addWidget(self.btn_sales)
        layout.addWidget(self.btn_reports)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def open_inventory(self):
        self.inv = InventoryWindow()
        self.inv.show()

    def open_sales(self):
        self.sales = SalesWindow()
        self.sales.show()

    def open_reports(self):
        self.rep = ReportsWindow()
        self.rep.show()