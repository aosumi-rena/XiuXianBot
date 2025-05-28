import os
import json
import logging
from datetime import datetime
from pymongo import MongoClient
from typing import Optional, Dict, Any, List

logger = logging.getLogger("Database")

client = None
db = None

class DatabaseError(Exception):
    pass

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

def connect_mongo(uri: str = None, db_name: str = None):
    global client, db
    
    if uri is None or db_name is None:
        config = load_config()
        uri = uri or config.get('db', {}).get('mongo_uri', "mongodb://localhost:27017")
        db_name = db_name or config.get('db', {}).get('mongo_db_name', "XiuXianGameV4")
    
    try:
        client = MongoClient(uri)
        db = client[db_name]
        logger.info(f"Connected to MongoDB database: {db_name}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise DatabaseError(f"Failed to connect to MongoDB: {e}")

def get_collection(collection_name: str):
    global db

    if db is None:
        raise DatabaseError("No database connection found. Call connect_mongo() first.")

    try:
        return db[collection_name]
    except KeyError as e:
        raise DatabaseError(f"Collection '{collection_name}' not found.") from e
    except Exception as e:
        raise DatabaseError(f"Unknown database error: {e}") from e

def ensure_defaults(user_collection, defaults: Dict[str, Any] = None):
    if defaults is None:
        from core.database.schemas import USER_DEFAULT_VALUES
        defaults = USER_DEFAULT_VALUES

    users = user_collection.find()
    for user in users:
        update_data = {key: value for key, value in defaults.items() if key not in user}
        if update_data:
            user_collection.update_one({"_id": user["_id"]}, {"$set": update_data})

def backup_collection(collection_name: str) -> Optional[str]:

    try:
        collection = get_collection(collection_name)
        data = list(collection.find())

        for item in data:
            item["_id"] = str(item["_id"])

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M")
        
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                 "backups", date_str, collection_name)
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_file = os.path.join(backup_dir, f"{date_str}-{time_str}.json")
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"Backup of {collection_name} created at {backup_file}")
        return backup_file
    except Exception as e:
        print(f"Error during {collection_name} backup: {e}")
        return None

def backup_users_data() -> Optional[str]:
    return backup_collection("users")

def backup_items_data() -> Optional[str]:
    return backup_collection("items")

def backup_timings_data() -> Optional[str]:
    return backup_collection("timings")
