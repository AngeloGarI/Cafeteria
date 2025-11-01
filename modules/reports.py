import sqlite3
import pandas as pd
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout
)
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta

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

    def get_db_path(self):
        db_path = os.path.join(os.path.dirname(__file__), "..", "cafeteria.db")
        return os.path.abspath(db_path)

    def load_data_safe(self, table_name):
        try:
            self.load_data(table_name)
        except sqlite3.OperationalError as e:
            QMessageBox.critical(
                self, "Error de base de datos",
                f"No se encontró la tabla '{table_name}' en la base de datos.\n\nDetalles:\n{str(e)}"
            )
            self.table_widget.clear()

    def load_data(self, table_name):
        db_path = self.get_db_path()
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()

        if df.empty:
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            self.status_label.setText(f"⚠️ La tabla '{table_name}' no tiene registros.")
            return

        self.table_widget.setRowCount(len(df))
        self.table_widget.setColumnCount(len(df.columns))
        self.table_widget.setHorizontalHeaderLabels(df.columns)

        for i, row in df.iterrows():
            for j, value in enumerate(row):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(value)))

        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.status_label.setText(f"Mostrando datos de '{table_name}' ({len(df)} registros).")

        self.current_df = df
        self.current_table = table_name

        if table_name == "inventario":
            self.check_expiring_products()

    def check_expiring_products(self):
        # Verifica productos que vencen en 7 días
        conn = sqlite3.connect(self.get_db_path())
        c = conn.cursor()
        c.execute("SELECT producto, fecha_vencimiento FROM inventario WHERE fecha_vencimiento IS NOT NULL")
        rows = c.fetchall()
        conn.close()

        expiring = []
        for p, f in rows:
            if f:
                try:
                    venc = datetime.strptime(f, "%Y-%m-%d")
                    if (venc - datetime.now()).days <= 7 and (venc - datetime.now()).days >= 0:
                        expiring.append(f"{p} (vence: {f})")
                except ValueError:
                    pass  # Ignora fechas inválidas

        if expiring:
            mensaje = "\n".join(expiring)
            QMessageBox.warning(self, "Productos por vencer", f"Estos productos vencen pronto:\n{mensaje}")

    def refresh_data(self):
        if hasattr(self, "current_table"):
            self.load_data_safe(self.current_table)
        else:
            self.load_data_safe("inventario")

    def export_report(self):
        if not hasattr(self, "current_df") or self.current_df.empty:
            QMessageBox.warning(self, "Sin datos", "No hay datos para exportar.")
            return

        table_name = getattr(self, "current_table", "tabla")
        export_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
        os.makedirs(export_dir, exist_ok=True)
        export_path = os.path.join(export_dir, f"reporte_{table_name}.xlsx")

        self.current_df.to_excel(export_path, index=False)
        self.status_label.setText(f"✅ Reporte de {table_name} exportado correctamente.")
        QMessageBox.information(
            self, "Reporte generado",
            f"El reporte de '{table_name}' fue exportado con éxito.\n\nUbicación:\n{export_path}"
        )
