"""
Main application file - Integrates bot with Flask for Render deployment
"""

import asyncio
import logging
from threading import Thread
from datetime import datetime
from flask import Flask
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
import config
from database import db
from bot_handlers import *
from admin_handlers import *

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app for keeping bot alive on Render
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>Extractor Bot - Running</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .container {
                text-align: center;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 50px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            h1 {
                color: white;
                font-size: 3em;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .status {
                color: #4ade80;
                font-size: 1.5em;
                margin: 20px 0;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .info {
                color: white;
                font-size: 1.1em;
                margin: 15px 0;
            }
            .badge {
                display: inline-block;
                background: rgba(255, 255, 255, 0.2);
                padding: 10px 20px;
                border-radius: 25px;
                margin: 10px 5px;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Extractor Bot</h1>
            <div class="status">🟢 Bot is Running</div>
            <div class="info">Advanced Telegram Content Extraction Bot</div>
            <div class="info">
                <span class="badge">⚡ Fast Extraction</span>
                <span class="badge">🔒 Secure</span>
                <span class="badge">💎 Premium Features</span>
            </div>
            <div class="info" style="margin-top: 30px; font-size: 0.9em; opacity: 0.8;">
                Powered by RATNA ❤️
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "bot": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.route('/ping')
def ping():
    """Simple ping endpoint for UptimeRobot"""
    return "pong"

def run_flask():
    """Run Flask app in a separate thread"""
    app.run(host='0.0.0.0', port=config.PORT, debug=False, use_reloader=False)

# ===== CALLBACK QUERY HANDLERS =====
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "help":
        await help_command(update, context)
    elif data == "plans":
        await plans_command(update, context)
    elif data == "settings":
        await settings_command(update, context)
    elif data == "mystats":
        await my_plan_command(update, context)
    elif data == "buypremium":
        await buy_premium_command(update, context)
    
    # Settings callbacks
    elif data.startswith("setting_"):
        setting = data.replace("setting_", "")
        
        if setting == "reset":
            user_id = update.effective_user.id
            await db.reset_settings(user_id)
            await query.message.reply_text("✅ Settings reset to default!")
        
        elif setting == "logout":
            user_id = update.effective_user.id
            await db.delete_session(user_id)
            await extractor.cleanup_user_client(user_id)
            await query.message.reply_text("✅ Logged out successfully!")
        
        elif setting == "chatid":
            await query.message.reply_text(
                "📤 **Set Upload Destination**\n\n"
                "Send the chat ID where you want files to be uploaded.\n"
                "Format: `-100XXXXXXXXXX`\n\n"
                "To upload to a channel, add bot as admin.\n"
                "Send /cancel to abort.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif setting == "rename":
            await query.message.reply_text(
                "✏️ **Set Rename Format**\n\n"
                "Available variables:\n"
                "• `{index}` - File number\n"
                "• `{name}` - Original name\n"
                "• `{ext}` - File extension\n\n"
                "Example: `Video_{index}.{ext}`\n"
                "Send /cancel to abort.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif setting == "caption":
            await query.message.reply_text(
                "💬 **Set Custom Caption**\n\n"
                "Available variables:\n"
                "• `{filename}` - File name\n"
                "• `{size}` - File size\n"
                "• `{index}` - File number\n\n"
                "Example:\n"
                "`📁 File: {filename}`\n"
                "`💾 Size: {size}`\n\n"
                "Send /cancel to abort.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif setting == "report":
            await query.message.reply_text(
                "⚠️ **Report an Error**\n\n"
                "Please describe the error you encountered.\n"
                "Our team will review it.\n\n"
                "Send /cancel to abort."
            )
        
        else:
            await query.message.reply_text(
                f"⚙️ Setting: {setting}\n\n"
                "This feature is under development. Stay tuned!",
                parse_mode=ParseMode.MARKDOWN
            )

# ===== SESSION GENERATOR =====
async def session_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate Pyrogram session string"""
    msg = """🔑 **Pyrogram Session Generator**

This will help you generate a session string for advanced usage.

⚠️ **Warning:**
• Never share your session string with anyone
• Keep it secure like a password
• Session string has full access to your account

Use /login instead for normal bot usage.

To generate session, use /login command.
"""
    
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

# ===== DOWNLOAD COMMANDS =====
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download video from message link"""
    if not context.args:
        await update.message.reply_text(
            "Usage: `/dl <message_link>`\n\n"
            "Example:\n"
            "`/dl https://t.me/channel/123`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    link = context.args[0]
    user_id = update.effective_user.id
    
    msg = await update.message.reply_text("⬇️ Preparing download...")
    
    async def progress_callback(text, current=0, total=0):
        try:
            await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
        except:
            pass
    
    file_path = await extractor.download_media(user_id, link, progress_callback, 'video')
    
    if file_path:
        await update.message.reply_text("✅ Download complete! Uploading...")
        try:
            await update.message.reply_video(video=open(file_path, 'rb'))
            import os
            os.remove(file_path)
        except Exception as e:
            await update.message.reply_text(f"❌ Upload failed: {str(e)}")

async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download audio from message link"""
    if not context.args:
        await update.message.reply_text(
            "Usage: `/adl <message_link>`\n\n"
            "Example:\n"
            "`/adl https://t.me/channel/123`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    link = context.args[0]
    user_id = update.effective_user.id
    
    msg = await update.message.reply_text("⬇️ Preparing download...")
    
    async def progress_callback(text, current=0, total=0):
        try:
            await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
        except:
            pass
    
    file_path = await extractor.download_media(user_id, link, progress_callback, 'audio')
    
    if file_path:
        await update.message.reply_text("✅ Download complete! Uploading...")
        try:
            await update.message.reply_audio(audio=open(file_path, 'rb'))
            import os
            os.remove(file_path)
        except Exception as e:
            await update.message.reply_text(f"❌ Upload failed: {str(e)}")

def main():
    """Main function to run the bot"""
    logger.info("🚀 Starting Extractor Bot...")
    
    # Start Flask in background thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info(f"✅ Flask server started on port {config.PORT}")
    
    # Create bot application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Initialize database
    async def init():
        await db.init_db()
        logger.info("✅ Database initialized")
    
    asyncio.get_event_loop().run_until_complete(init())
    
    # Login conversation handler
    login_conv = ConversationHandler(
        entry_points=[CommandHandler("login", login_start)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_handler)],
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, code_handler)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    
    # Batch conversation handler
    batch_conv = ConversationHandler(
        entry_points=[CommandHandler("batch", batch_start)],
        states={
            BATCH_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, batch_link_handler)],
            BATCH_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, batch_count_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(login_conv)
    application.add_handler(batch_conv)
    application.add_handler(CommandHandler("logout", logout))
    application.add_handler(CommandHandler("session", session_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # Download handlers
    application.add_handler(CommandHandler("dl", download_video))
    application.add_handler(CommandHandler("adl", download_audio))
    
    # Admin handlers
    application.add_handler(CommandHandler("add", add_premium_command))
    application.add_handler(CommandHandler("rem", remove_premium_command))
    application.add_handler(CommandHandler("get", get_users_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Premium handlers
    application.add_handler(CommandHandler("transfer", transfer_premium))
    application.add_handler(CommandHandler("myplan", my_plan_command))
    application.add_handler(CommandHandler("plan", plans_command))
    application.add_handler(CommandHandler("buypremium", buy_premium_command))
    application.add_handler(CommandHandler("paymenthelp", payment_help))
    
    # Settings and other
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("speedtest", speedtest_command))
    application.add_handler(CommandHandler("terms", terms_command))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    logger.info("✅ Bot started successfully!")
    logger.info("🌐 Keep-alive URL for UptimeRobot: https://your-app.onrender.com/ping")
    logger.info("📊 Health check: https://your-app.onrender.com/health")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
