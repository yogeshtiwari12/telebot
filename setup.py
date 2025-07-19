"""
Setup script for Dating Bot
Run this to configure your bot token
"""

def setup_bot():
    print("🤖 Dating Bot Setup")
    print("=" * 40)
    print()
    
    print("📋 Steps to get your bot token:")
    print("1. Go to https://t.me/BotFather")
    print("2. Send /newbot command")
    print("3. Choose a name for your bot (e.g., 'My Dating Bot')")
    print("4. Choose a username (must end with 'bot', e.g., 'mydating_bot')")
    print("5. Copy the token you receive")
    print()
    
    token = input("🔑 Enter your bot token: ").strip()
    
    if not token or token == "":
        print("❌ No token provided!")
        return
    
    if not token.count(':') == 1 or len(token.split(':')[0]) < 8:
        print("❌ Invalid token format!")
        print("Token should look like: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        return
    
    # Read the bot.py file
    try:
        with open('bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the token
        updated_content = content.replace(
            'BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"',
            f'BOT_TOKEN = "{token}"'
        )
        
        # Write back to file
        with open('bot.py', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Bot token configured successfully!")
        print()
        print("🚀 To start your bot, run:")
        print("   python bot.py")
        print()
        print("🔹 Your bot features:")
        print("  • Anonymous profile creation")
        print("  • Smart matching system")
        print("  • Subscription-based premium access") 
        print("  • Private messaging")
        print("  • Gender-neutral approach")
        
    except FileNotFoundError:
        print("❌ bot.py file not found!")
        print("Make sure you're in the correct directory.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup_bot()
