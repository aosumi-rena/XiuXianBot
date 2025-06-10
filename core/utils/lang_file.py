"""Helper for storing language preferences in a JSON file.

Structure of ``language_prefs.json``::

    {
        "discord": {
            "<platform_id>": "EN"
        },
        "telegram": {
            "<platform_id>": "CHS"
        }
    }

Each platform has its own object so IDs never clash.
"""

import json
import os
from typing import Dict, Any

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
)
LANG_FILE = os.path.join(DATA_DIR, "language_prefs.json")

DEFAULT_PREFS = {"discord": {}, "telegram": {}}


def _ensure_file() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(LANG_FILE):
        with open(LANG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_PREFS, f, indent=2, ensure_ascii=False)


def load_prefs() -> Dict[str, Any]:
    _ensure_file()
    try:
        with open(LANG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                # ensure required keys exist
                for k in DEFAULT_PREFS:
                    data.setdefault(k, {})
                return data
    except Exception:
        pass
    return DEFAULT_PREFS.copy()


def save_prefs(prefs: Dict[str, Any]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LANG_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=2, ensure_ascii=False)


def get_user_lang(platform: str, user_id: str, default: str = "CHS") -> str:
    prefs = load_prefs()
    return prefs.get(platform, {}).get(str(user_id), default)


def set_user_lang(platform: str, user_id: str, lang: str) -> None:
    prefs = load_prefs()
    prefs.setdefault(platform, {})[str(user_id)] = lang.upper()
    save_prefs(prefs)

