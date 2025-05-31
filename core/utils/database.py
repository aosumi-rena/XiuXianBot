import os
import json
from datetime import datetime
from pymongo import MongoClient

client = None
db = None

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load config: {e}")
        return {}

def ensure_defaults(user_collection):
    defaults = {
        "lang": "CHS",
        "state": False,
        "exp": 0,
        "rank": 1,
        "dy_times": 0,
        "copper": 0,
        "gold": 0,
        "asc_reduction": 0,
        "sign": False,
        "third_party_ids": {}
    }

    users = user_collection.find()
    for user in users:
        update_data = {key: value for key, value in defaults.items() if key not in user}
        if update_data:
            user_collection.update_one({"_id": user["_id"]}, {"$set": update_data})

def connect_mongo():
    global client, db
    config = load_config()
    uri = config.get('db', {}).get('mongo_uri', "mongodb://localhost:27017")
    db_name = config.get('db', {}).get('mongo_db_name', "XiuXianGameV4")
    
    try:
        client = MongoClient(uri)
        db = client[db_name]
        print(f"Connected to MongoDB database: {db_name}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

class DatabaseError(Exception):
    pass

def get_collection(collection_name):
    global db

    if db is None:
        raise DatabaseError("No database connection found.")

    try:
        return db[collection_name]
    except KeyError as e:
        raise DatabaseError(f"Collection '{collection_name}' not found.") from e
    except Exception as e:
        raise DatabaseError(f"Unknown database error: {e}") from e

def generate_universal_uid():
    try:
        user_collection = get_collection('users')
        highest_user = user_collection.find_one(
            {"user_id": {"$regex": "^[0-9]+$"}}, 
            sort=[("user_id", -1)]
        )
        if highest_user:
            next_uid = int(highest_user["user_id"]) + 1
        else:
            next_uid = 1000001
        return str(next_uid)
    except Exception as e:
        print(f"Error generating UID: {e}")
        return None

def migrate_existing_accounts():
    try:
        user_collection = get_collection('users')
        
        users_to_migrate = user_collection.find({
            "user_id": {"$not": {"$regex": "^[0-9]+$"}}
        })
        
        migrated_count = 0
        for user in users_to_migrate:
            old_user_id = user["user_id"]
            new_uid = generate_universal_uid()
            
            if not new_uid:
                print(f"Failed to generate UID for user {old_user_id}")
                continue
            
            platform = None
            if old_user_id.isdigit() and len(old_user_id) > 10:
                platform = "discord"
            elif old_user_id.isdigit():
                platform = "telegram"
            else:
                third_party_ids = user.get("third_party_ids", {})
                if third_party_ids.get("discord") == old_user_id:
                    platform = "discord"
                elif third_party_ids.get("telegram") == old_user_id:
                    platform = "telegram"
                else:
                    platform = "discord"
            
            update_data = {
                "user_id": new_uid
            }
            
            if "third_party_ids" not in user:
                update_data["third_party_ids"] = {
                    "discord": "",
                    "telegram": "",
                    "matrix": ""
                }
            
            update_data[f"third_party_ids.{platform}"] = old_user_id
            
            user_collection.update_one(
                {"_id": user["_id"]},
                {"$set": update_data}
            )
            
            print(f"Migrated user {old_user_id} ({platform}) to universal UID {new_uid}")
            migrated_count += 1
            
        print(f"Migration completed: {migrated_count} accounts migrated")
        return True
        
    except Exception as e:
        print(f"Error migrating accounts: {e}")
        return False

def ensure_universal_uid_compatibility():
    try:
        user_collection = get_collection('users')
        
        all_users = user_collection.find({})
        updated_count = 0
        
        for user in all_users:
            needs_update = False
            update_data = {}
            
            if "third_party_ids" not in user:
                update_data["third_party_ids"] = {
                    "discord": "",
                    "telegram": "",
                    "matrix": ""
                }
                needs_update = True
            else:
                third_party_ids = user["third_party_ids"]
                for platform in ["discord", "telegram", "matrix"]:
                    if platform not in third_party_ids:
                        update_data[f"third_party_ids.{platform}"] = ""
                        needs_update = True
            
            if needs_update:
                user_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": update_data}
                )
                updated_count += 1
        
        print(f"Compatibility update completed: {updated_count} accounts updated")
        return True
        
    except Exception as e:
        print(f"Error ensuring compatibility: {e}")
        return False

def backup_users_data():
    try:
        user_collection = get_collection("users")
        users_data = list(user_collection.find())

        for user in users_data:
            user["_id"] = str(user["_id"])

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M")
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../backups", date_str, "users")
        os.makedirs(backup_dir, exist_ok=True)

        backup_file = os.path.join(backup_dir, f"{date_str}-{time_str}.json")
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(users_data, f, indent=4, ensure_ascii=False)
        return backup_file
    except Exception as e:
        print(f"Error during backup: {e}")
        return None

def backup_items_data():
    try:
        items_collection = get_collection("items")
        items_data = list(items_collection.find())

        for item in items_data:
            item["_id"] = str(item["_id"])
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M")
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../backups", date_str, "items")
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, f"{date_str}-{time_str}.json")
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(items_data, f, indent=4, ensure_ascii=False)
        return backup_file
    except Exception as e:
        print(f"Error during items backup: {e}")
        return None
