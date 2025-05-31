import logging
from datetime import datetime
from core.database.connection import get_collection, DatabaseError
from core.utils.localisation import load_localisation

logger = logging.getLogger(__name__)

def get_user_status(user_id, lang="CHS"):
    try:
        user_collection = get_collection('users')
        user = user_collection.find_one({"user_id": user_id})
        
        if not user:
            return None
        
        localisation = load_localisation(lang)
        
        rank = user.get('rank', 1)
        stage_description = localisation['xx_stage_descriptions'].get(str(rank), "未知境界")
        max_exp = localisation['xx_stage_max'].get(str(rank), 1000)
        
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

def format_status_text(status_info, lang="CHS"):
    if not status_info:
        return "用户信息未找到 | User information not found"
    
    progress = status_info['progress_percentage']
    progress_bar_length = 10
    filled_length = int(progress_bar_length * progress / 100)
    progress_bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
    
    if lang.upper() == "CHS":
        return (
            f"👤 **{status_info['in_game_username']}**\n"
            f"🆔 UID: `{status_info['user_id']}`\n"
            f"⭐ 境界: {status_info['stage_description']} (第{status_info['rank']}重)\n"
            f"💫 修为: {status_info['exp']:,}/{status_info['max_exp']:,}\n"
            f"📊 进度: {progress_bar} {progress:.1f}%\n"
            f"🔥 元素: {status_info['element']}\n"
            f"💰 铜币: {status_info['copper']:,}\n"
            f"💎 元宝: {status_info['gold']:,}\n"
            f"📅 每日次数: {status_info['dy_times']}/3\n"
            f"🧘 状态: {'修炼中' if status_info['state'] else '空闲'}"
        )
    else:
        return (
            f"👤 **{status_info['in_game_username']}**\n"
            f"🆔 UID: `{status_info['user_id']}`\n"
            f"⭐ Stage: {status_info['stage_description']} (Level {status_info['rank']})\n"
            f"💫 Cultivation: {status_info['exp']:,}/{status_info['max_exp']:,}\n"
            f"📊 Progress: {progress_bar} {progress:.1f}%\n"
            f"🔥 Element: {status_info['element']}\n"
            f"💰 Copper: {status_info['copper']:,}\n"
            f"💎 Gold: {status_info['gold']:,}\n"
            f"📅 Daily Times: {status_info['dy_times']}/3\n"
            f"🧘 State: {'Cultivating' if status_info['state'] else 'Idle'}"
        )

def check_user_exists(user_id):
    try:
        user_collection = get_collection('users')
        user = user_collection.find_one({"user_id": user_id})
        return user is not None
    except Exception as e:
        logger.error(f"Error checking user existence for {user_id}: {e}")
        return False
