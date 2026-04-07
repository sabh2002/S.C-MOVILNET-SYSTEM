# CLAUDE.md — S.C Movilnet System

Instrucciones para Claude Code al trabajar en este proyecto.

## Stack

| Capa | Tecnología | Notas |
|------|-----------|-------|
| Backend | Django 6.0.3 + Python 3.x | ⚠️ Django 6 — más nuevo que el boilerplate |
| Base de datos | SQLite | Solo desarrollo — sin PostgreSQL aún |
| Frontend | Django Templates | Sin HTMX/Alpine por ahora |
| Auth | Django default (sin AbstractUser) | Pendiente de migrar |
| Deploy | Sin configurar | Fase 1 en progreso |

## Estructura del proyecto

```
movilnet/
├── core/
│   ├── settings.py   → DJANGO_SETTINGS_MODULE=core.settings
│   ├── urls.py
│   └── wsgi.py
├── movilnet/          → App principal
└── manage.py
```

## Estado del proyecto

**Fase 1 en progreso.** Proyecto en etapa inicial. Solo tiene la app `movilnet` creada.

- Sin custom user model (usar AbstractUser antes de primera migración)
- Sin multi-tenancy implementado
- Sin deploy configurado
- SECRET_KEY hardcodeada en settings — cambiar antes de cualquier push

## ⚠️ Advertencias críticas

1. **Django 6.0.3** — versión más nueva que el stack estándar (5.x). Verificar compatibilidad antes de usar librerías del boilerplate.
2. **SECRET_KEY expuesta** en `core/settings.py` — si esto va a producción, mover a `.env` inmediatamente.
3. **SQLite only** — si se agrega multi-tenancy, migrar a PostgreSQL.
4. **Sin AbstractUser** — si se necesita custom user, hacerlo ANTES de la primera migración real (o requiere squash complejo).

## Próximos pasos recomendados

```python
# Antes de avanzar:
# 1. Crear apps/core/ con AbstractUser
# 2. Configurar AUTH_USER_MODEL = 'core.User'
# 3. Mover SECRET_KEY a .env
# 4. Decidir si agregar PostgreSQL
```

## Comandos de desarrollo

```bash
# Activar entorno virtual
source env/bin/activate

# Desarrollo
python manage.py runserver

# Migraciones
python manage.py makemigrations
python manage.py migrate
```

## Variables de entorno (a configurar)

```
SECRET_KEY=changeme
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```
