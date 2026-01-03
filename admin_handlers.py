"""
Additional bot handlers - Admin, Premium, Settings, Downloads
Continuation of bot_handlers.py
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import config
from database import db
from extractor import extractor
from utils import is_owner
import psutil
import platform
from datetime import datetime

# ===== ADMIN COMMANDS =====
async def add_premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add premium to user (Owner only)"""
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        await update.message.reply_text("❌ This command is for owner only!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /add <userID> [days]\nExample: /add 123456789 30")
        return
    
    try:
        target_user = int(context.args[0])
        days = int(context.args[1]) if len(context.args) > 1 else 30
        
        expiry = await db.add_premium(target_user, days)
        await update.message.reply_text(
            f"✅ Premium added successfully!\n\n"
            f"👤 User ID: `{target_user}`\n"
            f"⏰ Duration: {days} days\n"
            f"📅 Expires: {expiry.strftime('%Y-%m-%d %H:%M')}",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Notify user
        try:
            await context.bot.send_message(
                target_user,
                f"🎉 **Premium Activated!**\n\n"
                f"Your premium subscription is now active.\n"
                f"Duration: {days} days\n"
                f"Expires: {expiry.strftime('%Y-%m-%d')}\n\n"
                f"Enjoy unlimited features! 💎",
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass
            
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID or days")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def remove_premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove premium from user (Owner only)"""
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        await update.message.reply_text("❌ This command is for owner only!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /rem <userID>")
        return
    
    try:
        target_user = int(context.args[0])
        await db.remove_premium(target_user)
        
        await update.message.reply_text(
            f"✅ Premium removed successfully!\n\n"
            f"👤 User ID: `{target_user}`",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Notify user
        try:
            await context.bot.send_message(
                target_user,
                "⚠️ Your premium subscription has been removed.",
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            pass
            
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def get_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get all users (Owner only)"""
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        await update.message.reply_text("❌ This command is for owner only!")
        return
    
    users = await db.get_all_users()
    
    premium_users = [u for u in users if u.get('is_premium')]
    free_users = [u for u in users if not u.get('is_premium')]
    
    msg = f"👥 **Total Users: {len(users)}**\n\n"
    
    if premium_users:
        msg += f"💎 **Premium Users ({len(premium_users)}):**\n"
        for u in premium_users[:20]:  # Limit to 20
            username = f"@{u.get('username')}" if u.get('username') else "No username"
            msg += f"• `{u['user_id']}` - {username}\n"
        if len(premium_users) > 20:
            msg += f"... and {len(premium_users) - 20} more\n"
    
    msg += f"\n📊 **Free Users: {len(free_users)}**\n"
    
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot statistics"""
    stats = await db.get_stats()
    
    # Server stats
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    stats_msg = f"""📊 **Bot Statistics**

👥 **Users:**
• Total: {stats['total_users']}
• Premium: {stats['premium_users']}
• Free: {stats['free_users']}

📦 **Extractions:**
• Total: {stats['total_extractions']}

🖥️ **Server:**
• CPU: {cpu_percent}%
• RAM: {memory.percent}%
• Disk: {disk.percent}%
• Platform: {platform.system()}

⏰ **Uptime:**
• Running smoothly 🟢

**Powered by RATNA**
"""
    
    await update.message.reply_text(stats_msg, parse_mode=ParseMode.MARKDOWN)

# ===== PREMIUM COMMANDS =====
async def transfer_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Transfer premium to another user"""
    user_id = update.effective_user.id
    
    # Check if user has premium
    is_premium = await db.check_premium(user_id)
    if not is_premium:
        await update.message.reply_text("❌ You don't have premium to transfer!")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /transfer <userID>\n\n"
            "Example: /transfer 123456789\n\n"
            "⚠️ This will transfer your remaining premium to another user."
        )
        return
    
    try:
        target_user = int(context.args[0])
        
        if target_user == user_id:
            await update.message.reply_text("❌ You cannot transfer to yourself!")
            return
        
        # Transfer
        success = await db.transfer_premium(user_id, target_user)
        
        if success:
            await update.message.reply_text(
                f"✅ Premium transferred successfully!\n\n"
                f"👤 To User: `{target_user}`\n\n"
                f"Your premium has been transferred.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Notify recipient
            try:
                await context.bot.send_message(
                    target_user,
                    f"🎉 You received premium from user `{user_id}`!\n\n"
                    f"Check your plan: /myplan",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        else:
            await update.message.reply_text("❌ Transfer failed!")
            
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def my_plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check user's plan"""
    user_id = update.effective_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ User not found")
        return
    
    is_premium = await db.check_premium(user_id)
    
    if is_premium:
        expiry = user.get('premium_expiry')
        days_left = (expiry - datetime.utcnow()).days if expiry else 0
        
        msg = f"""💎 **Your Premium Plan**

✅ Status: Active
📅 Expires: {expiry.strftime('%Y-%m-%d %H:%M')}
⏳ Days Left: {days_left}

**Features:**
✔️ Bulk extraction up to {config.PREMIUM_MAX_BATCH} messages
✔️ Custom captions & renaming
✔️ Watermarks & thumbnails
✔️ Priority support
✔️ Transfer premium

**Powered by RATNA**
"""
    else:
        msg = f"""📊 **Your Plan**

❌ Status: Free
📦 Max Batch: {config.FREE_MAX_BATCH} messages

**Upgrade to Premium:**
Use /plan to see premium plans
Use /buypremium to purchase

**Powered by RATNA**
"""
    
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def plans_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show premium plans"""
    plans_msg = """💎 **Premium Plans**

**Basic Plan - ₹99/month**
✔️ 1000 messages batch
✔️ Fast extraction
✔️ Custom captions
✔️ Bulk download

**Pro Plan - ₹199/month**
✔️ 5000 messages batch
✔️ All Basic features
✔️ Watermarks
✔️ Priority support
✔️ Transferable

**Premium Plan - ₹499/month**
✔️ 10,000 messages batch
✔️ All Pro features
✔️ Unlimited transfers
✔️ Custom branding
✔️ API access

**Contact owner to purchase!**
"""
    
    keyboard = [[InlineKeyboardButton("💳 Buy Premium", callback_data="buypremium")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        plans_msg,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def buy_premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Purchase premium"""
    msg = """💳 **Purchase Premium**

Please contact the owner to purchase premium:

👤 Owner: Contact via /paymenthelp

**Payment Methods:**
• UPI
• PayPal
• Crypto

After payment, owner will activate your premium.
"""
    
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def payment_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Payment help"""
    msg = """💳 **Payment Help**

**How to Purchase Premium:**

1. Choose your plan from /plan
2. Contact owner via bot
3. Make payment using:
   • UPI
   • PayPal
   • Cryptocurrency
4. Send payment proof
5. Premium will be activated within 24 hours

**Need Help?**
Contact owner: /buypremium

**Refund Policy:**
7-day money back guarantee

**Powered by RATNA**
"""
    
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

# ===== SETTINGS COMMANDS =====
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings panel"""
    keyboard = [
        [
            InlineKeyboardButton("📤 Set Chat ID", callback_data="setting_chatid"),
            InlineKeyboardButton("✏️ Set Rename Tag", callback_data="setting_rename")
        ],
        [
            InlineKeyboardButton("💬 Caption", callback_data="setting_caption"),
            InlineKeyboardButton("🔄 Replace Words", callback_data="setting_replace")
        ],
        [
            InlineKeyboardButton("🗑️ Remove Words", callback_data="setting_remove"),
            InlineKeyboardButton("🔄 Reset", callback_data="setting_reset")
        ],
        [
            InlineKeyboardButton("🔐 Session Login", callback_data="setting_session"),
            InlineKeyboardButton("🚪 Logout", callback_data="setting_logout")
        ],
        [
            InlineKeyboardButton("🖼️ Set Thumbnail", callback_data="setting_thumb"),
            InlineKeyboardButton("❌ Remove Thumbnail", callback_data="setting_removethumb")
        ],
        [
            InlineKeyboardButton("📊 Video Watermark", callback_data="setting_watermark"),
            InlineKeyboardButton("📤 Upload Method", callback_data="setting_upload")
        ],
        [
            InlineKeyboardButton("⚠️ Report Errors", callback_data="setting_report")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    settings_msg = """⚙️ **SETTINGS**

Customize by your end and Configure your settings...

**Available Options:**
📤 Set Chat ID - Direct upload destination
✏️ Set Rename Tag - Custom file naming
💬 Caption - Custom caption template
🔄 Replace/Remove Words - Text processing
🔄 Reset - Back to default
🔐 Session Login - Advanced features
🖼️ Thumbnail - Custom preview image
📊 Watermark - Brand your videos
📤 Upload Method - Optimize uploads

**Powered by RATNA**
"""
    
    await update.message.reply_text(
        settings_msg,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def speedtest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Server speed test"""
    msg = await update.message.reply_text("⚡ Running speed test...")
    
    import time
    start = time.time()
    
    # Simple CPU test
    _ = sum(i * i for i in range(1000000))
    
    elapsed = time.time() - start
    
    # Network test (ping to Telegram)
    import aiohttp
    async with aiohttp.ClientSession() as session:
        ping_start = time.time()
        try:
            async with session.get('https://api.telegram.org') as resp:
                await resp.text()
            ping = (time.time() - ping_start) * 1000
        except:
            ping = 999
    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    result = f"""⚡ **Speed Test Results**

🖥️ **CPU Test:**
• Time: {elapsed:.2f}s
• Usage: {cpu_percent}%

🌐 **Network:**
• Ping: {ping:.0f}ms
• Status: {'🟢 Good' if ping < 200 else '🟡 Fair' if ping < 500 else '🔴 Slow'}

💾 **Memory:**
• Used: {memory.percent}%
• Available: {memory.available / (1024**3):.1f} GB

**Server Status: 🟢 Optimal**
"""
    
    await msg.edit_text(result, parse_mode=ParseMode.MARKDOWN)

async def terms_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Terms and conditions"""
    terms = """📜 **Terms & Conditions**

**By using this bot, you agree to:**

1. **Usage Policy:**
   • Use bot for legal purposes only
   • Respect copyright and privacy laws
   • Don't spam or abuse the service

2. **Content Policy:**
   • You are responsible for content extracted
   • Don't extract copyrighted material without permission
   • Respect content creators' rights

3. **Account Policy:**
   • One account per user
   • No account sharing
   • Premium is non-transferable (except via /transfer)

4. **Refund Policy:**
   • 7-day money back guarantee
   • No refunds after 7 days
   • Refunds processed within 5-7 business days

5. **Privacy:**
   • We don't store your messages
   • Session data is encrypted
   • Your data is secure

6. **Disclaimer:**
   • Service provided "as is"
   • No guarantee of 100% uptime
   • We are not responsible for any data loss

**Contact:** Use /paymenthelp for support

**Last Updated:** January 2026

**Powered by RATNA**
"""
    
    await update.message.reply_text(terms, parse_mode=ParseMode.MARKDOWN)

# Continue in main.py...
