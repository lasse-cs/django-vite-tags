from dataclasses import dataclass, field

from django.conf import settings
from django.template import Library
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from django_vite_tags import load_manifest

register = Library()


class DjangoViteManifestError(Exception):
    pass


@dataclass
class DjangoViteManifestContext:
    css_files: list[str] = field(default_factory=list)
    js_files: list[str] = field(default_factory=list)
    modulepreloads: list[str] = field(default_factory=list)


@dataclass
class DjangoViteManifestWalkState:
    entries: set[str] = field(default_factory=set)
    css_files: set[str] = field(default_factory=set)
    js_files: set[str] = field(default_factory=set)
    modulepreloads: set[str] = field(default_factory=set)


def append_static_file(target_list, seen_set, file_path):
    if file_path in seen_set:
        return

    seen_set.add(file_path)
    target_list.append(static(file_path))


def walk_manifest(manifest, entry_point, context=None, state=None):
    if context is None:
        context = DjangoViteManifestContext()
    if state is None:
        state = DjangoViteManifestWalkState()

    if entry_point in state.entries:
        return context

    if entry_point not in manifest:
        raise DjangoViteManifestError(
            f'Entrypoint "{entry_point}" is not found in the Vite manifest.'
        )
    entry = manifest[entry_point]
    referenced_file = entry["file"]
    is_entry = entry.get("isEntry", False)
    state.entries.add(entry_point)
    for css_file in entry.get("css", []):
        append_static_file(context.css_files, state.css_files, css_file)
    if is_entry:
        if referenced_file.endswith(".css"):
            append_static_file(context.css_files, state.css_files, referenced_file)
        elif referenced_file.endswith(".js"):
            append_static_file(context.js_files, state.js_files, referenced_file)
    elif referenced_file.endswith(".js"):
        append_static_file(
            context.modulepreloads,
            state.modulepreloads,
            referenced_file,
        )

    for imported_file in entry.get("imports", []):
        walk_manifest(manifest, imported_file, context, state)
    return context


@register.inclusion_tag("django_vite_tags/vite.html")
def vite(entry_point):
    if hasattr(settings, "DJANGO_VITE_SERVER_URL"):
        result = DjangoViteManifestContext(
            js_files=[
                mark_safe(f"{settings.DJANGO_VITE_SERVER_URL.strip('/')}/@vite/client"),
                mark_safe(
                    f"{settings.DJANGO_VITE_SERVER_URL.strip('/')}/{entry_point}"
                ),
            ]
        )
    else:
        manifest = load_manifest()
        result = walk_manifest(manifest, entry_point)
    return {"manifest": result}
