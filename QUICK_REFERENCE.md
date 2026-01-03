# ⚡ QUICK REFERENCE CARD

## 🚀 Instant Start

```bash
# 1. Set your Telegram ID in .env
OWNER_ID=YOUR_ID_HERE

# 2. Run bot
python main.py

# 3. OR use setup script
python setup_and_run.py
```

---

## 📝 Essential Commands

### User Commands
```
/start         - Welcome message
/help          - Command list
/login         - Login to Telegram
/batch         - Bulk extraction
/dl <link>     - Download video
/settings      - Configure bot
/myplan        - Check plan
```

### Admin Commands (Owner Only)
```
/add <id> [days]  - Add premium
/rem <id>         - Remove premium
/get              - List all users
/stats            - Bot statistics
```

---

## 🔧 Configuration

### .env File (Required)
```env
BOT_TOKEN=8513397474:AAFuSpGil8u0jFObL41NbmLGdHI7pE3Q-4k
API_ID=20598098
API_HASH=c1727e40f8585b869cef73b828b2bf69
MONGO_URI=mongodb+srv://UNIVORA_SAVER:aaghaz9431@univorasaver.6st7ygj.mongodb.net/?appName=UNIVORASAVER
OWNER_ID=0  # ⚠️ Set your ID here!
PORT=10000
```

**Get your ID:** @userinfobot on Telegram

---

## 🌐 Deployment URLs

After deploying to Render:
```
Main:    https://your-app.onrender.com
Ping:    https://your-app.onrender.com/ping
Health:  https://your-app.onrender.com/health
```

Use `/ping` URL in UptimeRobot for 24/7 uptime.

---

## 🐛 Quick Fixes

### Bot not responding?
```bash
# Check if running
curl http://localhost:10000/ping

# Restart
Ctrl+C then: python main.py
```

### MongoDB error?
- Whitelist IP: 0.0.0.0/0 in MongoDB Atlas
- Check MONGO_URI is correct

### Can't login?
- Verify API_ID and API_HASH
- Delete old .session files
- Use correct phone format: +91XXXXXXXXXX

---

## 📊 File Structure Quick View

```
EXTRACTOR_BOT/
├── main.py              ← Start here
├── config.py            ← Settings
├── database.py          ← DB operations
├── extractor.py         ← Core engine
├── bot_handlers.py      ← Commands
├── admin_handlers.py    ← Admin commands
├── utils.py             ← Helpers
├── .env                 ← Credentials ⚠️
├── requirements.txt     ← Dependencies
└── [Documentation]      ← Guides
```

---

## 💎 Premium Limits

| Plan | Batch Limit |
|------|-------------|
| Free | 3 messages |
| Basic (₹99) | 1,000 messages |
| Pro (₹199) | 5,000 messages |
| Premium (₹499) | 10,000 messages |

---

## 🔑 Important Links

- **Get Bot Token:** @BotFather
- **Get API Creds:** https://my.telegram.org
- **Get User ID:** @userinfobot
- **MongoDB:** https://cloud.mongodb.com
- **Render:** https://render.com
- **UptimeRobot:** https://uptimerobot.com

---

## ✅ Pre-Flight Checklist

Before deployment:
- [ ] OWNER_ID set in .env
- [ ] All dependencies installed
- [ ] MongoDB accessible
- [ ] Bot token verified
- [ ] Tested locally
- [ ] Read DEPLOYMENT.md
- [ ] GitHub repo ready (if using)

---

## 🎯 Testing Sequence

1. Start bot: `python main.py`
2. Open Telegram bot
3. Send: `/start` → Should reply
4. Send: `/stats` → Should show stats
5. Send: `/batch` → Test extraction
6. All working? ✅ Ready to deploy!

---

## 📱 Telegram Extraction Example

```
You: /batch
Bot: Please send the start link.

You: https://t.me/c/1234567890/100
Bot: Link verified! How many messages?

You: 5
Bot: Batch process started ⚡
     Processing: 5/5
     ✅ Extraction Complete!
```

---

## 🚨 Emergency Commands

```bash
# Force stop bot
Ctrl+C

# Check logs
tail -f logs.txt  # If logging to file

# Check MongoDB
mongo "MONGO_URI"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📞 Quick Support

**Issue:** Bot command not responding
**Fix:** Check logs, restart bot

**Issue:** Extraction stuck
**Fix:** Send `/cancel`, restart extraction

**Issue:** Premium not working
**Fix:** Check expiry with `/myplan`

**Issue:** Settings not saving
**Fix:** Check MongoDB connection

---

## 🎨 Beautiful Features

✅ Real-time progress bars
✅ Glassmorphism UI (web page)
✅ Professional messages
✅ Emoji-rich responses
✅ Settings panel like reference bot
✅ Speed & ETA in downloads

---

## 💡 Pro Tips

1. **Always test locally first**
2. **Keep OWNER_ID secret**
3. **Monitor MongoDB usage**
4. **Check Render logs regularly**
5. **UptimeRobot = 24/7 guarantee**
6. **Backup important data**
7. **Update dependencies monthly**

---

## 🏆 Success Metrics

After deployment, check:
- ✅ Bot responding to all commands
- ✅ Extraction working (public + private)
- ✅ Settings saving properly
- ✅ Premium system functional
- ✅ Web server accessible
- ✅ UptimeRobot pinging
- ✅ No errors in logs

**All green?** 🎉 PRODUCTION READY!

---

**Made with ❤️**
**Powered by RATNA**

*Last updated: January 2026*
