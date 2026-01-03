import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8513397474:AAFuSpGil8u0jFObL41NbmLGdHI7pE3Q-4k")
API_ID = int(os.getenv("API_ID", "20598098"))
API_HASH = os.getenv("API_HASH", "c1727e40f8585b869cef73b828b2bf69")

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://UNIVORA_SAVER:aaghaz9431@univorasaver.6st7ygj.mongodb.net/?appName=UNIVORASAVER")
DATABASE_NAME = "extractor_bot"

# Bot Configuration
OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # Set your Telegram user ID here
MAX_CONCURRENT_EXTRACTIONS = 3
PREMIUM_MAX_BATCH = 10000
FREE_MAX_BATCH = 3

# Server Configuration (for Render deployment)
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")  # For webhook mode if needed

# File Configuration
TEMP_DIR = "temp_downloads"
MAX_FILE_SIZE = 2000 * 1024 * 1024  # 2GB max file size

# Session Configuration
SESSION_STRING_BOT = "extractor_bot_session"

# Admin Configuration
ADMIN_IDS = [OWNER_ID]

# Premium Plans Configuration
PREMIUM_PLANS = {
    "basic": {
        "price": 99,
        "duration": 30,  # days
        "max_batch": 1000,
        "features": ["Fast extraction", "Custom captions", "Bulk download"]
    },
    "pro": {
        "price": 199,
        "duration": 30,
        "max_batch": 5000,
        "features": ["All Basic features", "Watermarks", "Priority support", "Transferable"]
    },
    "premium": {
        "price": 499,
        "duration": 30,
        "max_batch": 10000,
        "features": ["All Pro features", "Unlimited transfers", "Custom branding", "API access"]
    }
}

# Messages
WELCOME_MESSAGE = """
🌟 **Welcome to Advanced Content Extractor Bot!**

I can extract content from any Telegram channel/group:
✅ Public & Private channels
✅ Bulk extraction with progress tracking  
✅ Custom captions & renaming
✅ Direct upload to your channel
✅ Video & Audio downloads

**Quick Start:**
📱 For Private channels: `/login`
📦 Bulk extraction: `/batch`  
⚙️ Configure settings: `/settings`
💎 Check plans: `/plan`

**Made with ❤️ by RATNA**
"""

START_BUTTON_TEXT = "🚀 Get Started"
