"""
OTP system for account linking across platforms, not used yet
"""

import random
import time
import logging
from datetime import datetime, timedelta
from core.database.connection import get_collection, DatabaseError

logger = logging.getLogger(__name__)

class OTPManager:
    def __init__(self):
        self.otp_collection = get_collection('otp_codes')
        self.user_collection = get_collection('users')
        
    def generate_otp(self, user_id, purpose='account_link', expires_in_minutes=10):
        otp_code = str(random.randint(100000, 999999))
        
        expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
        
        otp_data = {
            "user_id": user_id,
            "otp_code": otp_code,
            "purpose": purpose,
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "used": False,
            "attempts": 0
        }
        
        try:
            self.otp_collection.delete_many({
                "user_id": user_id,
                "purpose": purpose,
                "used": False
            })
            
            self.otp_collection.insert_one(otp_data)
            logger.info(f"Generated OTP {otp_code} for user {user_id}")
            return otp_code
            
        except Exception as e:
            logger.error(f"Error generating OTP for user {user_id}: {e}")
            return None
    
    def verify_otp(self, user_id, otp_code, purpose='account_link'):
        try:
            otp_record = self.otp_collection.find_one({
                "user_id": user_id,
                "otp_code": otp_code,
                "purpose": purpose,
                "used": False
            })
            
            if not otp_record:
                logger.warning(f"OTP verification failed: No valid OTP found for user {user_id}")
                return False
            
            if datetime.now() > otp_record['expires_at']:
                logger.warning(f"OTP verification failed: OTP expired for user {user_id}")
                self.otp_collection.update_one(
                    {"_id": otp_record['_id']},
                    {"$set": {"used": True}}
                )
                return False
            
            if otp_record['attempts'] >= 3:
                logger.warning(f"OTP verification failed: Too many attempts for user {user_id}")
                self.otp_collection.update_one(
                    {"_id": otp_record['_id']},
                    {"$set": {"used": True}}
                )
                return False
            
            self.otp_collection.update_one(
                {"_id": otp_record['_id']},
                {"$set": {"used": True}}
            )
            
            logger.info(f"OTP verification successful for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying OTP for user {user_id}: {e}")
            return False
    
    def increment_attempt(self, user_id, otp_code, purpose='account_link'):
        try:
            self.otp_collection.update_one(
                {
                    "user_id": user_id,
                    "otp_code": otp_code,
                    "purpose": purpose,
                    "used": False
                },
                {"$inc": {"attempts": 1}}
            )
        except Exception as e:
            logger.error(f"Error incrementing OTP attempt for user {user_id}: {e}")
    
    def get_user_platforms(self, user_id):
        try:
            user = self.user_collection.find_one({"user_id": user_id})
            if not user:
                return []
            
            third_party_ids = user.get('third_party_ids', {})
            available_platforms = []
            
            platform_priority = ['discord', 'telegram', 'matrix']
            
            for platform in platform_priority:
                platform_id = third_party_ids.get(platform)
                if platform_id and platform_id.strip():
                    available_platforms.append(platform)
            
            return available_platforms
            
        except Exception as e:
            logger.error(f"Error getting user platforms for {user_id}: {e}")
            return []
    
    def find_user_by_platform_id(self, platform, platform_id):
        try:
            user = self.user_collection.find_one({
                f"third_party_ids.{platform}": platform_id
            })
            return user
        except Exception as e:
            logger.error(f"Error finding user by {platform} ID {platform_id}: {e}")
            return None
    
    def link_platform_account(self, user_id, platform, platform_id):
        try:
            existing_user = self.find_user_by_platform_id(platform, platform_id)
            if existing_user and existing_user['user_id'] != user_id:
                logger.warning(f"Platform ID {platform_id} already linked to user {existing_user['user_id']}")
                return False
            
            result = self.user_collection.update_one(
                {"user_id": user_id},
                {"$set": {f"third_party_ids.{platform}": platform_id}}
            )
            
            if result.matched_count > 0:
                logger.info(f"Successfully linked {platform} account {platform_id} to user {user_id}")
                return True
            else:
                logger.error(f"User {user_id} not found for platform linking")
                return False
                
        except Exception as e:
            logger.error(f"Error linking {platform} account for user {user_id}: {e}")
            return False
    
    def unlink_platform_account(self, user_id, platform):
        try:
            result = self.user_collection.update_one(
                {"user_id": user_id},
                {"$unset": {f"third_party_ids.{platform}": ""}}
            )
            
            if result.matched_count > 0:
                logger.info(f"Successfully unlinked {platform} account from user {user_id}")
                return True
            else:
                logger.error(f"User {user_id} not found for platform unlinking")
                return False
                
        except Exception as e:
            logger.error(f"Error unlinking {platform} account for user {user_id}: {e}")
            return False
    
    def cleanup_expired_otps(self):
        try:
            result = self.otp_collection.delete_many({
                "expires_at": {"$lt": datetime.now()}
            })
            logger.info(f"Cleaned up {result.deleted_count} expired OTP codes")
        except Exception as e:
            logger.error(f"Error cleaning up expired OTPs: {e}")

otp_manager = OTPManager()

def generate_otp(user_id, purpose='account_link', expires_in_minutes=10):
    return otp_manager.generate_otp(user_id, purpose, expires_in_minutes)

def verify_otp(user_id, otp_code, purpose='account_link'):
    return otp_manager.verify_otp(user_id, otp_code, purpose)

def get_user_platforms(user_id):
    return otp_manager.get_user_platforms(user_id)

def link_platform_account(user_id, platform, platform_id):
    return otp_manager.link_platform_account(user_id, platform, platform_id)

def unlink_platform_account(user_id, platform):
    return otp_manager.unlink_platform_account(user_id, platform)
