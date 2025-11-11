from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
from PyQt6.QtCore import Qt

class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo de Algoritmos - Cafetería")
        self.resize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.title_label = QLabel("🔍 Demo de Algoritmos")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.products = ["Café", "Pan", "Leche", "Azúcar", "Té", "Galletas", "Jugo", "Queso"]
        self.sorted_products = sorted(self.products)

        self.search_label = QLabel("Búsqueda Binaria (en lista ordenada):")
        layout.addWidget(self.search_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ingresa producto a buscar")
        layout.addWidget(self.search_input)
        self.search_btn = QPushButton("Buscar")
        self.search_btn.clicked.connect(self.binary_search)
        layout.addWidget(self.search_btn)

        self.sort_label = QLabel("Bubble Sort (ordenar lista):")
        layout.addWidget(self.sort_label)
        self.sort_btn = QPushButton("Ordenar Lista")
        self.sort_btn.clicked.connect(self.bubble_sort_demo)
        layout.addWidget(self.sort_btn)

        self.stack_label = QLabel("Pila (Stack) - Agregar/Quitar elementos:")
        layout.addWidget(self.stack_label)
        self.stack_input = QLineEdit()
        self.stack_input.setPlaceholderText("Ingresa elemento")
        layout.addWidget(self.stack_input)
        self.push_btn = QPushButton("Push (Agregar)")
        self.push_btn.clicked.connect(self.stack_push)
        layout.addWidget(self.push_btn)
        self.pop_btn = QPushButton("Pop (Quitar)")
        self.pop_btn.clicked.connect(self.stack_pop)
        layout.addWidget(self.pop_btn)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def binary_search(self):
        target = self.search_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Error", "Ingresa un producto")
            return

        low, high = 0, len(self.sorted_products) - 1
        while low <= high:
            mid = (low + high) // 2
            if self.sorted_products[mid] == target:
                self.result_text.append(f"Búsqueda Binaria: '{target}' encontrado en posición {mid}")
                return
            elif self.sorted_products[mid] < target:
                low = mid + 1
            else:
                high = mid - 1
        self.result_text.append(f"Búsqueda Binaria: '{target}' no encontrado")

    def bubble_sort_demo(self):
        arr = self.products.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n-i-1):
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
        self.result_text.append(f"Bubble Sort: Lista ordenada: {arr}")

    def stack_push(self):
        item = self.stack_input.text().strip()
        if not item:
            QMessageBox.warning(self, "Error", "Ingresa un elemento")
            return
        if not hasattr(self, 'stack'):
            self.stack = []
        self.stack.append(item)
        self.result_text.append(f"Pila Push: Agregado '{item}'. Pila: {self.stack}")

    def stack_pop(self):
        if not hasattr(self, 'stack') or not self.stack:
            QMessageBox.warning(self, "Error", "Pila vacía")
            return
        item = self.stack.pop()
        self.result_text.append(f"Pila Pop: Quitado '{item}'. Pila: {self.stack}")
