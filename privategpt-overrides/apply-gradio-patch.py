#!/usr/bin/env python3
"""
Apply Gradio Client Patch for PrivateGPT

Fixes: TypeError: argument of type 'bool' is not iterable

This occurs when gradio_client/utils.py encounters a boolean value in JSON schema
(e.g., additionalProperties: true/false) and tries to check "if 'x' in schema".

The patch adds isinstance(schema, dict) guards throughout the affected functions.
"""

import pathlib
import sys

VENV_PATHS = [
    pathlib.Path.home() / ".cache/pypoetry/virtualenvs",
]


def find_gradio_utils() -> pathlib.Path:
    """Find gradio_client/utils.py in the Poetry virtualenv."""
    for base in VENV_PATHS:
        if not base.exists():
            continue
        for venv in base.iterdir():
            candidate = venv / "lib/python3.11/site-packages/gradio_client/utils.py"
            if candidate.exists():
                return candidate
    raise FileNotFoundError("Could not find gradio_client/utils.py in virtualenv")


def apply_patch(filepath: pathlib.Path) -> bool:
    """Apply the comprehensive patch. Returns True if changes were made."""
    text = filepath.read_text()
    original = text

    # Fix 1: Guard get_type() against non-dict schemas
    old_gettype = '''def get_type(schema: dict):
    if "const" in schema:'''
    new_gettype = '''def get_type(schema: dict):
    if not isinstance(schema, dict):
        return None
    if "const" in schema:'''

    if old_gettype in text:
        text = text.replace(old_gettype, new_gettype)
        print("  Patched get_type() guard")

    # Fix 2: Handle None in _json_schema_to_python_type
    old_type_check = '    if type_ == {}:'
    new_type_check = '    if type_ is None or type_ == {}:'

    if old_type_check in text:
        text = text.replace(old_type_check, new_type_check)
        print("  Patched type_ None check")

    # Fix 3: Guard schema.get() in the None branch
    old_json_check = '''    if type_ is None or type_ == {}:
        if "json" in schema.get("description", {}):'''
    new_json_check = '''    if type_ is None or type_ == {}:
        if isinstance(schema, dict) and "json" in schema.get("description", {}):'''

    if old_json_check in text:
        text = text.replace(old_json_check, new_json_check)
        print("  Patched json description check")

    if text != original:
        filepath.write_text(text)
        return True
    return False


def main():
    print("Applying Gradio Client Patch...")
    try:
        target = find_gradio_utils()
        print(f"Target: {target}")
        if apply_patch(target):
            print("✅ Patch applied successfully")
        else:
            print("ℹ️  Patch already applied or not needed")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
