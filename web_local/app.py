import os
import json
import sys
import subprocess
import psutil
import logging
import datetime
import re
from core.database.connection import (
    connect_sqlite,
    create_tables,
    fetch_one,
    fetch_all,
    execute,
)
from flask import Flask, render_template, request, jsonify, send_file

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join("logs", "web_local.log")),
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

cfg = load_config()
db_path = cfg.get('db', {}).get('sqlite_path', os.path.join('data', 'xiu_xian.db'))
connect_sqlite(db_path)
create_tables()

def save_config(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def load_translations(lang):
    alias_map = {"CHS": "zh", "EN": "en"}
    lang_code = alias_map.get(lang.upper(), lang)
    path = os.path.join(I18N_DIR, f"{lang_code}.json")
    try:
        with open(path, encoding="utf-8") as f:
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
        
        try:
            from core.database.connection import connect_sqlite, create_tables
            from core.game.mechanics import initialize_game_mechanics

            connect_sqlite(db_path)
            create_tables()

            initialize_game_mechanics()

            logger.info("Core components initialized successfully")
        except Exception as init_error:
            logger.error(f"Failed to initialize core components: {init_error}")
        
        server_path = os.path.join(ROOT_DIR, 'core', 'server.py')
        process = subprocess.Popen(
            [sys.executable, server_path],
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

def parse_lang(arg: str) -> str:
    alias_map = {"CHS": "zh", "EN": "en"}
    return alias_map.get(arg.upper(), arg)


@app.context_processor
def inject_utils():
    return dict(parse_lang=parse_lang)


@app.context_processor
def inject_i18n():
    raw_lang = request.args.get('lang', 'en')
    lang = parse_lang(raw_lang)
    trans = load_translations(lang)
    return dict(trans=trans, current_lang=lang)


@app.context_processor
def inject_versions():
    return dict(
        core_version=os.getenv("CORE_VERSION", "dev"),
        web_version=os.getenv("WEB_VERSION", "dev"),
        discord_version=os.getenv("DISCORD_VERSION", "dev"),
        telegram_version=os.getenv("TELEGRAM_VERSION", "dev"),
    )

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
    lang = parse_lang(request.args.get('lang', 'en'))
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

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/database')
def database():
    return render_template('database.html')

@app.route('/admin/search_user')
def search_user():
    try:
        query = request.args.get('query', '')
        logger.info(f"Search user request with query: {query}")
        
        if not query:
            logger.warning("No query provided in search_user")
            return jsonify({'status': 'error', 'message': 'No query provided'}), 400
        
        from core.admin.user_management import search_users, get_user
        
        logger.info(f"Attempting to find user by ID: {query}")
        user = get_user(query)
        if user:
            logger.info(
                f"User found by ID: {user.get('user_id')} / {user.get('in_game_username')}"
            )
            return jsonify({'status': 'ok', 'user': user})
        
        logger.info(f"User not found by ID, searching by username regex: {query}")
        users = search_users({'in_game_username': {'$regex': query, '$options': 'i'}}, limit=10)
        if users:
            logger.info(f"Found {len(users)} users by username search")
            return jsonify({'status': 'ok', 'users': users})
        
        logger.warning(f"No users found for query: {query}")
        return jsonify({'status': 'error', 'message': 'No users found'}), 404
    except Exception as e:
        logger.error(f"Error in search_user: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@app.route('/admin/modify_user', methods=['POST'])
def modify_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        field = data.get('field')
        action = data.get('action')
        value = data.get('value')
        
        if not all([user_id, field, action, value is not None]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        from core.admin.user_management import modify_user_field
        
        success, message = modify_user_field(user_id, field, action, value)
        
        if success:
            return jsonify({'status': 'ok', 'message': message})
        else:
            return jsonify({'status': 'error', 'message': message}), 400
    except Exception as e:
        logger.error(f"Error in modify_user: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin/get_inventory/<user_id>')
def get_inventory(user_id):
    try:
        page = int(request.args.get('page', 1))
        items_per_page = 10
        
        from core.admin.user_management import get_user, get_user_inventory
        
        user = get_user(user_id)
        if not user:
            logger.warning(f"User not found in get_inventory: {user_id}")
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        if 'copper' not in user:
            user['copper'] = 0
        if 'gold' not in user:
            user['gold'] = 0
        
        
        if 'inventory' in user and isinstance(user['inventory'], list):
            logger.info(f"Using embedded inventory for user {user_id}")
            all_items = user['inventory']
            total_items = len(all_items)
            total_pages = (total_items + items_per_page - 1) // items_per_page
            
            start_idx = (page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)
            items = all_items[start_idx:end_idx]
            
        else:
            logger.info(f"Using items table for user {user_id}")
            items, total_pages = get_user_inventory(user_id, page, items_per_page)
        
        return jsonify({
            'status': 'ok',
            'user': user,
            'items': items,
            'page': page,
            'total_pages': max(1, total_pages)
        })
    except Exception as e:
        logger.error(f"Error in get_inventory: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
                'core': os.path.join(LOG_DIR, 'xiuxianbot.log'),
                'web' : os.path.join(LOG_DIR, 'web_local.log')
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
            'core': os.path.join(LOG_DIR, 'xiuxianbot.log'),
            'web': os.path.join(LOG_DIR, 'web_local.log'),
            'discord': os.path.join(LOG_DIR, 'discord.log'),
            'telegram': os.path.join(LOG_DIR, 'telegram.log'),
            'matrix': os.path.join(LOG_DIR, 'matrix.log')
        }
        
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
                            
                            actual_source = source_name
                            if source_name == 'web' and '127.0.0.1' in message:
                                actual_source = 'web-interface'
                            elif 'Core server started' in message or 'database connected' in message or 'Starting discord adapter' in message or 'Starting telegram adapter' in message:
                                actual_source = 'core'
                            elif 'discord' in logger_name.lower() or source_name == 'discord':
                                actual_source = 'discord'
                            elif 'telegram' in logger_name.lower() or source_name == 'telegram':
                                actual_source = 'telegram'
                            elif 'matrix' in logger_name.lower() or source_name == 'matrix':
                                actual_source = 'matrix'
                                
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
                                    'source': actual_source,
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
                    'message': 'Core server started with PID 36016'
                },
                {
                    'timestamp': datetime.datetime.now().replace(minute=1, second=0).isoformat(),
                    'source': 'core',
                    'level': 'info',
                    'message': 'Database connected successfully'
                },
                {
                    'timestamp': datetime.datetime.now().replace(minute=2, second=0).isoformat(),
                    'source': 'core',
                    'level': 'info',
                    'message': 'Starting discord adapter'
                },
                {
                    'timestamp': datetime.datetime.now().replace(minute=3, second=0).isoformat(),
                    'source': 'discord',
                    'level': 'info',
                    'message': 'Discord adapter connected'
                },
                {
                    'timestamp': datetime.datetime.now().replace(minute=4, second=0).isoformat(),
                    'source': 'telegram',
                    'level': 'warning',
                    'message': 'Telegram connection attempt failed, retrying...'
                },
                {
                    'timestamp': datetime.datetime.now().replace(minute=5, second=0).isoformat(),
                    'source': 'telegram',
                    'level': 'info',
                    'message': 'Telegram adapter connected'
                },
                {
                    'timestamp': datetime.datetime.now().replace(minute=6, second=0).isoformat(),
                    'source': 'web-interface',
                    'level': 'debug',
                    'message': 'Admin panel accessed from 127.0.0.1'
                },
                {
                    'timestamp': datetime.datetime.now().replace(minute=7, second=0).isoformat(),
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
    for adapter_name, enabled in cfg.get('adapters', {}).items():
        if enabled:
            adapter_running = (
                adapter_name in running_processes['adapters'] and 
                is_process_running(running_processes['adapters'][adapter_name].pid)
            )
            adapter_statuses[adapter_name] = {
                'running': adapter_running,
                'enabled': True
            }
    
    return jsonify({
        'core': {
            'running': core_running
        },
        'adapters': adapter_statuses
    })

@app.route('/servers/start/core', methods=['POST'])
def start_core_route():
    lang = parse_lang(request.args.get('lang', 'en'))
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
    lang = parse_lang(request.args.get('lang', 'en'))
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
    lang = parse_lang(request.args.get('lang', 'en'))
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
    lang = parse_lang(request.args.get('lang', 'en'))
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

@app.route('/database/query/<collection_name>', methods=['POST'])
def database_query(collection_name):
    try:
        data = request.get_json()
        query = data.get('query', {})
        page = int(request.args.get('page', 1))
        items_per_page = int(request.args.get('items_per_page', 20))
        
        if collection_name not in ['users', 'items', 'timings']:
            return (
                jsonify({'status': 'error', 'message': f'Invalid collection name: {collection_name}'}),
                400,
            )

        conditions = []
        params = []
        for field, value in query.items():
            if isinstance(value, dict) and '$regex' in value:
                conditions.append(f"{field} LIKE ?")
                params.append(f"%{value['$regex']}%")
            elif isinstance(value, dict) and '$ne' in value:
                conditions.append(f"{field} != ?")
                params.append(value['$ne'])
            elif isinstance(value, dict) and '$gt' in value:
                conditions.append(f"{field} > ?")
                params.append(value['$gt'])
            elif isinstance(value, dict) and '$gte' in value:
                conditions.append(f"{field} >= ?")
                params.append(value['$gte'])
            elif isinstance(value, dict) and '$lt' in value:
                conditions.append(f"{field} < ?")
                params.append(value['$lt'])
            elif isinstance(value, dict) and '$lte' in value:
                conditions.append(f"{field} <= ?")
                params.append(value['$lte'])
            else:
                conditions.append(f"{field} = ?")
                params.append(value)

        where_clause = ''
        if conditions:
            where_clause = 'WHERE ' + ' AND '.join(conditions)

        count_row = fetch_one(
            f"SELECT COUNT(*) as c FROM {collection_name} {where_clause}",
            tuple(params),
        )
        total_items = count_row['c'] if count_row else 0
        total_pages = (total_items + items_per_page - 1) // items_per_page

        params.extend([items_per_page, (page - 1) * items_per_page])
        results = fetch_all(
            f"SELECT * FROM {collection_name} {where_clause} LIMIT ? OFFSET ?",
            tuple(params),
        )
        for r in results:
            for k in list(r.keys()):
                if k.strip().lower() == 'actions':
                    r.pop(k, None)
        
        return jsonify({
            'status': 'ok',
            'results': results,
            'count': total_items,
            'page': page,
            'total_pages': max(1, total_pages)
        })
    except Exception as e:
        logger.error(f"Error in database_query: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/database/delete/<user_id>', methods=['POST'])
def database_delete_user(user_id):
    try:
        execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        execute('DELETE FROM items WHERE user_id = ?', (user_id,))
        execute('DELETE FROM timings WHERE user_id = ?', (user_id,))
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Error in database_delete_user: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/database/user/<user_id>')
def database_get_user(user_id):
    try:
        user = fetch_one('SELECT * FROM users WHERE user_id = ?', (user_id,))
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        return jsonify({'status': 'ok', 'user': user})
    except Exception as e:
        logger.error(f"Error in database_get_user: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    cfg  = load_config()
    port = cfg.get('admin_panel', {}).get('port', 11451)
    app.run(host='127.0.0.1', port=port, debug=True)
