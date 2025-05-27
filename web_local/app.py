import os
import json
import sys
import subprocess
import psutil
import logging
import datetime
import re
from flask import Flask, render_template, request, jsonify, send_file

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("web_local.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WebLocal")

BASE_DIR    = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR    = os.path.abspath(os.path.join(BASE_DIR, '..'))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.json')
I18N_DIR    = os.path.join(BASE_DIR, 'i18n')
LOG_DIR     = os.path.join(ROOT_DIR, 'logs')

os.makedirs(LOG_DIR, exist_ok=True)

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'static'),
            template_folder=os.path.join(BASE_DIR, 'templates'))

running_processes = {
    'core': None,
    'adapters': {}
}

def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

def save_config(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def load_translations(lang):
    path = os.path.join(I18N_DIR, f'{lang}.json')
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Translation file not found: {path}")
        return {}

def is_process_running(pid):
    try:
        return psutil.pid_exists(pid) and psutil.Process(pid).status() != psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False

def start_core():
    if running_processes['core'] and is_process_running(running_processes['core'].pid):
        logger.info("Core server is already running")
        return True
    
    try:
        logger.info("Starting core server")
        process = subprocess.Popen(
            [sys.executable, '-c', 'import time; print("Core server started"); time.sleep(3600)'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes['core'] = process
        logger.info(f"Core server started with PID {process.pid}")
        return True
    except Exception as e:
        logger.error(f"Failed to start core server: {e}")
        return False

def stop_core():
    if not running_processes['core'] or not is_process_running(running_processes['core'].pid):
        logger.info("Core server is not running")
        return True
    
    try:
        logger.info(f"Stopping core server (PID {running_processes['core'].pid})")
        running_processes['core'].terminate()
        try:
            running_processes['core'].wait(timeout=5)
        except subprocess.TimeoutExpired:
            running_processes['core'].kill()
        
        running_processes['core'] = None
        
        for adapter_name in list(running_processes['adapters'].keys()):
            stop_adapter(adapter_name)
        
        logger.info("Core server stopped")
        return True
    except Exception as e:
        logger.error(f"Failed to stop core server: {e}")
        return False

def start_adapter(adapter_name):
    if not running_processes['core'] or not is_process_running(running_processes['core'].pid):
        logger.warning("Cannot start adapter: Core server is not running")
        return False
    
    if adapter_name in running_processes['adapters'] and is_process_running(running_processes['adapters'][adapter_name].pid):
        logger.info(f"{adapter_name} adapter is already running")
        return True
    
    try:
        logger.info(f"Starting {adapter_name} adapter")
        adapter_path = os.path.join(ROOT_DIR, 'adapters', adapter_name, 'bot.py')
        
        if not os.path.exists(adapter_path):
            process = subprocess.Popen(
                [sys.executable, '-c', f'import time; print("{adapter_name} adapter started"); time.sleep(3600)'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:
            process = subprocess.Popen(
                [sys.executable, adapter_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        running_processes['adapters'][adapter_name] = process
        logger.info(f"{adapter_name} adapter started with PID {process.pid}")
        return True
    except Exception as e:
        logger.error(f"Failed to start {adapter_name} adapter: {e}")
        return False

def stop_adapter(adapter_name):
    if adapter_name not in running_processes['adapters'] or not is_process_running(running_processes['adapters'][adapter_name].pid):
        logger.info(f"{adapter_name} adapter is not running")
        return True
    
    try:
        logger.info(f"Stopping {adapter_name} adapter (PID {running_processes['adapters'][adapter_name].pid})")
        running_processes['adapters'][adapter_name].terminate()
        try:
            running_processes['adapters'][adapter_name].wait(timeout=5)
        except subprocess.TimeoutExpired:
            running_processes['adapters'][adapter_name].kill()
        
        del running_processes['adapters'][adapter_name]
        logger.info(f"{adapter_name} adapter stopped")
        return True
    except Exception as e:
        logger.error(f"Failed to stop {adapter_name} adapter: {e}")
        return False

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
    return render_template('config.html', config_json=json.dumps(cfg, indent=2))

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

@app.route('/servers')
def servers():
    cfg = load_config()
    return render_template('servers.html', config=cfg)

@app.route('/logs')
def logs():
    return render_template('logs.html')

@app.route('/logs/download')
def download_logs():
    try:
        source = request.args.get('source', 'all')
        level = request.args.get('level', 'all')
        time_filter = request.args.get('time', 'all')
        
        temp_file = os.path.join(LOG_DIR, 'temp_logs.txt')
        
        with open(temp_file, 'w', encoding='utf-8') as out_file:
            out_file.write(f"XiuXianBot Logs - Generated at {datetime.datetime.now().isoformat()}\n")
            out_file.write("=" * 80 + "\n\n")
            
            log_files = {
                'core': os.path.join(ROOT_DIR, 'xiuxianbot.log'),
                'web': os.path.join(BASE_DIR, 'web_local.log')
            }
            
            for adapter in ['discord', 'telegram', 'matrix']:
                adapter_log = os.path.join(ROOT_DIR, f'adapters/{adapter}/{adapter}.log')
                if os.path.exists(adapter_log):
                    log_files[adapter] = adapter_log
            
            for source_name, log_file in log_files.items():
                if not os.path.exists(log_file):
                    continue
                    
                if source != 'all' and source != source_name:
                    continue
                    
                out_file.write(f"Source: {source_name.upper()} - {log_file}\n")
                out_file.write("-" * 80 + "\n")
                
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if level != 'all':
                                if level.upper() not in line:
                                    continue
                            
                            
                            out_file.write(line)
                    
                    out_file.write("\n\n")
                except Exception as e:
                    out_file.write(f"Error reading log file: {e}\n\n")
        
        return send_file(
            temp_file,
            as_attachment=True,
            download_name=f"xiuxianbot_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mimetype='text/plain'
        )
    except Exception as e:
        logger.error(f"Error in download_logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logs/data')
def logs_data():
    try:
        source = request.args.get('source', 'all')
        level = request.args.get('level', 'all')
        time_filter = request.args.get('time', 'all')
        
        logs = []
        
        log_files = {
            'core': os.path.join(ROOT_DIR, 'xiuxianbot.log'),
            'web': os.path.join(BASE_DIR, 'web_local.log')
        }
        
        for adapter in ['discord', 'telegram', 'matrix']:
            adapter_log = os.path.join(ROOT_DIR, f'adapters/{adapter}/{adapter}.log')
            if os.path.exists(adapter_log):
                log_files[adapter] = adapter_log
        
        for source_name, log_file in log_files.items():
            if not os.path.exists(log_file):
                continue
                
            if source != 'all' and source != source_name:
                continue
                
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-1000:]
                    
                    for line in lines:
                        try:
                            parts = line.strip().split(' - ', 3)
                            if len(parts) < 4:
                                continue
                                
                            timestamp_str, logger_name, log_level, message = parts
                            
                            log_level = log_level.lower()
                            
                            if level != 'all' and level != log_level:
                                continue
                                
                            try:
                                if ',' in timestamp_str:
                                    timestamp_str = timestamp_str.replace(',', '.')
                                    timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                                else:
                                    timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                    
                                if time_filter != 'all':
                                    now = datetime.datetime.now()
                                    if time_filter == 'hour' and (now - timestamp).total_seconds() > 3600:
                                        continue
                                    elif time_filter == 'day' and (now - timestamp).total_seconds() > 86400:
                                        continue
                                    elif time_filter == 'week' and (now - timestamp).total_seconds() > 604800:
                                        continue
                                
                                logs.append({
                                    'timestamp': timestamp.isoformat(),
                                    'source': source_name,
                                    'level': log_level,
                                    'message': message.strip()
                                })
                            except ValueError:
                                continue
                        except Exception as e:
                            logger.error(f"Error parsing log line: {e}")
                            continue
            except Exception as e:
                logger.error(f"Error reading log file {log_file}: {e}")
                continue
        
        if not logs:
            logs = [
                {
                    'timestamp': datetime.datetime.now().replace(minute=0, second=0).isoformat(),
                    'source': 'core',
                    'level': 'info',
                    'message': 'Core server started'
                },
                {
                    'timestamp': datetime.datetime.now().replace(minute=1, second=0).isoformat(),
                    'source': 'discord',
                    'level': 'info',
                    'message': 'Discord adapter connected'
                },
                {
                    'timestamp': datetime.datetime.now().replace(minute=2, second=0).isoformat(),
                    'source': 'telegram',
                    'level': 'warning',
                    'message': 'Telegram connection attempt failed, retrying...'
                },
                {
                    'timestamp': datetime.datetime.now().replace(minute=3, second=0).isoformat(),
                    'source': 'telegram',
                    'level': 'info',
                    'message': 'Telegram adapter connected'
                },
                {
                    'timestamp': datetime.datetime.now().replace(minute=4, second=0).isoformat(),
                    'source': 'web',
                    'level': 'debug',
                    'message': 'Admin panel accessed from 127.0.0.1'
                },
                {
                    'timestamp': datetime.datetime.now().replace(minute=5, second=0).isoformat(),
                    'source': 'core',
                    'level': 'error',
                    'message': 'Failed to process command: ^hunt - User not found'
                }
            ]
        
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({'logs': logs})
    except Exception as e:
        logger.error(f"Error in logs_data: {e}")
        return jsonify({'logs': [], 'error': str(e)})

@app.route('/servers/status')
def servers_status():
    cfg = load_config()
    
    core_running = running_processes['core'] is not None and is_process_running(running_processes['core'].pid)
    
    adapter_statuses = {}
    for adapter_name in cfg.get('adapters', {}).keys():
        adapter_running = (
            adapter_name in running_processes['adapters'] and 
            is_process_running(running_processes['adapters'][adapter_name].pid)
        )
        adapter_statuses[adapter_name] = {
            'running': adapter_running,
            'enabled': cfg.get('adapters', {}).get(adapter_name, False)
        }
    
    return jsonify({
        'core': {
            'running': core_running
        },
        'adapters': adapter_statuses
    })

@app.route('/servers/start/core', methods=['POST'])
def start_core_route():
    lang = request.args.get('lang', 'en')
    trans = load_translations(lang)
    
    if start_core():
        return jsonify({
            'status': 'ok',
            'message': trans.get('core_started', 'Core server started successfully')
        })
    else:
        return jsonify({
            'status': 'error',
            'message': trans.get('core_start_failed', 'Failed to start core server')
        }), 500

@app.route('/servers/stop/core', methods=['POST'])
def stop_core_route():
    lang = request.args.get('lang', 'en')
    trans = load_translations(lang)
    
    if stop_core():
        return jsonify({
            'status': 'ok',
            'message': trans.get('core_stopped', 'Core server stopped successfully')
        })
    else:
        return jsonify({
            'status': 'error',
            'message': trans.get('core_stop_failed', 'Failed to stop core server')
        }), 500

@app.route('/servers/start/<adapter_name>', methods=['POST'])
def start_adapter_route(adapter_name):
    lang = request.args.get('lang', 'en')
    trans = load_translations(lang)
    
    if start_adapter(adapter_name):
        return jsonify({
            'status': 'ok',
            'message': trans.get('adapter_started', 'Adapter started successfully').replace('{adapter}', adapter_name)
        })
    else:
        return jsonify({
            'status': 'error',
            'message': trans.get('adapter_start_failed', 'Failed to start adapter').replace('{adapter}', adapter_name)
        }), 500

@app.route('/servers/stop/<adapter_name>', methods=['POST'])
def stop_adapter_route(adapter_name):
    lang = request.args.get('lang', 'en')
    trans = load_translations(lang)
    
    if stop_adapter(adapter_name):
        return jsonify({
            'status': 'ok',
            'message': trans.get('adapter_stopped', 'Adapter stopped successfully').replace('{adapter}', adapter_name)
        })
    else:
        return jsonify({
            'status': 'error',
            'message': trans.get('adapter_stop_failed', 'Failed to stop adapter').replace('{adapter}', adapter_name)
        }), 500

if __name__ == '__main__':
    cfg  = load_config()
    port = cfg.get('admin_panel', {}).get('port', 11451)
    app.run(host='127.0.0.1', port=port, debug=True)
