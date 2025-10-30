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

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        self.table_selector = QComboBox()
        self.table_selector.addItems(["inventario", "ventas"])
        self.table_selector.currentTextChanged.connect(self.load_data_safe)
        self.table_selector.setStyleSheet("""
                    QComboBox {
                        padding: 6px;
                        border: 1px solid #a1887f;
                        border-radius: 6px;
                        background-color: #fff;
                        color: #3e2723;
                        font-size: 14px;
                    }
                    QComboBox:hover { border-color: #795548; }
                """)
        controls_layout.addWidget(QLabel("Seleccione reporte:"))
        controls_layout.addWidget(self.table_selector)

        # Botón actualizar
        self.refresh_button = QPushButton("🔄 Actualizar datos")
        self.refresh_button.setStyleSheet("""
                    QPushButton {
                        background-color: #a1887f;
                        color: white;
                        padding: 8px 12px;
                        font-size: 13px;
                        border-radius: 6px;
                    }
                    QPushButton:hover { background-color: #8d6e63; }
                """)
        self.refresh_button.clicked.connect(self.refresh_data)
        controls_layout.addWidget(self.refresh_button)

        self.export_button = QPushButton("📤 Exportar a Excel")
        self.export_button.setStyleSheet("""
                    QPushButton {
                        background-color: #795548;
                        color: white;
                        padding: 8px 16px;
                        font-size: 13px;
                        border-radius: 6px;
                    }
                    QPushButton:hover { background-color: #5d4037; }
                """)
        self.export_button.clicked.connect(self.export_report)
        controls_layout.addWidget(self.export_button)

        layout.addLayout(controls_layout)

        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
                    QTableWidget {
                        background-color: #ffffff;
                        gridline-color: #d7ccc8;
                        border-radius: 8px;
                    }
                    QHeaderView::section {
                        background-color: #d7ccc8;
                        color: #3e2723;
                        font-weight: bold;
                        padding: 4px;
                    }
                """)
        layout.addWidget(self.table_widget)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        self.load_data_safe("inventario")
        