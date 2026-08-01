import json
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

_manifest_cache: tuple[int, dict] | None = None


def load_manifest():
    global _manifest_cache

    manifest_path = settings.DJANGO_VITE_MANIFEST_PATH
    if not manifest_path.exists():
        raise ImproperlyConfigured(f"Vite manifest at {manifest_path} not found.")
    if not manifest_path.is_file():
        raise ImproperlyConfigured(f"Vite manifest at {manifest_path} is not a file.")

    manifest_mtime_ns = os.stat(manifest_path).st_mtime_ns
    if _manifest_cache is not None:
        cached_mtime_ns, cached_manifest = _manifest_cache
        if cached_mtime_ns == manifest_mtime_ns:
            return cached_manifest

    with open(manifest_path, "r") as manifest_file:
        try:
            manifest = json.load(manifest_file)
        except json.JSONDecodeError as e:
            raise ImproperlyConfigured(
                f"Vite manifest {manifest_path} is not valid JSON: {e}"
            )

    _manifest_cache = (manifest_mtime_ns, manifest)
    return manifest
