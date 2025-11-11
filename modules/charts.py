from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QPieSeries, QPieSlice
from PyQt6.QtCore import Qt
import sqlite3
from datetime import datetime, timedelta

class ChartsWindow(QWidget):
    def __init__(self, rol, usuario_actual):
        super().__init__()
        self.rol = rol
        self.usuario_actual = usuario_actual
        self.setWindowTitle("Estadísticas - Cafetería")
        self.setup_ui()
        self.load_charts()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.title_label = QLabel("📊 Estadísticas Visuales")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.bar_chart_view = QChartView()
        layout.addWidget(self.bar_chart_view)

        self.pie_chart_view = QChartView()
        layout.addWidget(self.pie_chart_view)

        self.setLayout(layout)

    def load_charts(self):
        self.load_bar_chart()
        self.load_pie_chart()

    def load_bar_chart(self):
        months = []
        sales = []
        for i in range(5, -1, -1):  # Últimos 6 meses
            month_date = datetime.now().replace(day=1) - timedelta(days=i*30)
            month_str = month_date.strftime("%Y-%m")
            months.append(month_date.strftime("%b %Y"))
            try:
                conn = sqlite3.connect("cafeteria.db")
                c = conn.cursor()
                if self.rol != "admin":
                    c.execute("SELECT SUM(total) FROM ventas WHERE fecha LIKE ? AND usuario = ?", (f"{month_str}%", self.usuario_actual))
                else:
                    c.execute("SELECT SUM(total) FROM ventas WHERE fecha LIKE ?", (f"{month_str}%",))
                total = c.fetchone()[0] or 0
                sales.append(total)
                conn.close()
            except Exception as e:
                sales.append(0)

        bar_set = QBarSet("Ventas (Q)")
        bar_set.append(sales)
        bar_series = QBarSeries()
        bar_series.append(bar_set)

        chart = QChart()
        chart.addSeries(bar_series)
        chart.setTitle("Ventas por Mes")

        axis_x = QBarCategoryAxis()
        axis_x.append(months)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        bar_series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setTitleText("Total (Q)")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        bar_series.attachAxis(axis_y)

        self.bar_chart_view.setChart(chart)

    def load_pie_chart(self):
        categories = {}
        try:
            conn = sqlite3.connect("cafeteria.db")
            c = conn.cursor()
            c.execute("SELECT categoria, COUNT(*) FROM inventario GROUP BY categoria")
            rows = c.fetchall()
            conn.close()
            for row in rows:
                cat = row[0] or "Sin Categoría"
                categories[cat] = row[1]
        except Exception as e:
            categories = {"Error": 1}

        pie_series = QPieSeries()
        for cat, count in categories.items():
            slice = QPieSlice(cat, count)
            slice.setLabel(f"{cat}: {count}")
            pie_series.append(slice)

        chart = QChart()
        chart.addSeries(pie_series)
        chart.setTitle("Distribución de Inventario por Categoría")

        self.pie_chart_view.setChart(chart)