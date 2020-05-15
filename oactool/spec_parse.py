from __future__ import annotations

from jsonref import JsonLoader, JsonRef


def unref_spec(spec: dict) -> dict:
    return JsonRef.replace_refs(spec, base_uri="", loader=JsonLoader, jsonschema=False, load_on_repr=True)
