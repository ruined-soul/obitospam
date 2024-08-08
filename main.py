from telegram import Update, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import threading
import time

# Owner's information
OWNER_ID = 5585016974
OWNER_USERNAME = "i_killed_my_clan"

# Data Structures
sudo_users = set()
added_bots = {}
spam_flag = threading.Event()
spam_lock = threading.Lock()

# Define the /start command handler
def start(update: Update, context: CallbackContext):
    message = "Welcome to the Spam Bot! I'm here to assist you. Use /help to see available commands."
    update.message.reply_text(message)

# Define the /help command handler
def help_command(update: Update, context: CallbackContext):
    help_text = (
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/alive - Check bot's speed and ping\n"
        "/spam <n> <message> - Send the message n times\n"
        "/stop_spam - Stop the ongoing spam\n"
        "/add_sudo <user_id> - Add a sudo user\n"
        "/remove_sudo <user_id> - Remove a sudo user\n"
        "/listsudo - List all sudo users\n"
        "/stats - Get bot stats (ping, users, bots added)\n"
        "/broadcast <message> - Broadcast a message or media\n"
    )
    update.message.reply_text(help_text)

# Define the /alive command handler
def alive(update: Update, context: CallbackContext):
    start_time = time.time()
    reply_message = "â³ Checking bot status..."
    message = update.message.reply_text(reply_message)
    end_time = time.time()
    ping = round((end_time - start_time) * 1000)
    reply_message = (
        f"ðŸ¤– *Bot is Alive!*\n"
        f"âš¡ï¸ *Speed*: {ping}ms\n"
        f"ðŸ”„ *Status*: All systems operational."
    )
    message.edit_text(reply_message, parse_mode="Markdown")

# Define the /spam command handler
def spam(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id == OWNER_ID or user_id in sudo_users:
        try:
            n = int(context.args[0])
            message = ' '.join(context.args[1:])
            
            with spam_lock:
                spam_flag.clear()
                for _ in range(n):
                    if spam_flag.is_set():
                        break
                    context.bot.send_message(chat_id=update.message.chat_id, text=message)
            update.message.reply_text("Spam completed successfully!")
        except (IndexError, ValueError):
            update.message.reply_text("Usage: /spam <n> <message>")
    else:
        update.message.reply_text("You are not authorized to use this command.")

# Define the /stop_spam command handler
def stop_spam(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id == OWNER_ID or user_id in sudo_users:
        with spam_lock:
            spam_flag.set()
        update.message.reply_text("Spam stopped successfully.")
    else:
        update.message.reply_text("You are not authorized to use this command.")

# Define the /add_sudo command handler
def add_sudo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id == OWNER_ID:
        try:
            sudo_id = int(context.args[0])
            sudo_users.add(sudo_id)
            update.message.reply_text(f"User ID {sudo_id} added as a sudo user successfully.")
        except (IndexError, ValueError):
            update.message.reply_text("Usage: /add_sudo <user_id>")
    else:
        update.message.reply_text("You are not authorized to use this command.")

# Define the /remove_sudo command handler
def remove_sudo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id == OWNER_ID:
        try:
            sudo_id = int(context.args[0])
            sudo_users.discard(sudo_id)
            update.message.reply_text(f"User ID {sudo_id} removed from sudo users successfully.")
        except (IndexError, ValueError):
            update.message.reply_text("Usage: /remove_sudo <user_id>")
    else:
        update.message.reply_text("You are not authorized to use this command.")

# Define the /listsudo command handler
def listsudo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id == OWNER_ID:
        if sudo_users:
            sudo_list = "\n".join([str(sudo_id) for sudo_id in sudo_users])
            update.message.reply_text(f"Sudo users:\n{sudo_list}")
        else:
            update.message.reply_text("No sudo users added.")
    else:
        update.message.reply_text("You are not authorized to use this command.")

# Define the /addbot command handler
def addbot(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id == OWNER_ID:
        try:
            bot_token = context.args[0]
            added_bot = Bot(token=bot_token)
            added_bots[bot_token] = added_bot
            update.message.reply_text(f"Bot added successfully with token: {bot_token}")
        except (IndexError, ValueError):
            update.message.reply_text("Usage: /addbot <bot_token>")
    else:
        update.message.reply_text("You are not authorized to use this command.")

# Define the /rmbot command handler
def rmbot(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id == OWNER_ID:
        try:
            bot_token = context.args[0]
            if bot_token in added_bots:
                del added_bots[bot_token]
                update.message.reply_text(f"Bot removed successfully with token: {bot_token}")
            else:
                update.message.reply_text("Bot not found.")
        except (IndexError, ValueError):
            update.message.reply_text("Usage: /rmbot <bot_token>")
    else:
        update.message.reply_text("You are not authorized to use this command.")

# Define the /lsbot command handler
def lsbot(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id == OWNER_ID:
        if added_bots:
            bot_list = "\n".join([str(token) for token in added_bots])
            update.message.reply_text(f"Added bots:\n{bot_list}")
        else:
            update.message.reply_text("No bots added.")
    else:
        update.message.reply_text("You are not authorized to use this command.")

# Define the /stats command handler
def stats(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id == OWNER_ID:
        start_time = time.time()
        message = update.message.reply_text("Fetching stats...")
        end_time = time.time()
        ping = round((end_time - start_time) * 1000)
        user_count = len(context.bot_data.get('users', set()))
        bot_count = len(added_bots)
        stats_message = (
            f"ðŸ“Š *Bot Stats*\n"
            f"âš¡ï¸ *Ping*: {ping}ms\n"
            f"ðŸ‘¥ *Users*: {user_count}\n"
            f"ðŸ¤– *Bots Added*: {bot_count}"
        )
        message.edit_text(stats_message, parse_mode="Markdown")
    else:
        update.message.reply_text("You are not authorized to use this command.")

# Define the /broadcast command handler
def broadcast(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id == OWNER_ID:
        if update.message.reply_to_message:
            target_message = update.message.reply_to_message
            context.bot.send_message(chat_id=update.message.chat_id, text=target_message.text)
        else:
            message = ' '.join(context.args)
            context.bot.send_message(chat_id=update.message.chat_id, text=message)
        update.message.reply_text("Broadcast sent successfully.")
    else:
        update.message.reply_text("You are not authorized to use this command.")

# Define the /rspam command handler
def rspam(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id == OWNER_ID:
        try:
            n = int(context.args[0])
            if update.message.reply_to_message:
                message = update.message.reply_to_message.text
                for _ in range(n):
                    context.bot.send_message(chat_id=update.message.chat_id, text=message)
                update.message.reply_text("Rspam completed successfully!")
            else:
                update.message.reply_text("You must reply to a message to use /rspam.")
        except (IndexError, ValueError):
            update.message.reply_text("Usage: /rspam <n>")
    else:
        update.message.reply_text("You are not authorized to use this command.")

# Main function to start the bot
def main():
    bot_token = "6690642431:AAGSF6SvAuOx-Wu6ztRExET6e85DcTroTz8"
    
    updater = Updater(bot_token)

    # Register command handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("alive", alive))
    dp.add_handler(CommandHandler("spam", spam, pass_args=True))
    dp.add_handler(CommandHandler("stop_spam", stop_spam))
    dp.add_handler(CommandHandler("add_sudo", add_sudo, pass_args=True))
    dp.add_handler(CommandHandler("remove_sudo", remove_sudo, pass_args=True))
    dp.add_handler(CommandHandler("listsudo", listsudo))
    dp.add_handler(CommandHandler("addbot", addbot, pass_args=True))
    dp.add_handler(CommandHandler("rmbot", rmbot, pass_args=True))
    dp.add_handler(CommandHandler("lsbot", lsbot))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("broadcast", broadcast, pass_args=True))
    dp.add_handler(CommandHandler("rspam", rspam, pass_args=True))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
