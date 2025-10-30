import sqlite3
import pandas as pd
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout
)
from PyQt6.QtCore import Qt


class ReportsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generar Reportes - Cafetería")
        self.setGeometry(200, 200, 750, 550)
        self.setStyleSheet("background-color: #f5f0e6; color: #3e2723;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título
        title = QLabel("📊 Generador de Reportes")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

