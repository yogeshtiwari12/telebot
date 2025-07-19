# Dating Bot Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from @BotFather
DATABASE_PATH = "dating_bot.db"

# Premium subscription prices (in USD)
SUBSCRIPTION_PLANS = {
    "weekly": {
        "price": 4.99,
        "duration_days": 7,
        "description": "Chat with all users for 1 week"
    },
    "monthly": {
        "price": 14.99, 
        "duration_days": 30,
        "description": "Chat with all users for 1 month"
    },
    "yearly": {
        "price": 99.99,
        "duration_days": 365,
        "description": "Chat with all users for 1 year"
    }
}

# Bot settings
MAX_BIO_LENGTH = 200
MIN_AGE = 18
MAX_AGE = 99
ANONYMOUS_CHAT = True  # Don't reveal identities during chat
