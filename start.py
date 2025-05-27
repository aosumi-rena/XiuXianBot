import os
import sys
import json
import subprocess
import threading
import importlib.util
import logging
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("xiuxianbot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("XiuXianBot")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')

adapter_processes = {}

def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

def start_web_local(config):
    try:
        port = config.get('admin_panel', {}).get('port', 11451)
        logger.info(f"Starting local admin dashboard on port {port}")
        
        web_local_path = os.path.join(BASE_DIR, 'web_local', 'app.py')
        
        if not os.path.exists(web_local_path):
            logger.error(f"Web local app not found: {web_local_path}")
            return None
        
        web_local_dir = os.path.dirname(web_local_path)
        if web_local_dir not in sys.path:
            sys.path.insert(0, web_local_dir)
            
        spec = importlib.util.spec_from_file_location("app", web_local_path)
        web_local = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(web_local)
        
        def run_flask_app():
            web_local.app.run(host='127.0.0.1', port=port, debug=False)
        
        flask_thread = threading.Thread(target=run_flask_app, daemon=True)
        flask_thread.start()
        
        adapter_processes['web_local'] = flask_thread
        
        logger.info(f"Local admin dashboard started at http://127.0.0.1:{port}")
        return flask_thread
    except Exception as e:
        logger.error(f"Failed to start local admin dashboard: {e}")
        return None

def start_adapter(adapter_name, config):
    try:
        if not config.get('adapters', {}).get(adapter_name, False):
            logger.info(f"Adapter {adapter_name} is disabled in config")
            return None
        
        logger.info(f"Starting {adapter_name} adapter")
        adapter_path = os.path.join(BASE_DIR, 'adapters', adapter_name, 'bot.py')
        
        if not os.path.exists(adapter_path):
            logger.error(f"Adapter path not found: {adapter_path}")
            return None
        
        process = subprocess.Popen(
            [sys.executable, adapter_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        adapter_processes[adapter_name] = process
        logger.info(f"{adapter_name} adapter started with PID {process.pid}")
        return process
    except Exception as e:
        logger.error(f"Failed to start {adapter_name} adapter: {e}")
        return None

def stop_adapter(adapter_name):
    if adapter_name in adapter_processes:
        process = adapter_processes[adapter_name]
        logger.info(f"Stopping {adapter_name} adapter (PID {process.pid})")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        del adapter_processes[adapter_name]
        logger.info(f"{adapter_name} adapter stopped")
        return True
    return False

def main():
    logger.info("Starting XiuXianBot")
    
    config = load_config()
    if not config:
        logger.error("Failed to load configuration. Exiting.")
        return
    
    web_thread = start_web_local(config)
    if not web_thread:
        logger.error("Failed to start local admin dashboard. Exiting.")
        return
    
    try:
        logger.info("XiuXianBot is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down...")
        for adapter_name in list(adapter_processes.keys()):
            stop_adapter(adapter_name)
        logger.info("XiuXianBot stopped")

if __name__ == "__main__":
    main()
