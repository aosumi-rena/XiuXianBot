"""
Core server module
"""

import logging
import time
import threading
from flask import Flask, jsonify, request
from core.database.connection import connect_mongo, get_collection, ensure_defaults
from core.game.mechanics import initialize_game_mechanics

logger = logging.getLogger(__name__)

core_app = Flask(__name__)
core_app.config['JSON_AS_ASCII'] = False

server_running = False
server_thread = None

def initialize_core_components():
    try:
        logger.info("Initializing core components...")
        
        connect_mongo()
        logger.info("Database connection established")
        
        user_collection = get_collection('users')
        ensure_defaults(user_collection)
        logger.info("Database defaults ensured")
        
        initialize_game_mechanics()
        logger.info("Game mechanics initialized")
        
        logger.info("All core components initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize core components: {e}")
        return False

@core_app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Core server is running',
        'timestamp': time.time()
    })

@core_app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user_collection = get_collection('users')
        user = user_collection.find_one({"user_id": user_id})
        
        if user:
            user['_id'] = str(user['_id'])
            return jsonify({'success': True, 'user': user})
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@core_app.route('/api/user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        user_collection = get_collection('users')
        
        existing_user = user_collection.find_one({"user_id": data.get('user_id')})
        if existing_user:
            return jsonify({'success': False, 'message': 'User already exists'}), 400
        
        result = user_collection.insert_one(data)
        return jsonify({
            'success': True, 
            'message': 'User created successfully',
            'user_id': data.get('user_id')
        })
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@core_app.route('/api/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        user_collection = get_collection('users')
        
        result = user_collection.update_one(
            {"user_id": user_id},
            {"$set": data}
        )
        
        if result.matched_count > 0:
            return jsonify({'success': True, 'message': 'User updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404
            
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@core_app.route('/api/link-account', methods=['POST'])
def link_account():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        platform = data.get('platform')
        platform_id = data.get('platform_id')
        
        if not all([user_id, platform, platform_id]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        user_collection = get_collection('users')
        
        result = user_collection.update_one(
            {"user_id": user_id},
            {"$set": {f"third_party_ids.{platform}": platform_id}}
        )
        
        if result.matched_count > 0:
            return jsonify({'success': True, 'message': f'Account linked to {platform}'})
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404
            
    except Exception as e:
        logger.error(f"Error linking account: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@core_app.route('/api/unlink-account', methods=['POST'])
def unlink_account():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        platform = data.get('platform')
        
        if not all([user_id, platform]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        user_collection = get_collection('users')
        
        result = user_collection.update_one(
            {"user_id": user_id},
            {"$unset": {f"third_party_ids.{platform}": ""}}
        )
        
        if result.matched_count > 0:
            return jsonify({'success': True, 'message': f'Account unlinked from {platform}'})
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404
            
    except Exception as e:
        logger.error(f"Error unlinking account: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

def run_core_server():
    global server_running
    server_running = True
    
    try:
        logger.info("Starting core server on localhost:11451")
        core_app.run(host='127.0.0.1', port=11451, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Core server error: {e}")
    finally:
        server_running = False

def start_server():
    global server_thread, server_running
    
    if server_running:
        logger.info("Core server is already running")
        return True
    
    if not initialize_core_components():
        logger.error("Failed to initialize core components")
        return False
    
    server_thread = threading.Thread(target=run_core_server, daemon=True)
    server_thread.start()
    
    time.sleep(1)
    
    logger.info("Core server started successfully")
    return True

def stop_server():
    global server_running
    server_running = False
    logger.info("Core server stopped")

if __name__ == "__main__":
    start_server()
    try:
        while server_running:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_server()
