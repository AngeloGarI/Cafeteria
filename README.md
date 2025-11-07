☕ Sistema de Cafetería Profesional

Gestión moderna para cafeterías modernas

Un sistema creado en Python + PyQt6, pensado para llevar inventario, ventas, reportes, usuarios y estadísticas con la suavidad de un latte bien batido.

✨ ¿Qué ofrece este sistema?
Área	Funciones
🔐 Autenticación	Inicio de sesión con roles (Admin / Empleado).
📦 Inventario	Agregar, editar y controlar productos, stock y vencimientos.
💰 Ventas	Registra ventas y descuenta stock automáticamente.
📊 Reportes	Reportes por usuario o fecha y exportación.
📈 Dashboard	Ventas del día, producto top y estado general.
🚨 Alertas	Stock bajo y productos por vencer.
🎨 Temas	Tema claro y oscuro para la vista cansada.
🗄️ SQLite	Base de datos local automática.
🛠️ Requisitos

Python 3.8+

PyQt6

pip install PyQt6


Pandas

pip install pandas


SQLite (ya viene con Python)

🚀 Instalación y Ejecución

Clona el repositorio

git clone <https://github.com/AngeloGarI/Cafeteria.git>


Instala dependencias

pip install PyQt6 install pandas openpyxl


Ejecuta el sistema

python main.py


No necesitas moverte de carpeta ni nada extraño.
Solo ejecutas main.py y el sistema crea todo lo necesario, incluyendo el administrador inicial.

🔑 Credenciales iniciales

Usuario: admin

Contraseña: 1234

Rol con acceso total.

Desde el menú podrás crear empleados y administrar usuarios.

🧭 Cómo usar el sistema
🗂️ Inventario

Solo admins: Agrega, edita, controla y elimina productos del inventario como también los stocks y vencimientos.

💵 Ventas

Todos los usuarios pueden vender.
Los empleados ven solo sus ventas.

📄 Reportes

Ventas por mes, por usuario y por rango.
Incluye exportación (Excel / CSV).

📊 Dashboard visual

El pulso de la cafetería:
ventas del mes, producto más vendido y total de productos en inventario.

🔧 Ajustes

Tema claro/oscuro, restablecimiento de datos y recuperación de contraseña.

📁 Estructura del Proyecto
cafeteria

├── main.py                       # Entrada principal del sistema

├── database                 # Inicialización alternativa

│   ├── db_init.py

├── ui/

│   ├── login_window.py

│   ├── main_window.py

│   ├── styles.qss

│   ├── styles_dark.qss

│   └── assets/                # Logos e imágenes

│   ├── modules/

│   │   ├── inventory.py

│   │   ├── sales.py

│   │   ├── reports.py

│   │   └── dashboard.py

└── README.md

📝 Notas finales

Todo funciona al ejecutar main.py. No requiere configuraciones adicionales.

Si aparece un error, revisa que cafeteria.db exista (se genera sola).

Puedes poner tus propias imágenes en:

ui/assets/


Proyecto listo para uso, edición o ampliación.