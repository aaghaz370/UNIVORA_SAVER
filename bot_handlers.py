import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from telegram.constants import ParseMode
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired
import config
from database import db
from extractor import extractor
from utils import (
    parse_telegram_link,
    is_owner,
    check_user_limit,
    create_batch_progress_message
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
PHONE, CODE, PASSWORD, BATCH_LINK, BATCH_COUNT = range(5)

# User session data
user_sessions = {}

# ===== START & HELP COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    await db.add_user(user.id, user.username, user.first_name)
    await db.update_user_activity(user.id)
    
    keyboard = [
        [InlineKeyboardButton("📖 Help", callback_data="help"),
         InlineKeyboardButton("💎 Premium Plans", callback_data="plans")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
         InlineKeyboardButton("📊 My Stats", callback_data="mystats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        config.WELCOME_MESSAGE,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📝 **Bot Commands:**

**Authentication:**
🔐 `/login` - Login for private channel access
🚪 `/logout` - Logout and clear session
🔑 `/session` - Generate Pyrogram session string

**Extraction:**
📦 `/batch` - Bulk extract messages from channel
❌ `/cancel` - Cancel ongoing extraction

**Downloads:**
📥 `/dl [link]` - Download video from message
🎵 `/adl [link]` - Download audio from message

**Settings:**
⚙️ `/settings` - Configure bot settings
  • SETCHATID - Set upload destination
  • SETRENAME - Custom rename format
  • CAPTION - Custom caption template
  • RESET - Reset to default

**Premium:**
💎 `/plan` - View premium plans
💳 `/buypremium` - Purchase premium
📊 `/myplan` - Check your plan details

**Admin Only:**
👤 `/add [userID]` - Add premium to user
🗑️ `/rem [userID]` - Remove premium
📋 `/get` - Get all user list
📊 `/stats` - Bot statistics

**Other:**
🔄 `/transfer [userID]` - Transfer your premium
⚡ `/speedtest` - Server speed test
📜 `/terms` - Terms & Conditions

**Powered by RATNA**
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

# ===== LOGIN HANDLER =====
async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start login process"""
    await update.message.reply_text(
        "🔐 **Login to Telegram**\n\n"
        "Please send your phone number with country code.\n"
        "Example: +919876543210\n\n"
        "Send /cancel to abort.",
        parse_mode=ParseMode.MARKDOWN
    )
    return PHONE

async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number"""
    phone = update.message.text.strip()
    user_id = update.effective_user.id
    
    if not phone.startswith('+'):
        await update.message.reply_text("❌ Phone number must start with + and country code")
        return PHONE
    
    logger.info(f"Login attempt for user {user_id} with phone {phone[:5]}****")
    
    # Check if we already have an active session/client for this user
    client = None
    if user_id in user_sessions:
        logger.info(f"Found existing session for user {user_id}")
        existing_session = user_sessions[user_id]
        if existing_session.get('phone') == phone:
            # Reuse existing client if phone matches
            client = existing_session['client']
            if not client.is_connected:
                await client.connect()
        else:
            # Different phone, cleanup old session
            try:
                await existing_session['client'].disconnect()
            except:
                pass
            del user_sessions[user_id]
    
    try:
        if not client:
            # Create new client only if needed
            client = Client(
                f"temp_{user_id}",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                in_memory=True
            )
            logger.info(f"Connecting new Pyrogram client for user {user_id}")
            await client.connect()
        
        logger.info(f"Sending code to {phone[:5]}****")
        try:
            sent_code = await client.send_code(phone)
        except Exception as e:
            if "PHONE_CODE_INVALID" in str(e) or "PHONE_CODE_EXPIRED" in str(e):
                logger.info("Resending code...")
                sent_code = await client.resend_code(phone)
            else:
                raise e
        
        logger.info(f"Code sent successfully to user {user_id}, hash: {sent_code.phone_code_hash[:10]}...")
        
        # Store/Update in session
        user_sessions[user_id] = {
            'client': client,
            'phone': phone,
            'phone_code_hash': sent_code.phone_code_hash
        }
        
        await update.message.reply_text(
            "📱 **Verification Code Sent!**\n\n"
            "Please enter the code you received.\n"
            "Send /cancel to abort.",
            parse_mode=ParseMode.MARKDOWN
        )
        return CODE
        
    except Exception as e:
        logger.error(f"Login error for user {user_id}: {type(e).__name__} - {e}")
        await update.message.reply_text(
            f"❌ Error: {type(e).__name__}\n\n"
            "Please check:\n"
            "1. Phone number is correct (+countrycode)\n"
            "2. You have Telegram on this number\n"
            "3. Try again with /login"
        )
        # Cleanup on error
        if user_id in user_sessions:
            try:
                await user_sessions[user_id]['client'].disconnect()
            except:
                pass
            del user_sessions[user_id]
        return ConversationHandler.END


    
async def code_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle verification code"""
    text = update.message.text.strip().replace(" ", "")
    user_id = update.effective_user.id
    
    # Check if session is active
    if user_id not in user_sessions:
        await update.message.reply_text(
            "❌ Session expired or invalid.\n"
            "Please /login again."
        )
        return ConversationHandler.END
    
    # Validation: Check if it looks like a phone number
    if text.startswith('+') or len(text) > 8:
        await update.message.reply_text(
            "⚠️ That looks like a phone number.\n"
            "Please enter the **5-digit verification code** sent to your Telegram app."
        )
        return CODE
        
    session = user_sessions[user_id]
    client = session['client']
    phone = session['phone']
    phone_code_hash = session['phone_code_hash']
    
    logger.info(f"Attempting sign_in for user {user_id} with code {text}")
    
    try:
        # Try to sign in with the code
        try:
            signed_in = await client.sign_in(phone, phone_code_hash, text)
            logger.info(f"Sign in successful for user {user_id}")
        except SessionPasswordNeeded:
            logger.info(f"2FA required for user {user_id}")
            await update.message.reply_text(
                "🔒 **Two-Step Verification Enabled**\n\n"
                "Please send your **Cloud Password** to complete login.",
                parse_mode=ParseMode.MARKDOWN
            )
            return PASSWORD
        
        # Get session string
        session_string = await client.export_session_string()
        logger.info(f"Session string exported for user {user_id}")
        
        # Save to database
        await db.save_session(user_id, session_string, phone)
        logger.info(f"Session saved to database for user {user_id}")
        
        # Disconnect and cleanup
        try:
            await client.disconnect()
        except:
            pass
        
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        await update.message.reply_text(
            "✅ **Login Successful!**\n\n"
            "You have successfully authenticated.\n"
            "Now you can extract from private channels/groups!\n\n"
            "Start extraction: /batch",
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
        
    except PhoneCodeInvalid as e:
        logger.warning(f"Invalid code for user {user_id}: {e}")
        await update.message.reply_text(
            "❌ **Invalid Code**\n\n"
            "Please check the code from Telegram and try again.\n"
            "Send /cancel to abort.",
            parse_mode=ParseMode.MARKDOWN
        )
        # Stay in CODE state to allow retry
        return CODE
        
    except PhoneCodeExpired as e:
        logger.error(f"Expired code for user {user_id}: {e}")
        await update.message.reply_text(
            "❌ **Code Expired**\n\n"
            "The verification code has expired.\n"
            "Please start over with /login"
        )
        try:
            await client.disconnect()
        except:
            pass
        if user_id in user_sessions:
            del user_sessions[user_id]
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Code verification error for user {user_id}: {type(e).__name__} - {e}")
        await update.message.reply_text(
            f"❌ **Error: {type(e).__name__}**\n\n"
            f"Details: {str(e)}\n"
            "Please /login again."
        )
        try:
            await client.disconnect()
        except:
            pass
        if user_id in user_sessions:
            del user_sessions[user_id]
        return ConversationHandler.END

async def password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 2FA password"""
    password = update.message.text
    user_id = update.effective_user.id
    
    # Delete password message for security
    await update.message.delete()
    
    if user_id not in user_sessions:
        await context.bot.send_message(user_id, "❌ Session expired. Please /login again")
        return ConversationHandler.END
    
    session = user_sessions[user_id]
    client = session['client']
    
    try:
        await client.check_password(password)
        
        # Get session string
        session_string = await client.export_session_string()
        
        # Save to database
        await db.save_session(user_id, session_string, session['phone'])
        
        await client.disconnect()
        del user_sessions[user_id]
        
        await context.bot.send_message(
            user_id,
            "✅ **Login Successful!**\n\n"
            "You can now extract from private channels.\n"
            "Use /batch to start extraction.",
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Password error: {e}")
        await context.bot.send_message(user_id, f"❌ Wrong password or error: {str(e)}")
        if user_id in user_sessions:
            await user_sessions[user_id]['client'].disconnect()
            del user_sessions[user_id]
        return ConversationHandler.END

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logout"""
    user_id = update.effective_user.id
    
    await db.delete_session(user_id)
    await extractor.cleanup_user_client(user_id)
    
    await update.message.reply_text("✅ Logged out successfully!")

# ===== BATCH EXTRACTION =====
async def batch_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start batch extraction"""
    user_id = update.effective_user.id
    
    # Check if session exists
    session = await db.get_session(user_id)
    if not session:
        await update.message.reply_text(
            "❌ Please login first using /login to extract from private channels.\n"
            "For public channels, you can extract without login."
        )
    
    await update.message.reply_text(
        "📎 **Batch Extraction**\n\n"
        "Please send the start link.\n"
        "Example: https://t.me/c/2342349151/1200\n\n"
        "Maximum tries: 3\n"
        "Send /cancel to abort.",
        parse_mode=ParseMode.MARKDOWN
    )
    context.user_data['batch_tries'] = 0
    return BATCH_LINK

async def batch_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle batch link"""
    link = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Parse link
    parsed = parse_telegram_link(link)
    if not parsed:
        context.user_data['batch_tries'] = context.user_data.get('batch_tries', 0) + 1
        if context.user_data['batch_tries'] >= 3:
            await update.message.reply_text("❌ Maximum tries exceeded. Please start again with /batch")
            return ConversationHandler.END
        
        await update.message.reply_text(
            f"❌ Invalid link. Please try again.\n"
            f"Tries left: {3 - context.user_data['batch_tries']}"
        )
        return BATCH_LINK
    
    chat_id, message_id, chat_type = parsed
    context.user_data['batch_chat_id'] = chat_id
    context.user_data['batch_start_msg'] = message_id
    context.user_data['batch_chat_type'] = chat_type
    
    # Get user limits
    is_premium = await db.check_premium(user_id)
    max_limit = await check_user_limit(user_id, is_premium)
    
    await update.message.reply_text(
        f"✅ Link verified!\n\n"
        f"How many messages do you want to process?\n"
        f"Max limit: **{max_limit}**",
        parse_mode=ParseMode.MARKDOWN
    )
    return BATCH_COUNT

async def batch_count_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle batch count and start extraction"""
    try:
        count = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Please send a valid number")
        return BATCH_COUNT
    
    user_id = update.effective_user.id
    is_premium = await db.check_premium(user_id)
    max_limit = await check_user_limit(user_id, is_premium)
    
    if count > max_limit:
        await update.message.reply_text(
            f"❌ Limit exceeded! Your max limit is {max_limit}.\n"
            f"Upgrade to premium for higher limits: /plan"
        )
        return BATCH_COUNT
    
    if count <= 0:
        await update.message.reply_text("❌ Count must be greater than 0")
        return BATCH_COUNT
    
    # Start extraction
    chat_id = context.user_data['batch_chat_id']
    start_msg = context.user_data['batch_start_msg']
    
    # Send initial progress message
    progress_msg = await update.message.reply_text(
        create_batch_progress_message(0, count),
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Progress callback
    async def progress_callback(message, job_id=None, current=0, total=0, complete=False):
        try:
            if complete:
                await progress_msg.edit_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await progress_msg.edit_text(
                    create_batch_progress_message(current, total),
                    parse_mode=ParseMode.MARKDOWN
                )
        except Exception as e:
            logger.error(f"Progress update error: {e}")
    
    # Get user settings
    settings = await db.get_settings(user_id)
    
    # Start extraction in background
    asyncio.create_task(
        extractor.extract_messages(
            user_id, chat_id, start_msg, count,
            progress_callback, None, settings
        )
    )
    
    return ConversationHandler.END

# ===== CANCEL COMMAND =====
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel ongoing operation"""
    user_id = update.effective_user.id
    
    # Cancel extraction
    await extractor.cancel_extraction(user_id)
    
    # Clear conversation data
    context.user_data.clear()
    
    # Cleanup session if exists
    if user_id in user_sessions:
        try:
            await user_sessions[user_id]['client'].disconnect()
        except:
            pass
        del user_sessions[user_id]
    
    await update.message.reply_text("✅ Operation cancelled")
    return ConversationHandler.END

# To be continued in next file...
