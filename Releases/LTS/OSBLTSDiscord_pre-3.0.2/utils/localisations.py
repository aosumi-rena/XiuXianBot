import json

def load_localisation(lang='CHS'):
    try:
        with open(f'textmaps/{lang}.json', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Localisation file for {lang} not found. Using default (CHS).")
        with open('textmaps/CHS.json', encoding='utf-8') as f:
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

