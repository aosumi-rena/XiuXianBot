"""
Partially migrated legacy admin commands, acts as additional logics for the local admin dash
Buggy for now
"""

from typing import Dict, Any, Optional, List, Tuple
from core.database.connection import get_collection, DatabaseError

ADMIN_IDS = []

def load_admin_ids(admin_list: List[str]) -> None:

    global ADMIN_IDS
    ADMIN_IDS = admin_list

def is_admin(user_id: str) -> bool:

    return user_id in ADMIN_IDS

def get_user(user_id: str) -> Optional[Dict[str, Any]]:

    try:
        user_collection = get_collection('users')
        user = user_collection.find_one({"user_id": user_id})
        if user:
            return user
        
        return user_collection.find_one({"userid": user_id})
    except DatabaseError as e:
        raise e

def modify_user_field(user_id: str, field: str, action: str, value: int) -> Tuple[bool, str]:

    try:
        user_collection = get_collection('users')
        user = user_collection.find_one({"user_id": user_id})
        
        if not user:
            return False, f"User with ID {user_id} does not exist in the database."
        
        in_game_username = user.get("in_game_username", user_id)
        
        if not isinstance(value, int):
            try:
                value = int(value)
            except ValueError:
                return False, f"Failed to modify {in_game_username}'s {field}. Invalid value '{value}'."
        
        if action.lower() == "set":
            user_collection.update_one({"user_id": user_id}, {"$set": {field: value}})
            return True, f"Successfully set {in_game_username}'s {field} to {value}."
        
        elif action.lower() == "add":
            user_collection.update_one({"user_id": user_id}, {"$inc": {field: value}})
            return True, f"Successfully added {value} to {in_game_username}'s {field}."
        
        elif action.lower() == "minus":
            user_collection.update_one({"user_id": user_id}, {"$inc": {field: -value}})
            return True, f"Successfully subtracted {value} from {in_game_username}'s {field}."
        
        else:
            return False, f"Invalid action '{action}'. Use 'set', 'add', or 'minus'."
    
    except DatabaseError as e:
        return False, f"Database error: {str(e)}"

def modify_user_exp(user_id: str, action: str, value: int) -> Tuple[bool, str]:
    return modify_user_field(user_id, "exp", action, value)

def modify_user_copper(user_id: str, action: str, value: int) -> Tuple[bool, str]:
    return modify_user_field(user_id, "copper", action, value)

def modify_user_gold(user_id: str, action: str, value: int) -> Tuple[bool, str]:
    return modify_user_field(user_id, "gold", action, value)

def modify_user_rank(user_id: str, action: str, value: int) -> Tuple[bool, str]:
    return modify_user_field(user_id, "rank", action, value)

def get_all_users(limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:

    try:
        user_collection = get_collection('users')
        return list(user_collection.find().skip(skip).limit(limit))
    except DatabaseError as e:
        raise e

def search_users(query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:

    try:
        user_collection = get_collection('users')
        return list(user_collection.find(query).limit(limit))
    except DatabaseError as e:
        raise e

def get_user_inventory(user_id: str, page: int = 1, items_per_page: int = 10) -> Tuple[List[Dict[str, Any]], int]:

    try:
        items_collection = get_collection('items')
        
        total_items = items_collection.count_documents({"user_id": user_id})
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        items = list(items_collection.find(
            {"user_id": user_id},
            skip=(page - 1) * items_per_page,
            limit=items_per_page
        ))
        
        return items, max(1, total_pages)
    except DatabaseError as e:
        raise e
