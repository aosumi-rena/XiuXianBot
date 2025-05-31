import json
import os

def load_localisation(lang='CHS'):
    try:
        textmap_path = os.path.join(os.path.dirname(__file__), '..', 'textmaps', f'{lang}.json')
        with open(textmap_path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Localisation file for {lang} not found. Using default (CHS).")
        textmap_path = os.path.join(os.path.dirname(__file__), '..', 'textmaps', 'CHS.json')
        with open(textmap_path, encoding='utf-8') as f:
            return json.load(f)

def get_response(key, lang='CHS', **kwargs):
    try:
        textmap = load_localisation(lang)
        response = textmap['responses'].get(key, {})
        response_type = response.get('type', 'plain')
        text = response.get('text', '').format(**kwargs)
        return response_type, text
    except KeyError as e:
        print(f"Missing key in textmap: {e}")
        return 'plain', f"NO_TEXT({key}) | Report it to Bot Admins!"
    except Exception as e:
        print(f"Error in get_response for key {key}, lang {lang}: {e}")
        return 'plain', f"ERR_TEXT({key}) | Report it to Bot Admins!"
