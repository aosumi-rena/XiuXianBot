import logging
from datetime import datetime
from core.database.connection import fetch_one, DatabaseError
from core.utils.localisation import load_localisation, get_response

logger = logging.getLogger(__name__)

def get_user_status(user_id, lang="CHS"):
    try:
        user = fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
        
        if not user:
            return None
        
        localisation = load_localisation(lang)

        rank = user.get('rank', 1)
        stage_description = localisation.get('xx_stage_descriptions', {}).get(str(rank), "未知境界")
        max_exp = localisation.get('xx_stage_max', {}).get(str(rank), 1000)
        
        element = user.get("element")
        if element is None:
            element = "无" if lang.upper() == "CHS" else "None"
        elif lang.upper() != "CHS":
            ELEMENT_TRANSLATIONS = {
                "金": "Metallo", "木": "Dendro", "水": "Hydro",
                "火": "Pyro", "土": "Geo"
            }
            element = ELEMENT_TRANSLATIONS.get(element, element)
        
        current_exp = user.get('exp', 0)
        progress_percentage = (current_exp / max_exp) * 100 if max_exp > 0 else 0
        
        return {
            'user_id': user_id,
            'in_game_username': user.get('in_game_username', 'Unknown'),
            'rank': rank,
            'stage_description': stage_description,
            'exp': current_exp,
            'max_exp': max_exp,
            'progress_percentage': progress_percentage,
            'element': element,
            'copper': user.get('copper', 0),
            'gold': user.get('gold', 0),
            'dy_times': user.get('dy_times', 0),
            'state': user.get('state', False),
            'lang': user.get('lang', 'CHS'),
            'third_party_ids': user.get('third_party_ids', {})
        }
        
    except Exception as e:
        logger.error(f"Error getting user status for {user_id}: {e}")
        return None

def format_status_text(status_info, lang="CHS", platform=None):
    if not status_info:
        return "用户信息未找到 | User information not found"

    progress = status_info['progress_percentage']
    progress_bar_length = 10
    filled_length = int(progress_bar_length * progress / 100)
    progress_bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
    # Progress bar will be changed to discord emoji in future

    state_text = "修炼中" if status_info.get("state") else "空闲"
    if lang.upper() != "CHS":
        state_text = "Cultivating" if status_info.get("state") else "Idle"

    _, text = get_response(
        "user_status",
        lang=lang,
        platform=platform,
        in_game_username=status_info.get("in_game_username"),
        user_id=status_info.get("user_id"),
        stage_description=status_info.get("stage_description"),
        rank=status_info.get("rank"),
        exp=status_info.get("exp"),
        max_exp=status_info.get("max_exp"),
        element=status_info.get("element"),
        copper=status_info.get("copper"),
        gold=status_info.get("gold"),
        dy_times=status_info.get("dy_times"),
        state_text=state_text,
        progress_bar=progress_bar,
        progress=progress,
    )
    return text

def check_user_exists(user_id):
    try:
        user = fetch_one("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        return user is not None
    except Exception as e:
        logger.error(f"Error checking user existence for {user_id}: {e}")
        return False
