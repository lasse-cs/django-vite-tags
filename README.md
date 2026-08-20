# Django Vite Tags

Basic backend integration for Django to use vite for building static assets, following the [Vite backend integration guide](https://vite.dev/guide/backend-integration).

For a more comprehensive integration for Django, see for example [django-vite](https://github.com/MrBin99/django-vite).

## Usage

To use include `django_vite_tags` in `INSTALLED_APPS`. Then add the `{% vite %}` template tag with the entry point to include

```django+html
{% load vite_tags %}

{% vite '<entrypoint>' %}
```

For development, specify the `DJANGO_VITE_SERVER_URL` setting to point to the vite development server

```python
DJANGO_VITE_SERVER_URL="http://localhost:5173"
```

This will add the tags for the asset and to enable hot module reloading.

For production, specify the `DJANGO_VITE_MANIFEST_PATH` with the path that Django will read the vite generated `manifest.json`.

```python
from pathlib import Path

DJANGO_VITE_MANIFEST_PATH = BASE_DIR / "static_out" / ".vite" / "manifest.json"
```
