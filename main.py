import os
import re
import threading
import telebot
from flask import Flask, render_template_string
from pymongo import MongoClient
from bson.objectid import ObjectId

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TOKEN_HERE")
MONGO_URI = os.environ.get("MONGO_URI", "YOUR_MONGODB_URI_HERE")

# --- MONGODB SETUP ---
client = MongoClient(MONGO_URI)
db = client["media_archive"]
collection = db["media"]

# --- GLOBAL STATE ---
incognito_users = {}

# --- BOT SETUP ---
bot = telebot.TeleBot(BOT_TOKEN)

# --- FILENAME CLEANER ---
def clean_filename(filename):
    tags_to_remove = ["HDHub4u.ws", "4kHDHub.com", "MoviesMod.plus", "NKT"]
    for tag in tags_to_remove:
        filename = re.sub(rf'\[?{re.escape(tag)}\]?', '', filename, flags=re.IGNORECASE)
    
    # Format as: moviename year Quality
    filename = filename.replace(".", " ").replace("_", " ")
    return re.sub(r'\s+', ' ', filename).strip()

# --- FLASK SETUP (The Website) ---
app = Flask(__name__)

# Neon "Drive" Aesthetic UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎬 Media Server Archive</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Rajdhani:wght@500;700&display=swap" rel="stylesheet">
    <style>
        body { 
            font-family: 'Rajdhani', sans-serif; 
            background-color: #0d0d12; 
            background-image: radial-gradient(circle at top right, #1a0b2e, #0d0d12);
            color: #e0e0e0; 
            padding: 20px; 
            margin: 0; 
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .container { max-width: 1200px; margin: auto; flex: 1; width: 100%; }
        .header { text-align: center; margin-bottom: 40px; padding: 20px; text-transform: uppercase; letter-spacing: 2px; }
        .header h1 { 
            font-family: 'Orbitron', sans-serif; 
            color: #fff; 
            text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 40px #00ffff; 
            margin: 0; 
            font-size: 2.5rem;
        }
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); 
            gap: 25px; 
        }
        .card { 
            background: rgba(20, 20, 30, 0.6); 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 255, 0.1); 
            padding: 25px; 
            border-radius: 16px; 
            box-shadow: 0 4px 15px rgba(0, 255, 255, 0.05);
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .card:hover { 
            transform: translateY(-5px); 
            box-shadow: 0 0 25px rgba(0, 255, 255, 0.3);
            border-color: #00ffff;
        }
        .card h3 { margin-top: 0; color: #fff; font-size: 1.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px; }
        .meta { font-size: 0.95rem; color: #8892b0; margin-bottom: 20px; }
        .meta code { background: #1a1a24; padding: 3px 8px; border-radius: 4px; color: #ff00ff; font-family: monospace; }
        .btn-group { display: flex; gap: 15px; }
        .btn { 
            flex: 1; text-align: center; padding: 10px; border-radius: 8px; text-decoration: none; 
            font-weight: bold; text-transform: uppercase; font-size: 0.9rem; transition: all 0.3s; letter-spacing: 1px;
        }
        .btn-dl { background: transparent; color: #00ffff; border: 1px solid #00ffff; box-shadow: 0 0 5px rgba(0, 255, 255, 0.2); }
        .btn-dl:hover { background: #00ffff; color: #000; box-shadow: 0 0 15px #00ffff; }
        .btn-watch { background: transparent; color: #ff00ff; border: 1px solid #ff00ff; box-shadow: 0 0 5px rgba(255, 0, 255, 0.2); }
        .btn-watch:hover { background: #ff00ff; color: #000; box-shadow: 0 0 15px #ff00ff; }
        .footer { text-align: center; color: #4a5568; margin-top: 50px; font-size: 0.9rem; padding-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Neon Drive Archive</h1>
        </div>
        
        {% if not media_list %}
            <div class="card" style="text-align: center; border-color: #ff00ff; box-shadow: 0 0 20px rgba(255, 0, 255, 0.2);">
                <h3 style="border: none;">Drive Empty</h3>
                <p style="color: #8892b0;">Initialize the database by forwarding media to the bot.</p>
            </div>
        {% else %}
            <div class="grid">
                {% for item in media_list %}
                    <div class="card">
                        <h3>{{ item.name }}</h3>
                        <div class="meta">
                            📦 <b>Size:</b> {{ item.size }}<br><br>
                            🔑 <b>ID:</b> <code>{{ item._id }}</code>
                        </div>
                        <div class="btn-group">
                            <a class="btn btn-dl" href="{{ item.download }}" target="_blank">📥 DL Link</a>
                            <a class="btn btn-watch" href="{{ item.watch }}" target="_blank">🍿 Stream</a>
                        </div>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    </div>
    <div class="footer">
        Maintained by @itsnayankumar | Encrypted via MongoDB
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    media_list = list(collection.find().sort("_id", -1))
    return render_template_string(HTML_TEMPLATE, media_list=media_list)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- BOT COMMANDS ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    help_text = (
        "🤖 **Neon Drive Bot**\n\n"
        "Send me links. I extract them and push them to the drive.\n\n"
        "**Commands:**\n"
        "• `/incognito` - Toggle stealth mode (auto-deletes your messages)\n"
        "• `/delete <ID>` - Wipe an entry from the database\n"
        "• `/list` - View the last 5 added items"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['incognito'])
def toggle_incognito(message):
    user_id = message.from_user.id
    if incognito_users.get(user_id):
        incognito_users[user_id] = False
        bot.reply_to(message, "👁️ Incognito Mode **OFF**.", parse_mode="Markdown")
    else:
        incognito_users[user_id] = True
        bot.reply_to(message, "👻 Incognito Mode **ON**. Messages will self-destruct after saving.", parse_mode="Markdown")

@bot.message_handler(commands=['delete'])
def delete_entry(message):
    try:
        entry_id = message.text.split(" ")[1].strip()
        result = collection.delete_one({"_id": ObjectId(entry_id)})
        
        if result.deleted_count > 0:
            bot.reply_to(message, f"🗑️ Purged entry `{entry_id}` from the database.", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ No matching ID found.")
    except Exception:
        bot.reply_to(message, "❌ Format error. Use: `/delete <ID>`", parse_mode="Markdown")

@bot.message_handler(commands=['list'])
def list_entries(message):
    recent = list(collection.find().sort("_id", -1).limit(5))
    if not recent:
        bot.reply_to(message, "Drive is currently empty.")
        return
    
    response = "🕒 **Recent Uploads:**\n\n"
    for item in recent:
        response += f"🎬 {item['name']}\n🔑 `{item['_id']}`\n\n"
    
    bot.reply_to(message, response, parse_mode="Markdown")

# --- FLEXIBLE MESSAGE HANDLER ---

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text
    user_id = message.from_user.id
    
    urls = re.findall(r'(https?://[^\s]+)', text)
    if not urls:
        bot.reply_to(message, "❌ Link extraction failed. No valid URLs found.")
        return

    download_link = urls[0]
    watch_link = urls[1] if len(urls) > 1 else download_link 

    size_match = re.search(r'(\d+(?:\.\d+)?\s*(?:MB|GB))', text, re.IGNORECASE)
    size = size_match.group(1).upper() if size_match else "Unknown"

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    raw_name = lines[0] if lines else "Unknown Media"
    raw_name = re.sub(r'^(File Name|Name|Title)\s*[:\-]\s*', '', raw_name, flags=re.IGNORECASE)
    
    clean_name = clean_filename(raw_name)

    media_data = {
        "name": clean_name,
        "size": size,
        "download": download_link,
        "watch": watch_link
    }
    
    inserted = collection.insert_one(media_data)

    if incognito_users.get(user_id):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            msg = bot.send_message(message.chat.id, f"👻 Encrypted & Stored: **{clean_name}**", parse_mode="Markdown")
            threading.Timer(3.0, bot.delete_message, args=(message.chat.id, msg.message_id)).start()
        except Exception:
            pass
    else:
        bot.reply_to(message, f"✅ Stored to Drive!\n**{clean_name}**\n🔑 ID: `{inserted.inserted_id}`", parse_mode="Markdown")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    print("🤖 Drive Bot initializing...")
    bot.polling(none_stop=True)
