import os
import json
from flask import Flask, render_template, request, jsonify

BASE_DIR    = os.path.abspath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, '..', 'config.json')
I18N_DIR    = os.path.join(BASE_DIR, 'i18n')

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'static'),
            template_folder=os.path.join(BASE_DIR, 'templates'))

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def load_translations(lang):
    path = os.path.join(I18N_DIR, f'{lang}.json')
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@app.context_processor
def inject_i18n():
    lang = request.args.get('lang', 'en')
    trans = load_translations(lang)
    return dict(trans=trans, current_lang=lang)

@app.route('/')
def index():
    cfg = load_config()
    return render_template('index.html', config=cfg)

@app.route('/config', methods=['GET'])
def config_get():
    cfg = load_config()
    return render_template(f'config.html', config_json=json.dumps(cfg, indent=2))

@app.route('/config', methods=['POST'])
def config_post():
    lang  = request.args.get('lang', 'en')
    trans = load_translations(lang)

    old_cfg = load_config()
    new_cfg = request.get_json()
    try:
        save_config(new_cfg)
        full_restart    = old_cfg.get('db')             != new_cfg.get('db') \
                       or old_cfg.get('admin_panel')    != new_cfg.get('admin_panel')
        adapter_restart = old_cfg.get('adapters')       != new_cfg.get('adapters') \
                       or old_cfg.get('tokens')         != new_cfg.get('tokens')
        return jsonify(
            status='ok',
            message=trans.get('config_saved', 'Config saved successfully!'),
            full_restart=full_restart,
            adapter_restart=adapter_restart
        )
    except Exception as e:
        return jsonify(status='error', message=str(e)), 500

if __name__ == '__main__':
    cfg  = load_config()
    port = cfg.get('admin_panel', {}).get('port', 11451)
    app.run(host='127.0.0.1', port=port, debug=True)
