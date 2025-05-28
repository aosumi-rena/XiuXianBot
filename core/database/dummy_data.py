"""
This file is to generate and write dummy data into database for testing.

Keys and values here may not neccessarily be the actual game
ones, only for references and debugging.
"""

import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from bson import ObjectId

from core.database.connection import get_collection, connect_mongo
from core.database.schemas import USER_DEFAULT_VALUES

logger = logging.getLogger("DummyData")

ELEMENTS = ["木", "土", "水", "火", "金"]
RANKS = [
    "练气期", "筑基期", "金丹期", "元婴期", "化神期", 
    "炼虚期", "合体期", "大乘期", "渡劫期", "仙人"
]
ITEM_TYPES = [
    "丹药", "法宝", "符箓", "灵草", "灵石", 
    "功法", "秘籍", "材料", "装备", "杂物"
]
ITEM_NAMES = {
    "丹药": ["回气丹", "聚灵丹", "培元丹", "固元丹", "金元丹", "玄元丹"],
    "法宝": ["飞剑", "灵符", "法印", "灵珠", "玉简", "灵幡"],
    "符箓": ["火符", "水符", "雷符", "风符", "土符", "金符"],
    "灵草": ["灵芝", "人参", "何首乌", "龙血草", "天山雪莲", "九叶灵芝"],
    "灵石": ["下品灵石", "中品灵石", "上品灵石", "极品灵石"],
    "功法": ["太极功", "玄阴功", "纯阳功", "五行功", "九阴真经", "九阳神功"],
    "秘籍": ["剑法", "刀法", "拳法", "掌法", "腿法", "指法"],
    "材料": ["铁", "铜", "银", "金", "玄铁", "寒铁"],
    "装备": ["剑", "刀", "枪", "戟", "斧", "钺"],
    "杂物": ["符纸", "墨", "笔", "砚", "香", "茶"]
}

def generate_dummy_users(count: int = 20) -> List[Dict[str, Any]]:
    users = []
    
    for i in range(count):
        user_id = str(1000000 + i)
        username = f"修仙者_{i+1}"
        
        rank = random.randint(0, min(9, i // 2))
        exp = random.randint(rank * 1000, (rank + 1) * 1000 - 1)
        copper = random.randint(100, 10000)
        gold = random.randint(0, 100)
        element = random.choice(ELEMENTS)
        
        user = USER_DEFAULT_VALUES.copy()
        
        user.update({
            "_id": ObjectId(),
            "user_id": user_id,
            "in_game_username": username,
            "rank": rank,
            "exp": exp,
            "copper": copper,
            "gold": gold,
            "element": element,
            "dy_times": random.randint(0, 100),
            "asc_reduction": random.randint(0, 10),
            "sign": random.choice([True, False]),
            "state": random.choice([True, False])
        })
        
        users.append(user)
    
    return users

def generate_dummy_items(users: List[Dict[str, Any]], items_per_user: int = 5) -> List[Dict[str, Any]]:

    items = []
    
    for user in users:
        user_id = user["user_id"]
        user_rank = user["rank"]
        
        num_items = random.randint(1, items_per_user * 2)
        
        for _ in range(num_items):
            item_type = random.choice(ITEM_TYPES)
            item_name = random.choice(ITEM_NAMES[item_type])
            
            level = random.randint(1, max(1, user_rank + 1))
            quantity = random.randint(1, 10)
            
            item = {
                "_id": ObjectId(),
                "user_id": user_id,
                "item_type": item_type,
                "item_name": item_name,
                "level": level,
                "quantity": quantity,
                "created_at": datetime.now() - timedelta(days=random.randint(0, 30))
            }
            
            items.append(item)
    
    return items

def generate_dummy_timings(users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    timings = []
    now = int(time.time())
    
    for user in users:
        user_id = user["user_id"]
        
        if user["state"]:
            start_time = now - random.randint(0, 3600 * 12) 
            end_time = start_time + random.randint(3600, 3600 * 24)  

            culti_gain = random.randint(10, 100) * (user["rank"] + 1)
            
            timing = {
                "_id": ObjectId(),
                "user_id": user_id,
                "start_time": start_time,
                "end_time": end_time,
                "type": "cultivation",
                "culti_gain": culti_gain
            }
            
            timings.append(timing)
        
        if random.random() < 0.3:  
            start_time = now - random.randint(0, 1800)  
            end_time = start_time + random.randint(300, 3600)  
            
            timing = {
                "_id": ObjectId(),
                "user_id": user_id,
                "start_time": start_time,
                "end_time": end_time,
                "type": "hunt_cd"
            }
            
            timings.append(timing)
    
    return timings

def insert_dummy_data(users_count: int = 20, clear_existing: bool = False) -> Dict[str, int]:

    try:
        connect_mongo()
        
        users_collection = get_collection("users")
        items_collection = get_collection("items")
        timings_collection = get_collection("timings")
        
        if clear_existing:
            users_collection.delete_many({})
            items_collection.delete_many({})
            timings_collection.delete_many({})
            logger.info("Cleared existing data from collections")
        
        users = generate_dummy_users(users_count)
        items = generate_dummy_items(users)
        timings = generate_dummy_timings(users)
        
        if users:
            users_collection.insert_many(users)
        
        if items:
            items_collection.insert_many(items)
        
        if timings:
            timings_collection.insert_many(timings)
        
        logger.info(f"Inserted {len(users)} users, {len(items)} items, and {len(timings)} timings")
        
        return {
            "users": len(users),
            "items": len(items),
            "timings": len(timings)
        }
    except Exception as e:
        logger.error(f"Error inserting dummy data: {e}")
        return {
            "users": 0,
            "items": 0,
            "timings": 0,
            "error": str(e)
        }

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    result = insert_dummy_data(clear_existing=True)
    print(f"Inserted dummy data: {result}")
