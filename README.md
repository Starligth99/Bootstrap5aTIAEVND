# Bootstrap5aTIAEVND
Es un sitio web con fines académicos para aprendizaje de framework Bootstrap.

## Ejecutar (desarrollo)
1) Activa el entorno virtual y corre migraciones:
   - `venv\Scripts\activate`
   - `python manage.py migrate`
2) Levanta el servidor:
   - `python manage.py runserver`

## Variables de entorno (recomendado)
En `config/settings.py` ya no dependes de valores inseguros hardcodeados en producción.
Puedes partir de `Bootstrap5aTIAEVND/.env.example` y configurar:
- `DJANGO_DEBUG` (`true`/`false`)
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS` (lista separada por comas)
