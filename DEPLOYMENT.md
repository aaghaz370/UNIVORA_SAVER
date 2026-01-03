# Extractor Bot - Render Deployment Configuration

## Environment Variables
Add these in Render dashboard:

```
BOT_TOKEN=8513397474:AAFuSpGil8u0jFObL41NbmLGdHI7pE3Q-4k
API_ID=20598098
API_HASH=c1727e40f8585b869cef73b828b2bf69
MONGO_URI=mongodb+srv://UNIVORA_SAVER:aaghaz9431@univorasaver.6st7ygj.mongodb.net/?appName=UNIVORASAVER
OWNER_ID=YOUR_TELEGRAM_USER_ID
PORT=10000
```

## Deployment Steps

### 1. Create Render Account
- Go to https://render.com
- Sign up or log in

### 2. Create New Web Service
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Or use Manual Deploy

### 3. Configure Service

**Basic Settings:**
- Name: `extractor-bot` (or any name)
- Region: Select closest to you
- Branch: `main`
- Runtime: `Python 3`

**Build Settings:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `bash start.sh`

**Instance Type:**
- Select: `Free` (0$/month)

### 4. Environment Variables
Add all variables from above in the "Environment" section

### 5. Deploy
- Click "Create Web Service"
- Wait for deployment (2-5 minutes)

### 6. Get Your URLs
After deployment, you'll get URLs like:
- Main: `https://extractor-bot-xxxx.onrender.com`
- Ping: `https://extractor-bot-xxxx.onrender.com/ping`
- Health: `https://extractor-bot-xxxx.onrender.com/health`

### 7. Setup UptimeRobot (Keep bot alive 24/7)

1. Go to https://uptimerobot.com
2. Sign up (Free account)
3. Add New Monitor:
   - Monitor Type: `HTTP(s)`
   - Friendly Name: `Extractor Bot`
   - URL: `https://your-app.onrender.com/ping`
   - Monitoring Interval: `5 minutes`
4. Save

**Done!** Your bot will run 24/7 without sleeping.

## Important Notes

⚠️ **Render Free Tier Limitations:**
- Sleeps after 15 minutes of inactivity
- UptimeRobot pings every 5 minutes to keep it awake
- 750 hours/month free (enough for 24/7)

✅ **Advantages:**
- Completely free
- Auto-deploy on git push
- SSL certificates included
- Logs and monitoring

## Monitoring

Check bot status:
- Logs: Render Dashboard → Logs
- Health: Visit `/health` endpoint
- Ping: Visit `/ping` endpoint

## Troubleshooting

**Bot not responding:**
1. Check Render logs for errors
2. Verify environment variables
3. Check UptimeRobot is pinging
4. Restart service from dashboard

**Database connection failed:**
1. Verify MONGO_URI is correct
2. Check MongoDB Atlas whitelist (allow all IPs: 0.0.0.0/0)
3. Check network access in MongoDB

**Session errors:**
1. Run /login command again
2. Check API_ID and API_HASH
3. Clear old sessions

## Support

For issues, check:
- Render docs: https://render.com/docs
- Bot logs in dashboard
- MongoDB Atlas status

**Powered by RATNA** ❤️
