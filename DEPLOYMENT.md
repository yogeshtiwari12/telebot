# 🤖 Anonymous Dating Bot - Deployment Guide

A Telegram bot for anonymous dating with premium subscriptions. Users can create profiles and chat anonymously.

## 🚀 Deploy to Render.com

### Step 1: Prepare Files
Your repository needs these files (✅ already included):
- `bot.py` - Main bot code
- `requirements.txt` - Python dependencies  
- `runtime.txt` - Python version (python-3.12.0)
- `Procfile` - Start command (web: python bot.py)

### Step 2: Deploy on Render

1. **Create Render account** at [render.com](https://render.com)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Choose your bot repository

3. **Configure Settings**:
   - **Name**: `dating-bot` (or your choice)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`

4. **Add Environment Variable**:
   - Go to "Environment" tab
   - Add variable:
     - **Key**: `BOT_TOKEN`
     - **Value**: `7750483935:AAENsDFiOYfB41WcjfzEiTZn1m6ah4-LHYs`

5. **Deploy**: Click "Create Web Service"

### Step 3: Monitor Deployment
- Watch the logs for "🤖 Dating Bot is starting..."
- Check for any errors in the deployment logs

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set bot token (Windows)
set BOT_TOKEN=7750483935:AAENsDFiOYfB41WcjfzEiTZn1m6ah4-LHYs

# Run locally
python bot.py
```

## 📋 Bot Features

### User Commands
- `/start` - Welcome & commands menu
- `/createprofile` - Create anonymous profile (6 questions)
- `/profile` - View your profile
- `/findmatch` - Search for chat partner
- `/stopchat` - End current chat
- `/premium` - View subscription options

### Premium System
- **Free**: Males chat with males only
- **Premium**: Chat with anyone ($4.99-$99.99)

## 🔧 Troubleshooting Render Deployment

### Common Issues:

1. **Build fails**: Check requirements.txt format
2. **Bot doesn't start**: Verify BOT_TOKEN environment variable
3. **Database errors**: SQLite creates automatically
4. **Port issues**: Render handles ports automatically

### Check Logs:
- Go to Render dashboard → Your service → "Logs" tab
- Look for startup messages or errors

## 📊 Admin Features
- User statistics
- Broadcast messages  
- Premium user management

## 🗄️ Database
- SQLite (file-based, persistent)
- Automatic table creation
- User profiles, chats, messages stored

Ready to deploy! 🚀
