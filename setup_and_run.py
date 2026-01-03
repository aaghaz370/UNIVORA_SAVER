"""
Quick Start Script - Run this to test bot locally
"""

import subprocess
import sys
import os

def main():
    print("""
    ╔════════════════════════════════════════╗
    ║   🚀 EXTRACTOR BOT - LOCAL TEST       ║
    ╚════════════════════════════════════════╝
    """)
    
    # Check Python version
    print("✓ Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required!")
        return
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected\n")
    
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("\n📝 Please create .env file with:")
        print("""
BOT_TOKEN=your_bot_token
API_ID=your_api_id
API_HASH=your_api_hash
MONGO_URI=your_mongodb_uri
OWNER_ID=your_telegram_id
PORT=10000
        """)
        return
    print("✓ .env file found\n")
    
    # Check MongoDB connection
    print("⏳ Checking MongoDB connection...")
    try:
        from pymongo import MongoClient
        import config
        client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✓ MongoDB connected\n")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}\n")
        print("Please check your MONGO_URI in .env file\n")
        return
    
    # Check bot token
    print("⏳ Verifying bot token...")
    try:
        import requests
        response = requests.get(f"https://api.telegram.org/bot{config.BOT_TOKEN}/getMe")
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✓ Bot verified: @{bot_info['result']['username']}\n")
        else:
            print("❌ Invalid bot token!\n")
            return
    except Exception as e:
        print(f"❌ Bot verification failed: {e}\n")
        return
    
    # Install dependencies
    print("⏳ Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
        print("✓ Dependencies installed\n")
    except Exception as e:
        print(f"❌ Installation failed: {e}\n")
        return
    
    print("""
    ╔════════════════════════════════════════╗
    ║   ✅ All checks passed!               ║
    ║   🚀 Starting bot...                  ║
    ╚════════════════════════════════════════╝
    """)
    
    # Start bot
    subprocess.call([sys.executable, "main.py"])

if __name__ == "__main__":
    main()
