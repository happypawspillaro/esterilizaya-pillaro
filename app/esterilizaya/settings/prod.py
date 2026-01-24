# No comprobar en ciertas líneas F403 y F405 para compartir las configuraciones del base.py
from .base import *  # noqa: F403
from .utils import retornar_urls

DEBUG = False
ADMINS = [("José Jácome", "josejacomeb@gmail.com")]
ALLOWED_HOSTS = [*retornar_urls(), "localhost", "nginx"]
STATIC_ROOT = BASE_DIR / "static"  # noqa: F405
STATICFILES_DIRS = [
    BASE_DIR / "static",  # noqa: F405
]
# Configuraciones de seguridad
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
