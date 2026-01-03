# 🚀 Advanced Telegram Content Extractor Bot

An industry-level Telegram bot for extracting and downloading content from any channel or group (public/private) with premium features.

## ✨ Features

### 🔑 Core Features
- **Batch Extraction**: Extract up to 10,000 messages at once (premium)
- **Private Channel Access**: Login with your account to access private channels
- **Progress Tracking**: Real-time progress updates with beautiful UI
- **Custom Settings**: Rename files, add captions, set thumbnails, and more
- **Direct Upload**: Upload extracted content directly to your channel/group
- **Session Management**: Secure Pyrogram session handling

### 💎 Premium Features
- Higher batch limits (1000-10,000 messages)
- Custom captions and file renaming
- Video watermarks
- Custom thumbnails
- Transfer premium to others
- Priority support

### 👤 Admin Features
- Add/remove premium users
- View all users
- Bot statistics
- Manage premium plans

## 📋 Commands

### For Everyone
- `/start` - Start the bot
- `/help` - Show all commands
- `/login` - Login for private channel access
- `/logout` - Logout and clear session
- `/batch` - Start bulk extraction
- `/cancel` - Cancel ongoing process
- `/dl <link>` - Download video from message
- `/adl <link>` - Download audio from message
- `/settings` - Configure bot settings
- `/plan` - View premium plans
- `/myplan` - Check your plan
- `/buypremium` - Purchase premium
- `/stats` - Bot statistics
- `/speedtest` - Server speed test
- `/terms` - Terms and conditions

### Premium Users
- `/transfer <userID>` - Transfer premium to another user

### Admin Only
- `/add <userID> [days]` - Add premium to user
- `/rem <userID>` - Remove premium from user
- `/get` - Get all users list

## ⚙️ Settings Options

Access via `/settings`:

1. **Set Chat ID** - Direct upload destination
2. **Set Rename Tag** - Custom file naming format
3. **Caption** - Custom caption template
4. **Replace Words** - Text processing
5. **Remove Words** - Remove specific words
6. **Reset** - Reset to default settings
7. **Session Login** - Advanced session management
8. **Set Thumbnail** - Custom preview image
9. **Video Watermark** - Add branding to videos
10. **Upload Method** - Optimize upload settings

## 🚀 Quick Start

### Requirements
- Python 3.8+
- Telegram Bot Token
- Telegram API ID & Hash
- MongoDB Database

### Installation

1. Clone repository:
```bash
git clone <your-repo>
cd EXTRACTOR_BOT
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
- Copy `.env.example` to `.env`
- Fill in your credentials

4. Run locally:
```bash
python main.py
```

## 🌐 Deployment

### Render (Free 24/7)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

**Quick Steps:**
1. Create Render account
2. Create new Web Service
3. Connect repository
4. Add environment variables
5. Deploy!
6. Setup UptimeRobot for 24/7 uptime

### Files Structure
```
EXTRACTOR_BOT/
├── main.py              # Main application
├── config.py            # Configuration
├── database.py          # MongoDB handler
├── extractor.py         # Content extraction logic
├── bot_handlers.py      # Bot command handlers
├── admin_handlers.py    # Admin commands
├── utils.py             # Utility functions
├── requirements.txt     # Dependencies
├── .env                 # Environment variables
├── start.sh             # Start script for deployment
└── DEPLOYMENT.md        # Deployment guide
```

## 🔧 Configuration

### Environment Variables

```env
BOT_TOKEN=your_bot_token
API_ID=your_api_id
API_HASH=your_api_hash
MONGO_URI=your_mongodb_uri
OWNER_ID=your_telegram_id
PORT=10000
```

### Get Telegram API Credentials
1. Go to https://my.telegram.org
2. Login with your phone number
3. Go to "API Development Tools"
4. Create new application
5. Copy API ID and API Hash

### Get Bot Token
1. Open Telegram
2. Search for @BotFather
3. Send `/newbot`
4. Follow instructions
5. Copy the token

## 💡 Usage Examples

### Extract from Public Channel
```
1. Send /batch
2. Send channel link: https://t.me/channel/123
3. Enter number of messages: 10
4. Wait for extraction to complete
```

### Extract from Private Channel
```
1. Send /login
2. Enter your phone number: +919876543210
3. Enter verification code
4. Now use /batch as above
```

### Download Video
```
/dl https://t.me/channel/123
```

### Custom Settings
```
1. Send /settings
2. Click "Set Rename Tag"
3. Send format: Video_{index}.{ext}
4. Files will be renamed accordingly
```

## 📊 Database Schema

### Users Collection
- user_id, username, first_name
- is_premium, premium_expiry
- total_extractions, total_downloads
- joined_date, last_active

### Sessions Collection
- user_id, session_string, phone
- created_at

### Settings Collection
- user_id, chat_id, custom_caption
- rename_format, thumbnail, watermark
- replace_words

### Extraction Jobs Collection
- user_id, job_type, total_messages
- processed, status
- created_at, updated_at

## 🛡️ Security

- Session strings are encrypted
- Pyrogram sessions stored securely
- No message content stored
- User data is private
- 2FA password handled securely (deleted immediately)

## 📈 Performance

- Async operations for speed
- Efficient database queries
- Minimal storage usage (streaming)
- Real-time progress updates
- Handles FloodWait automatically

## 🐛 Troubleshooting

**Bot not responding:**
- Check bot token is correct
- Verify bot is running (`/ping` endpoint)
- Check Render logs

**Can't extract private channels:**
- Use `/login` first
- Ensure you're member of the channel
- Check session is valid

**Database errors:**
- Verify MongoDB URI
- Check network access (whitelist 0.0.0.0/0)
- Ensure database exists

**Download issues:**
- Check file size limits
- Verify sufficient storage
- Check network connection

## 📝 Development

### Adding New Features
1. Create handler in appropriate file
2. Register handler in `main.py`
3. Update database schema if needed
4. Test thoroughly
5. Deploy

### Code Style
- Use async/await for I/O operations
- Follow PEP 8 guidelines
- Add type hints
- Comment complex logic
- Handle exceptions properly

## 📜 License

This project is for educational purposes only. Use responsibly and respect Telegram's Terms of Service.

## 🙏 Credits

- **Pyrogram** - MTProto API framework
- **python-telegram-bot** - Bot framework
- **MongoDB** - Database
- **Render** - Hosting platform

## 📧 Support

For issues and questions:
- Create GitHub issue
- Contact via bot: `/paymenthelp`
- Check documentation

## 🌟 Premium Plans

| Plan | Price | Batch Limit | Features |
|------|-------|-------------|----------|
| Free | ₹0 | 3 messages | Basic extraction |
| Basic | ₹99/mo | 1,000 messages | Custom captions, Fast extraction |
| Pro | ₹199/mo | 5,000 messages | + Watermarks, Priority support, Transferable |
| Premium | ₹499/mo | 10,000 messages | + Custom branding, API access, Unlimited transfers |

## 🔄 Updates

**Version 1.0.0** (Current)
- Initial release
- Batch extraction
- Login/logout system
- Premium features
- Settings panel
- Admin commands

## 🎯 Roadmap

- [ ] Video watermark implementation
- [ ] Custom thumbnail support
- [ ] Scheduled extractions
- [ ] API access for premium users
- [ ] Multi-language support
- [ ] Advanced analytics

---

**Made with ❤️ by RATNA**

*Last updated: January 2026*
