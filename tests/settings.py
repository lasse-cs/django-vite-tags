from pathlib import Path

INSTALLED_APPS = [
    "django_vite_tags",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
    }
]

DJANGO_VITE_MANIFEST_PATH = Path(__file__).parent.resolve() / "manifest.json"
