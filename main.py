import os
import threading
import telebot
from flask import Flask

# --- FLASK SETUP (To keep Render's Web Service happy) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT SETUP ---
# It will pull your token securely from Render's Environment Variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TOKEN_HERE")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text
    
    # Check if the message contains the specific format
    if "File Name :" in text:
        try:
            # Extract the filename (grabs everything after "File Name : " on that line)
            lines = text.split('\n')
            file_name = "Unknown"
            file_size = "Unknown" # You can add extraction logic for size later if it's in the text
            
            for line in lines:
                if "File Name :" in line:
                    file_name = line.split("File Name :")[1].strip()
                # If your pasted text includes "Size : 500MB", you'd extract it here
                elif "Size :" in line:
                    file_size = line.split("Size :")[1].strip()
            
            # Generate your links (you can customize these base URLs later)
            base_url = "https://your-site.com"
            download_link = f"{base_url}/download/{file_name.replace(' ', '_')}"
            watch_link = f"{base_url}/watch/{file_name.replace(' ', '_')}"
            
            # Build the clean reply message
            reply = (
                f"🎬 **Extracted Data**\n\n"
                f"**Name:** `{file_name}`\n"
                f"**Size:** `{file_size}`\n\n"
                f"📥 **Download:** [Click Here]({download_link})\n"
                f"🍿 **Watch:** [Stream Here]({watch_link})"
            )
            
            bot.reply_to(message, reply, parse_mode="Markdown", disable_web_page_preview=True)
            
        except Exception as e:
            bot.reply_to(message, f"Oops, error parsing that: {e}")
    else:
        bot.reply_to(message, "Send me a message containing 'File Name : ...'")

if __name__ == "__main__":
    # 1. Start Flask in a background thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # 2. Start the Telegram Bot on the main thread
    print("🤖 Bot is waking up...")
    bot.polling(none_stop=True)
