import os
import json
from datetime import datetime
from pymongo import MongoClient

client = None
db = None

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
    }

    users = user_collection.find()
    for user in users:
        update_data = {key: value for key, value in defaults.items() if key not in user}
        if update_data:
            user_collection.update_one({"_id": user["_id"]}, {"$set": update_data})

def connect_mongo():
    global client, db
    try:
        client = MongoClient("mongodb://localhost:27017")
        db = client['XiuXianGame']
        print("Connected to MongoDB.")
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


def backup_users_data():
    try:
        user_collection = get_collection("users")
        users_data = list(user_collection.find())

        for user in users_data:
            user["_id"] = str(user["_id"])

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M")
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../backups", date_str, "users")
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
        # Create backup directory: backups/<date>/items/
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../backups", date_str, "items")
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, f"{date_str}-{time_str}.json")
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(items_data, f, indent=4, ensure_ascii=False)
        return backup_file
    except Exception as e:
        print(f"Error during items backup: {e}")
        return None
    
'''

DataBase Explained:

_id                 ObjID       Randomly generated ID
user_id             Str         Main mode used for identity in server communication, same as Discord UID
discord_username    Str         Discord "tag"
in_game_username    Str         In game username to be displayed in messages
lang                Str         User's prefered localisation language
state               Bool        Whether user is cultivating
exp                 int32       User's current cultivation value
rank                int32       ID representing user's current cultivation stage 
dy_times            int32       Times user successfully hunted
copper              int32       Amount of copper user has (Currency)
gold                int32       Amount of gold user has (Precious currency)
asc_reduction       int32       User's reduction for chance of failing during ascending, due to equipped armor, 1-->9%_Fail | 2-->8%_Fail... 
sign                Bool        Whther user signed in today

'''