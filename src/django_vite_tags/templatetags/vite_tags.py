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
    css_files: set[str] = field(default_factory=set)
    js_files: set[str] = field(default_factory=set)
    modulepreloads: set[str] = field(default_factory=set)


def append_static_file(target_list, seen_set, file_path):
    if file_path in seen_set:
        return

    seen_set.add(file_path)
    target_list.append(static(file_path))


def collect_imports(manifest, entry_point):
    imported_entries = []
    seen = {entry_point}

    def visit(entry):
        for imported_file in entry.get("imports", []):
            if imported_file in seen:
                continue
            if imported_file not in manifest:
                raise DjangoViteManifestError(
                    f'Entrypoint "{imported_file}" is not found in the Vite manifest.'
                )

            seen.add(imported_file)
            imported_entry = manifest[imported_file]
            visit(imported_entry)
            imported_entries.append(imported_entry)

    visit(manifest[entry_point])
    return imported_entries


def walk_manifest(manifest, entry_point):
    if entry_point not in manifest:
        raise DjangoViteManifestError(
            f'Entrypoint "{entry_point}" is not found in the Vite manifest.'
        )

    context = DjangoViteManifestContext()
    state = DjangoViteManifestWalkState()
    entry = manifest[entry_point]
    imported_entries = collect_imports(manifest, entry_point)

    for css_file in entry.get("css", []):
        append_static_file(context.css_files, state.css_files, css_file)

    for imported_entry in imported_entries:
        for css_file in imported_entry.get("css", []):
            append_static_file(context.css_files, state.css_files, css_file)

    referenced_file = entry["file"]
    if referenced_file.endswith(".css"):
        append_static_file(context.css_files, state.css_files, referenced_file)
    elif referenced_file.endswith(".js"):
        append_static_file(context.js_files, state.js_files, referenced_file)

    for imported_entry in imported_entries:
        referenced_file = imported_entry["file"]
        if referenced_file.endswith(".js"):
            append_static_file(
                context.modulepreloads,
                state.modulepreloads,
                referenced_file,
            )

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
