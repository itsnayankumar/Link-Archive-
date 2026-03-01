import os
import re
import threading
import telebot
from flask import Flask

# --- SHARED DATA STORAGE ---
# This list will hold all the scraped links.
# (Note: On the free Render tier, this will reset if the server restarts. 
# We can add a database later if you need permanent storage).
saved_media = []

# --- FLASK SETUP (The Website) ---
app = Flask(__name__)

@app.route('/')
def home():
    html = "<h1>🎬 My Media Server Archive</h1>"
    
    if not saved_media:
        html += "<p>No media saved yet. Forward a message to the bot!</p>"
    else:
        html += "<ul>"
        # Loop through our saved data and build the HTML
        for item in reversed(saved_media): # Show newest first
            html += f"<li>"
            html += f"<h3>{item['name']}</h3>"
            html += f"<p>Size: {item['size']}</p>"
            html += f"<p><a href='{item['download']}' target='_blank'>📥 Download File</a> | "
            html += f"<a href='{item['watch']}' target='_blank'>🍿 Watch Online</a></p>"
            html += f"</li><hr>"
        html += "</ul>"
        
    return html

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT SETUP ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TOKEN_HERE")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text
    
    # Check if this is the correct message format
    if "File Name :" in text and "Download :" in text:
        try:
            # Use Regex to cleanly extract exactly what we need
            name_match = re.search(r'File Name :\s*(.+)', text)
            size_match = re.search(r'File Size :\s*(.+)', text)
            dl_match = re.search(r'Download :\s*(https?://\S+)', text)
            watch_match = re.search(r'Watch Online :\s*(https?://\S+)', text)
            
            if name_match and dl_match and watch_match:
                # Store the extracted data in a dictionary
                media_data = {
                    "name": name_match.group(1).strip(),
                    "size": size_match.group(1).strip() if size_match else "Unknown",
                    "download": dl_match.group(1).strip(),
                    "watch": watch_match.group(1).strip()
                }
                
                # Add it to our global list so the website can see it
                saved_media.append(media_data)
                
                # Let you know it worked
                bot.reply_to(message, f"✅ Saved to website!\n**{media_data['name']}**", parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ Could not extract the links. Make sure the format is exact.")
                
        except Exception as e:
            bot.reply_to(message, f"❌ Error extracting data: {e}")
    else:
        bot.reply_to(message, "Send or forward a message containing 'File Name :' and 'Download :'")

if __name__ == "__main__":
    # Start Flask
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # Start Bot
    print("🤖 Bot is waking up...")
    bot.polling(none_stop=True)
