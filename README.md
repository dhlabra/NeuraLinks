📦 NeuraLinks Backend

Un backend seguro y escalable desarrollado con FastAPI, que implementa autenticación JWT, manejo de roles de usuario (admin/user), y conexión a PostgreSQL.

🚀 Características

🔐 Autenticación segura con JWT
🔑 Registro e inicio de sesión con cifrado bcrypt
👤 Roles de usuario (admin/user) con control de accesos
🗄️ Base de datos PostgreSQL con SQLAlchemy
⚡ FastAPI para endpoints rápidos y documentados
✅ Preparado para deploy en Railway/Render/Supabase
⚙️ Instalación

Clona el repositorio:
git clone https://github.com/TU_USUARIO/NeuraLinks.git
cd NeuraLinks
Crea un entorno virtual:
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
Instala las dependencias:
pip install -r requirements.txt
🛠️ Configuración

Crea un archivo .env en la raíz del proyecto con:

DATABASE_URL=postgresql://postgres:postgres@localhost/secure_backend_db
SECRET_KEY=TU_SECRET_KEY_AQUI
🚀 Ejecución local

uvicorn main:app --reload
Accede a la documentación interactiva:
📑 http://127.0.0.1:8000/docs
Redacción automática de Swagger incluida.

🔑 Endpoints principales

Método	Ruta	Descripción
POST	/register	Registro de usuario con rol
POST	/login	Login y generación de JWT
GET	/users/me	Consultar datos del usuario autenticado
GET	/admin/dashboard	Endpoint exclusivo para administradores
🚀 Tecnologías

FastAPI
PostgreSQL
SQLAlchemy
JWT (jose)
bcrypt (passlib)
Docker Ready (opcional, para el deploy)
📦 Deploy sugerido

Railway
Render
Supabase para la base de datos
Docker para despliegue en VPS
📜 Licencia

MIT License

✅ Próximamente:

🔒 Refresh tokens
📊 Dockerización completa
🧠 IA integrada (Predicciones / Recomendaciones API)