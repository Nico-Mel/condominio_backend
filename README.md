# Smart Condominium Backend

Este es el backend del sistema "Smart Condominium", desarrollado con Django + PostgreSQL, organizado en una estructura minimalista y clara. No se utiliza el sistema de autenticación por defecto de Django (`auth_user`), sino un modelo de usuario completamente personalizado.

---


- Python 3.11+
- Django 5.2.6
- Django REST Framework
- PostgreSQL
- `.env` para configuración secreta
- Serializers y Views personalizadas (no ViewSets)

---


```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate   # en Windows

# Instalar dependencias
pip install -r requirements.txt
