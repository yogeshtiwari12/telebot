# 💕 Anonymous Dating Bot

A Telegram bot that allows anonymous dating and chatting with subscription-based features.

## 🌟 Features

- **Anonymous Profiles**: Users create profiles without revealing gender labels
- **Smart Matching**: Connects compatible users for chatting
- **Subscription System**: Premium access for chatting with all users
- **Free Tier**: Basic access with limited matching options
- **Safe Environment**: Respectful and moderated chat experience
- **Privacy Focused**: No personal information shared during chats

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### 2. Installation

```bash
# Navigate to the bot directory
cd c:\Users\yt781\tg_bots\dating_bot

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

1. Open `bot.py`
2. Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token:
```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

### 4. Run the Bot

```bash
python bot.py
```

## 💬 How It Works

### For Users:

1. **Start**: Use `/start` to begin
2. **Create Profile**: Set up anonymous profile (age, bio, preference)
3. **Find Matches**: Search for compatible users
4. **Chat Anonymously**: Messages are forwarded without revealing identity
5. **Premium Access**: Subscribe for unlimited matching

### Subscription Rules:

- **Free Users**: Limited matching based on gender preferences
- **Premium Users**: Can chat with anyone
- **Anonymous**: Gender labels are not shown to maintain anonymity

## 🎛️ Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show main menu |
| `/profile` | View your profile |
| `/premium` | View subscription options |
| `/stop_chat` | End current chat session |
| `/help` | Show help information |

## 🏗️ Bot Structure

```
dating_bot/
│
├── bot.py              # Main bot application
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── dating_bot.db      # SQLite database (auto-created)
```

## 📊 Database Schema

### Tables:
- **users**: User profiles and subscription status
- **chat_sessions**: Active and past chat sessions
- **messages**: Chat message history
- **subscription_plans**: Available premium plans

## 🎯 Key Features Explained

### 1. Anonymous Matching
- Users are matched without revealing gender labels
- Focus on personality and compatibility

### 2. Subscription System
- **Weekly Premium**: $4.99 for 1 week access
- **Monthly Premium**: $14.99 for 1 month access  
- **Yearly Premium**: $99.99 for 1 year access

### 3. Chat Privacy
- Messages are forwarded as "Anonymous: [message]"
- No personal information shared during chat
- Users can end chats anytime

### 4. Smart Matching Algorithm
- Premium users can match with anyone
- Free users have limited options
- Prevents matching with users already in active chats

## 🔒 Privacy & Safety

- No personal information displayed during chats
- Users can end conversations anytime
- Respectful communication encouraged
- Anonymous environment protects user privacy

## 🛠️ Customization Options

### Modify Subscription Plans
Edit the prices and durations in `config.py`:

```python
SUBSCRIPTION_PLANS = {
    "weekly": {"price": 4.99, "duration_days": 7},
    # Add more plans as needed
}
```

### Change Bot Behavior
Modify matching logic in the `find_match()` method in `bot.py`

### Add New Features
- Photo sharing capabilities
- Location-based matching
- Interest-based filtering
- Chat history export

## 🐛 Troubleshooting

### Common Issues:

1. **Bot not responding**: Check if token is correct
2. **Database errors**: Ensure write permissions in bot directory
3. **Matching issues**: Verify user profiles are complete
4. **Premium not working**: Check subscription expiry dates

### Error Logs:
The bot logs important events. Check console output for debugging.

## 📝 Usage Examples

### Creating a Profile:
```
User: /start
Bot: Welcome to Anonymous Dating Bot! Click 'Create Profile' to get started.

User: [Clicks Create Profile]
Bot: Select your preference (this won't be shown to others)

User: [Selects preference] 
Bot: Enter your age (18-99)

User: 25
Bot: Write a brief bio about yourself
```

### Finding Matches:
```
User: [Clicks Find Match]
Bot: Searching for a match...

[When match found]
Bot: Match found! You're now connected with someone.
     Start chatting by sending a message!
```

### Premium Subscription:
```
User: [Clicks Premium]
Bot: Premium Membership
     • Chat with all users
     • Unlimited matches
     Choose your plan: [Weekly/Monthly/Yearly]
```

## 🤝 Contributing

Feel free to contribute by:
- Adding new features
- Improving matching algorithms
- Enhancing user interface
- Fixing bugs and issues

## ⚠️ Important Notes

1. **Payment Integration**: Currently uses simulated payments. Integrate with real payment gateways for production.
2. **Moderation**: Consider adding content moderation for safer environment.
3. **Scaling**: For high traffic, consider using Redis for session management.
4. **Legal**: Ensure compliance with local dating app regulations.

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review error logs in console
- Modify code as needed for your requirements

---

**Made with ❤️ for anonymous connections and meaningful conversations**
