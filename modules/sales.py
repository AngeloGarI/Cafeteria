from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class SalesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventas")
        self.resize(400, 300)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Módulo de ventas en desarrollo"))
        self.setLayout(layout)