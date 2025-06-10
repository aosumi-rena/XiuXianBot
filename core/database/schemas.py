from typing import Dict, Any, Union, List

USER_SCHEMA = {
    "user_id": str,           # Unique identifier, same as platform UID
    "third_party_ids": {      # To let bot know which user is controlling which account
        "discord": str,         
        "telegram": str,
        "matrix": str
    },
    "in_game_username": str,  # Display name in game
    "lang": str,              # User's preferred localization language (default: "CHS")
    "state": bool,            # Whether user is cultivating
    "exp": int,               # User's current cultivation value
    "rank": int,              # ID representing user's current cultivation stage
    "dy_times": int,          # Times user successfully hunted
    "copper": int,            # Amount of copper user has (basic currency)
    "gold": int,              # Amount of gold user has (premium currency)
    "asc_reduction": int,     # Reduction for ascension failure chance
    "sign": bool,             # Whether user signed in today
    "element": str,           # User's chosen element (金, 木, 水, 火, 土,)
}

USER_DEFAULT_VALUES = {
    "lang": "CHS",
    "state": False,
    "exp": 0,
    "rank": 1,
    "dy_times": 0,
    "copper": 0,
    "gold": 0,
    "asc_reduction": 0,
    "sign": False,
    "element": None,
}

ITEM_SCHEMA = {
    "owner": str,             # User ID of the owner
    "item": Union[int, str],  # Item identifier
    "quantity": int,          # Amount of the item
    "level": int,             # For leveled items
}

TIMING_SCHEMA = {
    "user_id": str,           # User ID
    "start_time": int,        # Unix timestamp
    "type": str,              # "cultivation" or "hunt_cd"
    "base_gain": int,         # Base hourly gain for cultivation
}

COLLECTIONS = {
    "USERS": "users",
    "ITEMS": "items",
    "TIMINGS": "timings",
}

def create_default_user(user_id: str, username: str = None) -> Dict[str, Any]:
    user_data = USER_DEFAULT_VALUES.copy()
    user_data["user_id"] = user_id
    user_data["in_game_username"] = username if username else user_id
    return user_data

def validate_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    validated_data = {}
    
    for field, field_type in USER_SCHEMA.items():
        if field not in user_data and field not in USER_DEFAULT_VALUES:
            raise ValueError(f"Required field '{field}' is missing")
        
        value = user_data.get(field, USER_DEFAULT_VALUES.get(field))
        
        if field_type == int and not isinstance(value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise ValueError(f"Field '{field}' must be an integer")
        
        elif field_type == bool and not isinstance(value, bool):
            if isinstance(value, str):
                value = value.lower() in ('true', 'yes', '1')
            else:
                value = bool(value)
        
        validated_data[field] = value
    
    return validated_data
