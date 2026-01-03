from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import config

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(config.MONGO_URI)
        self.db = self.client[config.DATABASE_NAME]
        self.users = self.db.users
        self.sessions = self.db.sessions
        self.extraction_jobs = self.db.extraction_jobs
        self.settings = self.db.settings
        self.stats = self.db.stats
        
    async def init_db(self):
        """Initialize database indexes"""
        await self.users.create_index("user_id", unique=True)
        await self.sessions.create_index("user_id", unique=True)
        await self.extraction_jobs.create_index("user_id")
        await self.settings.create_index("user_id", unique=True)
        
    # ===== USER MANAGEMENT =====
    async def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """Add or update user in database"""
        await self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "username": username,
                    "first_name": first_name,
                    "last_active": datetime.utcnow()
                },
                "$setOnInsert": {
                    "user_id": user_id,
                    "is_premium": False,
                    "premium_expiry": None,
                    "joined_date": datetime.utcnow(),
                    "total_extractions": 0,
                    "total_downloads": 0
                }
            },
            upsert=True
        )
        return await self.get_user(user_id)
    
    async def get_user(self, user_id: int):
        """Get user data"""
        return await self.users.find_one({"user_id": user_id})
    
    async def update_user_activity(self, user_id: int):
        """Update last active time"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"last_active": datetime.utcnow()}}
        )
    
    # ===== PREMIUM MANAGEMENT =====
    async def add_premium(self, user_id: int, days: int = 30):
        """Add premium to user"""
        expiry_date = datetime.utcnow() + timedelta(days=days)
        await self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "is_premium": True,
                    "premium_expiry": expiry_date,
                    "premium_added_date": datetime.utcnow()
                }
            }
        )
        return expiry_date
    
    async def remove_premium(self, user_id: int):
        """Remove premium from user"""
        await self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "is_premium": False,
                    "premium_expiry": None
                }
            }
        )
    
    async def check_premium(self, user_id: int):
        """Check if user has active premium"""
        user = await self.get_user(user_id)
        if not user or not user.get("is_premium"):
            return False
        
        expiry = user.get("premium_expiry")
        if expiry and expiry > datetime.utcnow():
            return True
        else:
            # Premium expired, remove it
            await self.remove_premium(user_id)
            return False
    
    async def transfer_premium(self, from_user: int, to_user: int):
        """Transfer premium from one user to another"""
        from_user_data = await self.get_user(from_user)
        if not from_user_data or not from_user_data.get("is_premium"):
            return False
        
        expiry = from_user_data.get("premium_expiry")
        remaining_days = max(0, (expiry - datetime.utcnow()).days)
        
        await self.remove_premium(from_user)
        await self.add_premium(to_user, remaining_days)
        return True
    
    # ===== SESSION MANAGEMENT =====
    async def save_session(self, user_id: int, session_string: str, phone: str = None):
        """Save user's Pyrogram session"""
        await self.sessions.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "session_string": session_string,
                    "phone": phone,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
    
    async def get_session(self, user_id: int):
        """Get user's session"""
        return await self.sessions.find_one({"user_id": user_id})
    
    async def delete_session(self, user_id: int):
        """Delete user's session"""
        await self.sessions.delete_one({"user_id": user_id})
    
    # ===== SETTINGS MANAGEMENT =====
    async def get_settings(self, user_id: int):
        """Get user settings"""
        settings = await self.settings.find_one({"user_id": user_id})
        if not settings:
            # Default settings
            settings = {
                "user_id": user_id,
                "chat_id": None,
                "custom_caption": None,
                "rename_format": None,
                "thumbnail": None,
                "watermark": None,
                "replace_words": {}
            }
            await self.settings.insert_one(settings)
        return settings
    
    async def update_settings(self, user_id: int, **kwargs):
        """Update user settings"""
        await self.settings.update_one(
            {"user_id": user_id},
            {"$set": kwargs},
            upsert=True
        )
    
    async def reset_settings(self, user_id: int):
        """Reset user settings to default"""
        await self.settings.delete_one({"user_id": user_id})
    
    # ===== EXTRACTION JOBS =====
    async def create_job(self, user_id: int, job_type: str, total_messages: int):
        """Create new extraction job"""
        job = {
            "user_id": user_id,
            "job_type": job_type,
            "total_messages": total_messages,
            "processed": 0,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.extraction_jobs.insert_one(job)
        job["_id"] = result.inserted_id
        return job
    
    async def update_job_progress(self, job_id, processed: int):
        """Update job progress"""
        await self.extraction_jobs.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "processed": processed,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    async def cancel_job(self, job_id):
        """Cancel extraction job"""
        await self.extraction_jobs.update_one(
            {"_id": job_id},
            {"$set": {"status": "cancelled"}}
        )
    
    async def get_active_job(self, user_id: int):
        """Get active job for user"""
        return await self.extraction_jobs.find_one(
            {"user_id": user_id, "status": "active"}
        )
    
    # ===== STATISTICS =====
    async def get_stats(self):
        """Get bot statistics"""
        total_users = await self.users.count_documents({})
        premium_users = await self.users.count_documents({"is_premium": True})
        total_extractions = await self.extraction_jobs.count_documents({})
        
        return {
            "total_users": total_users,
            "premium_users": premium_users,
            "free_users": total_users - premium_users,
            "total_extractions": total_extractions
        }
    
    async def increment_user_stat(self, user_id: int, field: str):
        """Increment user statistic"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$inc": {field: 1}}
        )
    
    async def get_all_users(self):
        """Get all user IDs (for owner)"""
        users = await self.users.find({}, {"user_id": 1, "username": 1, "is_premium": 1}).to_list(None)
        return users

# Global database instance
db = Database()
