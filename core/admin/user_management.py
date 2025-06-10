
from typing import Dict, Any, Optional, List, Tuple
from core.database.connection import (
    fetch_one,
    fetch_all,
    execute,
    DatabaseError,
)

ADMIN_IDS = []

def load_admin_ids(admin_list: List[str]) -> None:
    global ADMIN_IDS
    ADMIN_IDS = admin_list

def is_admin(user_id: str) -> bool:
    return user_id in ADMIN_IDS

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    try:
        return fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
    except Exception as e:
        raise DatabaseError(str(e))

def modify_user_field(user_id: str, field: str, action: str, value: int) -> Tuple[bool, str]:
    try:
        user = fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))

        if not user:
            return False, f"User with ID {user_id} does not exist in the database."

        in_game_username = user.get("in_game_username", user_id)
        
        if not isinstance(value, int):
            try:
                value = int(value)
            except ValueError:
                return False, f"Failed to modify {in_game_username}'s {field}. Invalid value '{value}'."
        
        if action.lower() == "set":
            execute(
                f"UPDATE users SET {field} = ? WHERE user_id = ?",
                (value, user_id),
            )
            return True, f"Successfully set {in_game_username}'s {field} to {value}."

        elif action.lower() == "add":
            execute(
                f"UPDATE users SET {field} = {field} + ? WHERE user_id = ?",
                (value, user_id),
            )
            return True, f"Successfully added {value} to {in_game_username}'s {field}."

        elif action.lower() == "minus":
            execute(
                f"UPDATE users SET {field} = {field} - ? WHERE user_id = ?",
                (value, user_id),
            )
            return True, f"Successfully subtracted {value} from {in_game_username}'s {field}."
        
        else:
            return False, f"Invalid action '{action}'. Use 'set', 'add', or 'minus'."
    
    except Exception as e:
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
        return fetch_all(
            "SELECT * FROM users LIMIT ? OFFSET ?",
            (limit, skip),
        )
    except Exception as e:
        raise DatabaseError(str(e))

def search_users(query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
    try:
        if "in_game_username" in query:
            regex = query["in_game_username"].get("$regex") if isinstance(query["in_game_username"], dict) else query["in_game_username"]
            pattern = f"%{regex}%"
            return fetch_all(
                "SELECT * FROM users WHERE in_game_username LIKE ? LIMIT ?",
                (pattern, limit),
            )
        if "user_id" in query:
            return fetch_all(
                "SELECT * FROM users WHERE user_id = ? LIMIT ?",
                (query["user_id"], limit),
            )
        return []
    except Exception as e:
        raise DatabaseError(str(e))

def get_user_inventory(user_id: str, page: int = 1, items_per_page: int = 10) -> Tuple[List[Dict[str, Any]], int]:
    try:
        count_row = fetch_one(
            "SELECT COUNT(*) as c FROM items WHERE user_id = ?",
            (user_id,),
        )
        total_items = count_row["c"] if count_row else 0
        total_pages = (total_items + items_per_page - 1) // items_per_page

        items = fetch_all(
            "SELECT * FROM items WHERE user_id = ? LIMIT ? OFFSET ?",
            (user_id, items_per_page, (page - 1) * items_per_page),
        )

        return items, max(1, total_pages)
    except Exception as e:
        raise DatabaseError(str(e))
