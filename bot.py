import logging
import sqlite3
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import BadRequest
import asyncio
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = 'dating_bot.db'

class DatingBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.active_chats: Dict[int, int] = {}  # user_id: partner_id
        self.pending_matches: List[int] = []  # Users waiting for matches
        self.init_database()
        self.setup_handlers()

    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                gender TEXT,
                age TEXT,
                favorite_game TEXT,
                favorite_movie TEXT,
                favorite_music TEXT,
                interests TEXT,
                photo_url TEXT,
                is_premium BOOLEAN DEFAULT FALSE,
                premium_expires DATETIME,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chat sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_id INTEGER,
                user2_id INTEGER,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user1_id) REFERENCES users (user_id),
                FOREIGN KEY (user2_id) REFERENCES users (user_id)
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                sender_id INTEGER,
                message_text TEXT,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id),
                FOREIGN KEY (sender_id) REFERENCES users (user_id)
            )
        ''')
        
        # Subscription plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscription_plans (
                plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_name TEXT,
                duration_days INTEGER,
                price REAL,
                description TEXT
            )
        ''')
        
        # Insert default subscription plans
        cursor.execute('''
            INSERT OR IGNORE INTO subscription_plans (plan_id, plan_name, duration_days, price, description)
            VALUES 
                (1, 'Weekly Premium', 7, 4.99, 'Chat with all users for 1 week'),
                (2, 'Monthly Premium', 30, 14.99, 'Chat with all users for 1 month'),
                (3, 'Yearly Premium', 365, 99.99, 'Chat with all users for 1 year')
        ''')
        
        conn.commit()
        conn.close()

    def setup_handlers(self):
        """Set up command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("profile", self.show_profile))
        self.application.add_handler(CommandHandler("createprofile", self.create_profile_start))
        self.application.add_handler(CommandHandler("search", self.search_for_match))
        self.application.add_handler(CommandHandler("findmatch", self.search_for_match))
        self.application.add_handler(CommandHandler("premium", self.premium_command))
        self.application.add_handler(CommandHandler("stopchat", self.stop_chat_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("menu", self.show_main_menu))
        self.application.add_handler(CommandHandler("activechat", self.show_active_chat_info))
        
        # Admin commands
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("stats", self.admin_stats))
        self.application.add_handler(CommandHandler("broadcast", self.admin_broadcast))
        
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        # Check if user exists in database
        if not self.get_user(user_id):
            # New user registration
            await update.message.reply_text(
                f"🌹 Welcome to Anonymous Dating Bot! 🌹\n\n"
                f"Find your perfect match without revealing identities upfront.\n\n"
                f"📋 Available Commands:\n"
                f"/createprofile - Create your profile\n"
                f"/help - See all commands\n\n"
                f"Start by creating your profile to begin matching!",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            # Existing user
            await self.show_commands_menu(update)

    async def show_commands_menu(self, update: Update):
        """Show available commands to existing users"""
        commands_text = (
            "🏠 Dating Bot Commands\n\n"
            "👤 Profile:\n"
            "/profile - View your profile\n"
            "/createprofile - Create new profile\n\n"
            "💬 Matching & Chat:\n"
            "/findmatch - Find a match\n"
            "/activechat - Check active chat\n"
            "/stopchat - End current chat\n\n"
            "💎 Premium:\n"
            "/premium - View premium options\n\n"
            "ℹ️ Help:\n"
            "/help - Show all commands\n"
            "/menu - Show this menu"
        )
        
        await update.message.reply_text(commands_text, reply_markup=ReplyKeyboardRemove())

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu to existing users"""
        await self.show_commands_menu(update)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Check if user is in an active chat
        if user_id in self.active_chats:
            partner_id = self.active_chats[user_id]
            try:
                await context.bot.send_message(
                    chat_id=partner_id,
                    text=f"💬 Anonymous: {message_text}"
                )
                # Save message to database
                self.save_message(user_id, partner_id, message_text)
            except BadRequest:
                # Partner blocked the bot or chat is unavailable
                await update.message.reply_text(
                    "❌ Your chat partner is no longer available. Starting new search..."
                )
                await self.end_chat(user_id, partner_id)
                await self.search_for_match(update, context)
            return
        
        # Handle profile creation steps
        await self.handle_profile_creation(update, context, message_text)

    async def create_profile_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start profile creation process"""
        context.user_data['creating_profile'] = True
        context.user_data['profile_step'] = 'name'
        
        await update.message.reply_text(
            "Let's create your profile! 📝\n\n"
            "We'll ask you 6 questions to build your profile:\n"
            "1️⃣ Name\n2️⃣ Gender\n3️⃣ Age\n4️⃣ Favorite Game\n5️⃣ Favorite Movie\n6️⃣ Favorite Music\n\n"
            "💡 You can enter anything you want or type 'skip' to skip a question.\n\n"
            "Step 1: What's your name? (or skip)",
            reply_markup=ReplyKeyboardRemove()
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data.startswith("premium_"):
            plan_id = int(data.split("_")[1])
            await self.handle_premium_purchase(query, context, plan_id)

    async def handle_profile_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Handle profile creation steps"""
        if not context.user_data.get('creating_profile'):
            return
            
        user_id = update.effective_user.id
        step = context.user_data.get('profile_step')
        
        if step == 'name':
            # Accept any input for name, even empty or "skip"
            if message_text.strip().lower() == 'skip':
                context.user_data['name'] = 'Anonymous'
            else:
                context.user_data['name'] = message_text.strip() if message_text.strip() else 'Anonymous'
            
            context.user_data['profile_step'] = 'gender'
            await update.message.reply_text(
                "Step 2: What's your gender? (M/F/Other or anything you want, or 'skip')"
            )
                
        elif step == 'gender':
            # Accept any input for gender
            if message_text.strip().lower() == 'skip':
                context.user_data['gender'] = 'Not specified'
            else:
                gender_input = message_text.strip().lower()
                if gender_input in ['m', 'male']:
                    context.user_data['gender'] = 'Male'
                elif gender_input in ['f', 'female']:
                    context.user_data['gender'] = 'Female'
                else:
                    # Accept anything else as custom gender
                    context.user_data['gender'] = message_text.strip() if message_text.strip() else 'Not specified'
            
            context.user_data['profile_step'] = 'age'
            await update.message.reply_text("Step 3: What's your age? (any number or text, or 'skip')")
                
        elif step == 'age':
            # Accept any input for age
            if message_text.strip().lower() == 'skip':
                context.user_data['age'] = 'Not specified'
            else:
                try:
                    age = int(message_text.strip())
                    context.user_data['age'] = age
                except ValueError:
                    # If not a number, store as text
                    context.user_data['age'] = message_text.strip() if message_text.strip() else 'Not specified'
            
            context.user_data['profile_step'] = 'favorite_game'
            await update.message.reply_text(
                "Step 4: What's your favorite game? (anything or 'skip')"
            )
                
        elif step == 'favorite_game':
            if len(message_text.strip()) > 0:
                context.user_data['favorite_game'] = message_text.strip()
                context.user_data['profile_step'] = 'favorite_movie'
                await update.message.reply_text(
                    "Step 5: What's your favorite movie?\n"
                    "(e.g., Avengers, Titanic, The Dark Knight, etc.)"
                )
            else:
                await update.message.reply_text("Please enter your favorite game:")
                
        elif step == 'favorite_movie':
            if len(message_text.strip()) > 0:
                context.user_data['favorite_movie'] = message_text.strip()
                context.user_data['profile_step'] = 'favorite_music'
                await update.message.reply_text(
                    "Step 6: What's your favorite music/artist?\n"
                    "(e.g., Pop, Rock, Hip-Hop, Classical, Taylor Swift, etc.)"
                )
            else:
                await update.message.reply_text("Please enter your favorite movie:")
                
        elif step == 'favorite_music':
            if len(message_text.strip()) > 0:
                context.user_data['favorite_music'] = message_text.strip()
                await self.finalize_profile(update, context)
            else:
                await update.message.reply_text("Please tell us about your favorite music:")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo uploads - not needed anymore"""
        pass

    async def finalize_profile(self, update_or_query, context: ContextTypes.DEFAULT_TYPE):
        """Finalize profile creation"""
        user_data = context.user_data
        user = update_or_query.effective_user if hasattr(update_or_query, 'effective_user') else update_or_query.from_user
        
        # Save user to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, gender, age, favorite_game, favorite_movie, favorite_music, interests, photo_url, last_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user.id,
            user.username,
            user_data.get('name', user.first_name),
            user_data.get('gender'),
            user_data.get('age'),
            user_data.get('favorite_game'),
            user_data.get('favorite_movie'),
            user_data.get('favorite_music'),
            '',  # interests field kept for compatibility
            '',  # Empty photo_url
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        # Clear profile creation data
        context.user_data.clear()
        
        message_text = "✅ Profile created successfully!\n\nYou can now start finding matches!"
        
        if hasattr(update_or_query, 'message'):
            await update_or_query.message.reply_text(message_text, reply_markup=ReplyKeyboardRemove())
            await self.show_commands_menu(update_or_query)
        else:
            await update_or_query.edit_message_text(message_text)
            # Show commands menu by sending new message
            await context.bot.send_message(
                chat_id=user.id,
                text="🏠 Dating Bot Commands\n\n"
                     "👤 Profile:\n"
                     "/profile - View your profile\n"
                     "/createprofile - Create new profile\n\n"
                     "💬 Matching & Chat:\n"
                     "/findmatch - Find a match\n"
                     "/activechat - Check active chat\n"
                     "/stopchat - End current chat\n\n"
                     "💎 Premium:\n"
                     "/premium - View premium options\n\n"
                     "ℹ️ Help:\n"
                     "/help - Show all commands\n"
                     "/menu - Show this menu",
                reply_markup=ReplyKeyboardRemove()
            )

    async def search_for_match(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Search for a match"""
        user_id = update.effective_user.id
        
        # Check if user has profile
        if not self.get_user(user_id):
            await update.message.reply_text(
                "❌ Please create your profile first using /createprofile.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        # Check if already in chat
        if user_id in self.active_chats:
            await update.message.reply_text(
                "❌ You're already in a chat! Use /stopchat to end it first.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        user_data = self.get_user(user_id)
        user_gender = user_data[3]  # gender column
        
        # Find potential matches
        potential_match = self.find_match(user_id, user_gender)
        
        if potential_match:
            # Start chat
            partner_id = potential_match[0]
            await self.start_chat(user_id, partner_id, context)
        else:
            # Add to pending matches
            if user_id not in self.pending_matches:
                self.pending_matches.append(user_id)
            
            await update.message.reply_text(
                "🔍 Searching for a match...\n\n"
                "You'll be notified when someone is found!\n"
                "You can continue using other features while waiting.",
                reply_markup=ReplyKeyboardRemove()
            )

    def find_match(self, user_id: int, user_gender: str) -> Optional[tuple]:
        """Find a potential match for the user"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # For premium users, they can chat with anyone
        # For non-premium users, males can only chat with males, females need premium to chat
        user_premium = self.is_user_premium(user_id)
        
        if user_premium:
            # Premium users can match with anyone who is not in active chat
            cursor.execute('''
                SELECT user_id FROM users 
                WHERE user_id != ? AND is_active = TRUE
                AND user_id NOT IN (SELECT user1_id FROM chat_sessions WHERE is_active = TRUE)
                AND user_id NOT IN (SELECT user2_id FROM chat_sessions WHERE is_active = TRUE)
                ORDER BY RANDOM()
                LIMIT 1
            ''', (user_id,))
        else:
            if user_gender == 'Male':
                # Non-premium males can only match with other males
                cursor.execute('''
                    SELECT user_id FROM users 
                    WHERE user_id != ? AND gender = 'Male' AND is_active = TRUE
                    AND user_id NOT IN (SELECT user1_id FROM chat_sessions WHERE is_active = TRUE)
                    AND user_id NOT IN (SELECT user2_id FROM chat_sessions WHERE is_active = TRUE)
                    ORDER BY RANDOM()
                    LIMIT 1
                ''', (user_id,))
            else:
                # Non-premium females cannot start chats (need premium)
                conn.close()
                return None
        
        result = cursor.fetchone()
        conn.close()
        return result

    async def start_chat(self, user1_id: int, user2_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Start a chat session between two users"""
        # Create chat session in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_sessions (user1_id, user2_id)
            VALUES (?, ?)
        ''', (user1_id, user2_id))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Update active chats
        self.active_chats[user1_id] = user2_id
        self.active_chats[user2_id] = user1_id
        
        # Remove from pending matches
        if user1_id in self.pending_matches:
            self.pending_matches.remove(user1_id)
        if user2_id in self.pending_matches:
            self.pending_matches.remove(user2_id)
        
        # Notify both users
        chat_message = (
            "💬 Match found! You're now connected with someone.\n\n"
            "🔹 Start chatting by sending a message\n"
            "🔹 Use /stopchat to end the conversation\n"
            "🔹 Be respectful and have fun! 😊"
        )
        
        try:
            await context.bot.send_message(chat_id=user1_id, text=chat_message, reply_markup=ReplyKeyboardRemove())
            await context.bot.send_message(chat_id=user2_id, text=chat_message, reply_markup=ReplyKeyboardRemove())
        except BadRequest as e:
            logger.error(f"Error starting chat: {e}")

    async def stop_chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stopchat command"""
        user_id = update.effective_user.id
        
        if user_id not in self.active_chats:
            await update.message.reply_text(
                "❌ You're not in any active chat.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        partner_id = self.active_chats[user_id]
        await self.end_chat(user_id, partner_id)
        
        try:
            await context.bot.send_message(
                chat_id=partner_id,
                text="💔 Your chat partner has left the conversation.\n\nUse /findmatch to start a new chat!",
                reply_markup=ReplyKeyboardRemove()
            )
        except BadRequest:
            pass  # Partner might have blocked the bot
        
        await update.message.reply_text(
            "💔 Chat ended successfully.\n\nUse /findmatch to start a new conversation!",
            reply_markup=ReplyKeyboardRemove()
        )

    async def end_chat(self, user1_id: int, user2_id: int):
        """End a chat session"""
        # Update database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE chat_sessions 
            SET is_active = FALSE, ended_at = ?
            WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)
            AND is_active = TRUE
        ''', (datetime.now(), user1_id, user2_id, user2_id, user1_id))
        
        conn.commit()
        conn.close()
        
        # Remove from active chats
        if user1_id in self.active_chats:
            del self.active_chats[user1_id]
        if user2_id in self.active_chats:
            del self.active_chats[user2_id]

    async def premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /premium command"""
        user_id = update.effective_user.id
        
        if self.is_user_premium(user_id):
            premium_data = self.get_premium_info(user_id)
            await update.message.reply_text(
                f"💎 You have Premium access!\n\n"
                f"Expires: {premium_data[1]}\n\n"
                f"Premium Benefits:\n"
                f"✅ Chat with all users\n"
                f"✅ Unlimited matches\n"
                f"✅ Priority matching",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            keyboard = [
                [InlineKeyboardButton("Weekly - $4.99", callback_data="premium_1")],
                [InlineKeyboardButton("Monthly - $14.99", callback_data="premium_2")],
                [InlineKeyboardButton("Yearly - $99.99", callback_data="premium_3")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "💎 Premium Membership\n\n"
                "🔹 Chat with all users\n"
                "🔹 Unlimited matches\n"
                "🔹 Priority matching\n"
                "🔹 No restrictions\n\n"
                "Choose your plan:",
                reply_markup=reply_markup
            )

    async def handle_premium_purchase(self, query, context: ContextTypes.DEFAULT_TYPE, plan_id: int):
        """Handle premium purchase (simulation)"""
        user_id = query.from_user.id
        
        # Get plan details
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM subscription_plans WHERE plan_id = ?', (plan_id,))
        plan = cursor.fetchone()
        conn.close()
        
        if not plan:
            await query.edit_message_text("❌ Invalid plan selected.")
            return
        
        # Simulate payment (in real implementation, integrate with payment gateway)
        await query.edit_message_text(
            f"💳 Payment Simulation\n\n"
            f"Plan: {plan[1]}\n"
            f"Price: ${plan[3]}\n"
            f"Duration: {plan[2]} days\n\n"
            f"✅ Payment successful! (Simulated)\n"
            f"Your premium access is now active!"
        )
        
        # Activate premium
        self.activate_premium(user_id, plan[2])

    def activate_premium(self, user_id: int, duration_days: int):
        """Activate premium for a user"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(days=duration_days)
        
        cursor.execute('''
            UPDATE users 
            SET is_premium = TRUE, premium_expires = ?
            WHERE user_id = ?
        ''', (expires_at, user_id))
        
        conn.commit()
        conn.close()

    async def show_active_chat_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show active chat information"""
        user_id = update.effective_user.id
        
        if user_id in self.active_chats:
            partner_id = self.active_chats[user_id]
            await update.message.reply_text(
                "💬 You're currently in a chat!\n\n"
                "Send any message and it will be forwarded to your chat partner.\n"
                "Use /stopchat to end the conversation.",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                "❌ You're not in any active chat.\n\n"
                "Use /findmatch to start a new conversation!",
                reply_markup=ReplyKeyboardRemove()
            )

    async def show_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user profile"""
        user_id = update.effective_user.id
        user_data = self.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text(
                "❌ You don't have a profile yet.\n\nUse /createprofile to get started!",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        premium_status = "💎 Premium" if self.is_user_premium(user_id) else "🆓 Free"
        
        profile_text = (
            f"👤 Your Profile\n\n"
            f"Name: {user_data[2] or 'Not set'}\n"
            f"Gender: {user_data[3] or 'Not set'}\n"
            f"Age: {user_data[4]}\n"
            f"Favorite Game: {user_data[5] or 'Not set'}\n"
            f"Favorite Movie: {user_data[6] or 'Not set'}\n"
            f"Favorite Music: {user_data[7] or 'Not set'}\n"
            f"Status: {premium_status}\n"
            f"Member since: {user_data[13][:10]}"
        )
        
        await update.message.reply_text(profile_text, reply_markup=ReplyKeyboardRemove())

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "🤖 Dating Bot Help\n\n"
            "🔹 How it works:\n"
            "1. Create your profile with /createprofile\n"
            "2. Find matches anonymously with /findmatch\n"
            "3. Chat without revealing identities\n"
            "4. End chat anytime with /stopchat\n\n"
            "🔹 User Commands:\n"
            "/start - Start the bot\n"
            "/createprofile - Create/update profile\n"
            "/profile - View your profile\n"
            "/findmatch - Search for matches\n"
            "/activechat - Check active chat\n"
            "/stopchat - End current chat\n"
            "/premium - View premium options\n"
            "/help - Show this help\n"
            "/menu - Show commands menu\n\n"
            "🔹 Subscription Rules:\n"
            "• Free users can chat with same gender\n"
            "• Premium unlocks all matches\n"
            "• Be respectful and have fun! 😊"
        )
        
        await update.message.reply_text(help_text, reply_markup=ReplyKeyboardRemove())

    # Admin Commands
    ADMIN_IDS = [123456789]  # Replace with actual admin user IDs

    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        user_id = update.effective_user.id
        
        if user_id not in self.ADMIN_IDS:
            await update.message.reply_text(
                "❌ You don't have admin access.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        admin_text = (
            "🔧 Admin Panel\n\n"
            "Available Commands:\n"
            "/stats - View bot statistics\n"
            "/broadcast <message> - Send message to all users\n"
            "/admin - Show this panel\n\n"
            "Database Management:\n"
            "• Total users: Use /stats\n"
            "• Active chats: Use /stats\n"
            "• Premium users: Use /stats"
        )
        
        await update.message.reply_text(admin_text, reply_markup=ReplyKeyboardRemove())

    async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot statistics to admins"""
        user_id = update.effective_user.id
        
        if user_id not in self.ADMIN_IDS:
            await update.message.reply_text(
                "❌ You don't have admin access.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_premium = TRUE')
        premium_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM chat_sessions WHERE is_active = TRUE')
        active_chats = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM messages')
        total_messages = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE gender = "Male"')
        male_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE gender = "Female"')
        female_users = cursor.fetchone()[0]
        
        conn.close()
        
        stats_text = (
            f"📊 Bot Statistics\n\n"
            f"👥 Users:\n"
            f"• Total Users: {total_users}\n"
            f"• Male Users: {male_users}\n"
            f"• Female Users: {female_users}\n"
            f"• Premium Users: {premium_users}\n\n"
            f"💬 Activity:\n"
            f"• Active Chats: {active_chats}\n"
            f"• Total Messages: {total_messages}\n"
            f"• Pending Matches: {len(self.pending_matches)}\n\n"
            f"💎 Revenue:\n"
            f"• Premium Rate: {(premium_users/total_users*100):.1f}%" if total_users > 0 else "• Premium Rate: 0%"
        )
        
        await update.message.reply_text(stats_text, reply_markup=ReplyKeyboardRemove())

    async def admin_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broadcast message to all users"""
        user_id = update.effective_user.id
        
        if user_id not in self.ADMIN_IDS:
            await update.message.reply_text(
                "❌ You don't have admin access.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        # Get message from command args
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: /broadcast <message>\n\n"
                "Example: /broadcast Welcome to our new features!",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        broadcast_message = " ".join(context.args)
        
        # Get all users
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE is_active = TRUE')
        users = cursor.fetchall()
        conn.close()
        
        success_count = 0
        failed_count = 0
        
        for user_row in users:
            user_id_to_send = user_row[0]
            try:
                await context.bot.send_message(
                    chat_id=user_id_to_send,
                    text=f"📢 Admin Announcement\n\n{broadcast_message}",
                    reply_markup=ReplyKeyboardRemove()
                )
                success_count += 1
            except Exception:
                failed_count += 1
        
        await update.message.reply_text(
            f"📢 Broadcast Complete\n\n"
            f"✅ Sent to: {success_count} users\n"
            f"❌ Failed: {failed_count} users",
            reply_markup=ReplyKeyboardRemove()
        )

    def get_user(self, user_id: int) -> Optional[tuple]:
        """Get user data from database"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def is_user_premium(self, user_id: int) -> bool:
        """Check if user has active premium"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT is_premium, premium_expires FROM users 
            WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0]:
            return False
        
        if result[1]:
            expires = datetime.fromisoformat(result[1])
            return datetime.now() < expires
        
        return False

    def get_premium_info(self, user_id: int) -> Optional[tuple]:
        """Get premium information for user"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT is_premium, premium_expires FROM users 
            WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def save_message(self, sender_id: int, receiver_id: int, message_text: str):
        """Save message to database"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get active session
        cursor.execute('''
            SELECT session_id FROM chat_sessions 
            WHERE ((user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?))
            AND is_active = TRUE
        ''', (sender_id, receiver_id, receiver_id, sender_id))
        
        session = cursor.fetchone()
        if session:
            cursor.execute('''
                INSERT INTO messages (session_id, sender_id, message_text)
                VALUES (?, ?, ?)
            ''', (session[0], sender_id, message_text))
            conn.commit()
        
        conn.close()

    def run(self):
        """Start the bot"""
        print("🤖 Dating Bot is starting...")
        print("🔹 Create profiles anonymously")
        print("🔹 Match with compatible users") 
        print("🔹 Premium subscription for unlimited access")
        print("🔹 Safe and respectful environment")
        print("🔹 NO KEYBOARD PANELS - Commands only!")
        print("\nBot is running...")
        
        self.application.run_polling()

if __name__ == '__main__':
    # Replace with your bot token
    BOT_TOKEN = "7750483935:AAENsDFiOYfB41WcjfzEiTZn1m6ah4-LHYs"
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please set your bot token in the BOT_TOKEN variable")
        print("Get your token from @BotFather on Telegram")
    else:
        bot = DatingBot(BOT_TOKEN)
        bot.run()
