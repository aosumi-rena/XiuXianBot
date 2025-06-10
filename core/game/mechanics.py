import random
import datetime
from typing import Dict, Any, Tuple, Optional, List, Union
import cnlunar

def initialize_game_mechanics():
    print("Game mechanics initialized successfully")
    print(f"Elements system loaded: {ELEMENTS}")
    print(f"Daily element: {get_daily_element()}")
    return True

ELEMENTS = ["木", "土", "水", "火", "金"]

RESTRAINED_ELEMENTS = {
    # "A": "B"     A is restrained by B
    "木": "火", 
    "火": "土", 
    "土": "金",  
    "金": "水",
    "水": "木"  
}

MUTUAL_ELEMENTS = {
    "木": "土", 
    "土": "水", 
    "水": "火",  
    "火": "金", 
    "金": "木" 
}

def get_element_multipliers(user_ele: str, daily_ele: str) -> Dict[str, Union[float, int]]:
    if user_ele == daily_ele:
        return {
            "cul": 1.5,
            "hunt_copper": 2.0,
            "hunt_gold": 2.0,
            "hunt_cultivation": 1.0,
            "asc_fail": 8
        }
    
    if RESTRAINED_ELEMENTS.get(user_ele) == daily_ele:
        return {
            "cul": 0.75,
            "hunt_copper": 0.75,
            "hunt_gold": 1.0,
            "hunt_cultivation": 0.75,
            "asc_fail": 15
        }
    
    if MUTUAL_ELEMENTS.get(user_ele) == daily_ele:
        return {
            "cul": 2.0,
            "hunt_copper": 1.5,
            "hunt_gold": 1.0,
            "hunt_cultivation": 2.0,
            "asc_fail": 10
        }
    
    return {
        "cul": 1.0,
        "hunt_copper": 1.0,
        "hunt_gold": 1.0,
        "hunt_cultivation": 1.0,
        "asc_fail": 10
    }

def get_daily_element() -> str:
    now_dt = datetime.datetime.now()
    lunar_date = datetime.datetime(now_dt.year, now_dt.month, now_dt.day, now_dt.hour, now_dt.minute)
    
    try:
        lunar = cnlunar.Lunar(lunar_date, godType="8char")
        elements_list = lunar.get_today5Elements()
        
        for word in elements_list:
            if word.startswith("属"):
                return word[1:]
    except Exception:
        pass
    
    return "未知"

DECAY_RATE = 4.0  # hours until gain halves, this will be moved to game constants config in future

def calculate_cultivation_gain(user_element: Optional[str] = None) -> int:
    base_gain = random.randint(150, 250)
    daily_element = get_daily_element()
    if user_element is None:
        multiplier = 1.0
    else:
        multiplier = get_element_multipliers(user_element, daily_element)["cul"]
    return int(base_gain * multiplier)

def start_cultivation(user_id: str, user_element: Optional[str] = None) -> Dict[str, Any]:
    gain_per_hour = calculate_cultivation_gain(user_element)
    start_time = datetime.datetime.now()
    return {
        "user_id": user_id,
        "start_time": int(start_time.timestamp()),
        "type": "cultivation",
        "base_gain": gain_per_hour,
    }

def calculate_cultivation_progress(timing: Dict[str, Any]) -> int:
    start = datetime.datetime.fromtimestamp(timing["start_time"])
    elapsed_hours = (datetime.datetime.now() - start).total_seconds() / 3600.0
    gain_per_hour = timing.get("base_gain", 0)
    total_gain = gain_per_hour * elapsed_hours * (0.5 ** (elapsed_hours / DECAY_RATE))
    return int(total_gain)

def calculate_hunt_rewards(user_data: Dict[str, Any], stage_max_value: int) -> Dict[str, int]:
    stage = user_data.get('rank', 0)
    
    if stage == 70:  # Max stage
        base_cultivation_gain = 0
    else:
        base_cultivation_gain = random.randint(int(stage_max_value * 0.0075), int(stage_max_value * 0.0125))
    
    base_copper_gain = random.randint(100, 200)
    base_gold_gain = 0
    
    gold_chance = min(0.006 * (stage / 10), 0.5)
    if random.random() < gold_chance:
        base_gold_gain = max(1, min(int(stage / 10), 10))
    
    daily_element = get_daily_element()
    user_element = user_data.get("element")
    
    if user_element is None:
        multipliers = {
            "hunt_cultivation": 1.0,
            "hunt_copper": 1.0,
            "hunt_gold": 1.0
        }
    else:
        element_multipliers = get_element_multipliers(user_element, daily_element)
        multipliers = {
            "hunt_cultivation": element_multipliers["hunt_cultivation"],
            "hunt_copper": element_multipliers["hunt_copper"],
            "hunt_gold": element_multipliers["hunt_gold"]
        }
    
    cultivation_gain = int(base_cultivation_gain * multipliers["hunt_cultivation"])
    copper_gain = int(base_copper_gain * multipliers["hunt_copper"])
    gold_gain = int(base_gold_gain * multipliers["hunt_gold"])
    
    return {
        "cultivation_gain": cultivation_gain,
        "copper_gain": copper_gain,
        "gold_gain": gold_gain
    }

def calculate_ascension_chance(user_data: Dict[str, Any]) -> Tuple[int, bool]:
    user_element = user_data.get("element")
    daily_element = get_daily_element()
    
    if user_element is None:
        failure_percentage = 10
    else:
        failure_percentage = get_element_multipliers(user_element, daily_element)["asc_fail"]
    
    asc_reduction = user_data.get("asc_reduction", 0)
    failure_percentage = max(1, failure_percentage - asc_reduction)
    
    success = random.randint(1, 100) > failure_percentage
    
    return failure_percentage, success
