# 🧪 Testing Guide

## Local Testing

### 1. Prerequisites Check
```bash
python --version  # Should be 3.8+
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Edit `.env` file (if gitignore blocks, create new one):
```env
BOT_TOKEN=8513397474:AAFuSpGil8u0jFObL41NbmLGdHI7pE3Q-4k
API_ID=20598098
API_HASH=c1727e40f8585b869cef73b828b2bf69
MONGO_URI=mongodb+srv://UNIVORA_SAVER:aaghaz9431@univorasaver.6st7ygj.mongodb.net/?appName=UNIVORASAVER
OWNER_ID=0  # Replace with your Telegram user ID
PORT=10000
```

**Get your Telegram User ID:**
- Open Telegram
- Search for @userinfobot
- Start bot and get your ID
- Replace `0` with your ID in .env

### 4. Run Setup Script
```bash
python setup_and_run.py
```

OR run directly:
```bash
python main.py
```

### 5. Test Bot Commands

Open Telegram and find your bot, then test:

#### Basic Commands
```
/start - Should show welcome message
/help - Should show all commands
/stats - Should show bot statistics
```

#### Login Flow
```
/login
> Send your phone: +919876543210
> Enter code from Telegram
> (If 2FA) Enter password
✅ Login successful
```

#### Batch Extraction (Public Channel)
```
/batch
> Send link: https://t.me/channel/message_id
> Enter count: 3
✅ Should start extracting
```

#### Settings
```
/settings
> Click any button to configure
```

## Testing Checklist

### ✅ Core Functions
- [ ] `/start` shows welcome
- [ ] `/help` shows commands
- [ ] `/stats` shows statistics
- [ ] Bot responds to commands

### ✅ Authentication
- [ ] `/login` accepts phone number
- [ ] Receives and accepts verification code
- [ ] Handles 2FA password correctly
- [ ] `/logout` clears session

### ✅ Extraction
- [ ] `/batch` accepts Telegram links
- [ ] Validates message count limits
- [ ] Shows progress updates
- [ ] Completes extraction
- [ ] `/cancel` stops extraction

### ✅ Admin Commands (Only if you're owner)
- [ ] `/add` adds premium to user
- [ ] `/rem` removes premium
- [ ] `/get` lists all users

### ✅ Premium Features
- [ ] `/plan` shows plans
- [ ] `/myplan` shows user plan
- [ ] `/transfer` transfers premium

### ✅ Settings
- [ ] `/settings` shows panel
- [ ] All buttons work
- [ ] Settings are saved

### ✅ Web Server
- [ ] Open http://localhost:10000
- [ ] Should show beautiful landing page
- [ ] `/ping` endpoint works
- [ ] `/health` endpoint works

## Common Issues & Fixes

### Issue: "Bot not responding"
**Fix:**
1. Check bot token is correct
2. Verify bot is running (check logs)
3. Restart bot

### Issue: "MongoDB connection failed"
**Fix:**
1. Check MONGO_URI is correct
2. Whitelist all IPs in MongoDB Atlas (0.0.0.0/0)
3. Verify internet connection

### Issue: "Login not working"
**Fix:**
1. Check API_ID and API_HASH
2. Verify phone number format (+country_code)
3. Check for Pyrogram session files and delete old ones

### Issue: "Permission denied for admin commands"
**Fix:**
1. Set your OWNER_ID in .env
2. Restart bot
3. Make sure ID is correct (use @userinfobot)

### Issue: "Can't extract private channel"
**Fix:**
1. Login first with `/login`
2. Make sure you're member of channel
3. Verify session is active

### Issue: "Flask server not starting"
**Fix:**
1. Check PORT is available (default 10000)
2. Try different port in .env
3. Check firewall settings

## Performance Testing

### Test Extraction Speed
1. Start batch extraction with 10 messages
2. Measure time taken
3. Should complete within 1-2 minutes

### Test Concurrent Users
1. Have multiple users use bot simultaneously
2. Check if bot handles all requests
3. Monitor CPU and memory usage

### Test Limits
1. Free user: Try extracting >3 messages (should fail)
2. Add premium: Should allow higher limits
3. Test transfer premium feature

## Deployment Testing

After deploying to Render:

### 1. Check URLs
```
https://your-app.onrender.com - Should show landing page
https://your-app.onrender.com/ping - Should return "pong"
https://your-app.onrender.com/health - Should return JSON
```

### 2. Check Logs
- Go to Render Dashboard
- View Logs
- Should see "Bot started successfully!"

### 3. Test UptimeRobot
- Add monitor with `/ping` URL
- Wait 5 minutes
- Check if bot is being pinged

### 4. Test Bot on Telegram
- All commands should work same as local
- Check extraction works
- Verify settings persist

## Security Testing

### ✅ Session Security
- [ ] Sessions stored encrypted
- [ ] 2FA password deleted immediately
- [ ] No sensitive data in logs

### ✅ User Isolation
- [ ] Users can't access each other's data
- [ ] Admin commands restricted to owner
- [ ] Premium features locked for free users

### ✅ Rate Limiting
- [ ] FloodWait handled automatically
- [ ] No excessive API calls
- [ ] Batch limits enforced

## Load Testing

Test with:
- 100 messages extraction
- Multiple simultaneous extractions
- Large file downloads
- Monitor RAM and CPU usage

## Final Checklist Before Production

- [ ] All tests passed
- [ ] Environment variables secured
- [ ] MongoDB indexes created
- [ ] UptimeRobot configured
- [ ] Logs monitoring setup
- [ ] Backup plan ready
- [ ] Documentation complete
- [ ] README updated
- [ ] .gitignore configured
- [ ] No sensitive data in repo

---

## Test Report Template

```
Test Date: ___________
Tester: ___________

Core Functions: ✅ ❌
Authentication: ✅ ❌
Extraction: ✅ ❌
Admin Commands: ✅ ❌
Web Server: ✅ ❌
Deployment: ✅ ❌

Issues Found:
1. ___________
2. ___________

Performance:
- Extraction Speed: _____ seconds for 10 messages
- Memory Usage: _____ MB
- CPU Usage: _____ %

Status: PASS / FAIL
```

---

**Happy Testing! 🧪**

*Powered by RATNA*
