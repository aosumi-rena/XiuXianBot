'''
Not used for now
'''

import json
import os
from typing import Dict

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
LANG_FILE = os.path.join(DATA_DIR, 'language_prefs.json')


def _ensure_file() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(LANG_FILE):
        with open(LANG_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2, ensure_ascii=False)


def load_prefs() -> Dict[str, str]:
    _ensure_file()
    try:
        with open(LANG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def save_prefs(prefs: Dict[str, str]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LANG_FILE, 'w', encoding='utf-8') as f:
        json.dump(prefs, f, indent=2, ensure_ascii=False)


def get_user_lang(user_id: str, default: str = 'CHS') -> str:
    prefs = load_prefs()
    return prefs.get(str(user_id), default)


def set_user_lang(user_id: str, lang: str) -> None:
    prefs = load_prefs()
    prefs[str(user_id)] = lang.upper()
    save_prefs(prefs)
