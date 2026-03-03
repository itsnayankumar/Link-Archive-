import os
import re
import threading
import telebot
from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TOKEN_HERE")
MONGO_URI = os.environ.get("MONGO_URI", "YOUR_MONGODB_URI_HERE")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_neon_key") # Needed for secure logins

# Define Credentials (Set these in Render Environment Variables)
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin123")
GUEST_USER = os.environ.get("GUEST_USER", "user")
GUEST_PASS = os.environ.get("GUEST_PASS", "watch123")

# --- MONGODB SETUP ---
client = MongoClient(MONGO_URI)
db = client["media_archive"]
collection = db["media"]

# --- GLOBAL STATE ---
incognito_users = {}
bot = telebot.TeleBot(BOT_TOKEN)

# --- FILENAME CLEANER ---
def clean_filename(filename):
    tags_to_remove = ["HDHub4u.ws", "4kHDHub.com", "MoviesMod.plus", "NKT"]
    for tag in tags_to_remove:
        filename = re.sub(rf'\[?{re.escape(tag)}\]?', '', filename, flags=re.IGNORECASE)
    filename = filename.replace(".", " ").replace("_", " ")
    return re.sub(r'\s+', ' ', filename).strip()

# --- HTML TEMPLATES ---

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Login | Neon Drive</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Rajdhani:wght@500;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Rajdhani', sans-serif; background-color: #0d0d12; color: #e0e0e0; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: rgba(20, 20, 30, 0.8); padding: 40px; border-radius: 16px; border: 1px solid #00ffff; box-shadow: 0 0 20px rgba(0, 255, 255, 0.2); text-align: center; }
        h1 { font-family: 'Orbitron', sans-serif; color: #fff; text-shadow: 0 0 10px #00ffff; margin-bottom: 30px; }
        input { display: block; width: 100%; padding: 10px; margin-bottom: 20px; background: #1a1a24; border: 1px solid #444; color: #fff; border-radius: 5px; box-sizing: border-box; }
        button { background: transparent; color: #00ffff; border: 1px solid #00ffff; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; transition: 0.3s; }
        button:hover { background: #00ffff; color: #000; box-shadow: 0 0 15px #00ffff; }
        .error { color: #ff00ff; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>ACCESS DRIVE</h1>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">INITIALIZE</button>
        </form>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎬 Neon Drive Archive</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Rajdhani:wght@500;700&display=swap" rel="stylesheet">
    <style>
        /* (Keeping the previous CSS and adding a few components) */
        body { font-family: 'Rajdhani', sans-serif; background-color: #0d0d12; color: #e0e0e0; padding: 20px; margin: 0; min-height: 100vh; display: flex; flex-direction: column; }
        .container { max-width: 1200px; margin: auto; flex: 1; width: 100%; }
        .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .header h1 { font-family: 'Orbitron', sans-serif; color: #fff; text-shadow: 0 0 10px #00ffff; margin: 0; font-size: 2.5rem; text-align: center; margin-bottom: 20px;}
        .search-bar { width: 100%; padding: 15px; border-radius: 8px; border: 1px solid #00ffff; background: rgba(20,20,30,0.8); color: #fff; margin-bottom: 30px; font-size: 1.1rem; box-sizing: border-box; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 25px; }
        .card { background: rgba(20, 20, 30, 0.6); backdrop-filter: blur(10px); border: 1px solid rgba(0, 255, 255, 0.1); padding: 25px; border-radius: 16px; display: flex; flex-direction: column; justify-content: space-between; transition: 0.3s; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 0 25px rgba(0, 255, 255, 0.3); border-color: #00ffff; }
        .card h3 { margin-top: 0; color: #fff; font-size: 1.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px; }
        .meta { font-size: 0.95rem; color: #8892b0; margin-bottom: 20px; }
        .btn-group { display: flex; gap: 10px; margin-bottom: 10px;}
        .btn { flex: 1; text-align: center; padding: 8px; border-radius: 8px; text-decoration: none; font-weight: bold; text-transform: uppercase; font-size: 0.8rem; transition: 0.3s; cursor: pointer; }
        .btn-dl { background: transparent; color: #00ffff; border: 1px solid #00ffff; }
        .btn-dl:hover { background: #00ffff; color: #000; }
        .btn-watch { background: transparent; color: #ff00ff; border: 1px solid #ff00ff; }
        .btn-watch:hover { background: #ff00ff; color: #000; }
        .btn-admin { background: transparent; color: #ff3333; border: 1px solid #ff3333; }
        .btn-admin:hover { background: #ff3333; color: #fff; }
        .pagination { display: flex; justify-content: center; gap: 15px; margin-top: 40px; }
        .pagination a { color: #00ffff; text-decoration: none; padding: 10px 20px; border: 1px solid #00ffff; border-radius: 5px; }
        .pagination a:hover { background: #00ffff; color: #000; }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <div>Role: <b>{{ session['role'] }}</b></div>
            <a href="/logout" style="color: #ff00ff; text-decoration: none;">[ LOGOUT ]</a>
        </div>
        <div class="header"><h1>Neon Drive</h1></div>
        
        <form method="GET" action="/">
            <input type="text" name="q" class="search-bar" placeholder="Search for a movie, series, or anime..." value="{{ search_query }}">
        </form>

        <div class="grid">
            {% for item in media_list %}
                <div class="card">
                    <h3 id="title-{{ item._id }}">{{ item.name }}</h3>
                    <div class="meta">📦 Size: {{ item.size }}</div>
                    <div class="btn-group">
                        <a class="btn btn-dl" href="{{ item.download }}" target="_blank">📥 DL Link</a>
                        <a class="btn btn-watch" href="{{ item.watch }}" target="_blank">🍿 Stream</a>
                    </div>
                    {% if session['role'] == 'admin' %}
                    <div class="btn-group">
                        <button class="btn btn-admin" onclick="renameItem('{{ item._id }}', '{{ item.name|escape }}')">✏️ Rename</button>
                        <button class="btn btn-admin" onclick="deleteItem('{{ item._id }}')">🗑️ Delete</button>
                    </div>
                    {% endif %}
                </div>
            {% endfor %}
        </div>
        
        <div class="pagination">
            {% if page > 1 %}<a href="/?page={{ page - 1 }}&q={{ search_query }}">❮ PREV</a>{% endif %}
            {% if media_list|length == 20 %}<a href="/?page={{ page + 1 }}&q={{ search_query }}">NEXT ❯</a>{% endif %}
        </div>
    </div>

    <script>
        function deleteItem(id) {
            if(confirm("Are you sure you want to delete this?")) {
                fetch('/api/delete/' + id, { method: 'POST' })
                .then(response => window.location.reload());
            }
        }
        function renameItem(id, currentName) {
            let newName = prompt("Enter new name:", currentName);
            if(newName && newName !== currentName) {
                fetch('/api/rename/' + id, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: newName })
                }).then(response => window.location.reload());
            }
        }
    </script>
</body>
</html>
"""

# --- FLASK ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['role'] = 'admin'
            return redirect(url_for('home'))
        elif username == GUEST_USER and password == GUEST_PASS:
            session['role'] = 'user'
            return redirect(url_for('home'))
        else:
            error = "Invalid Credentials."
            
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'role' not in session:
        return redirect(url_for('login'))

    # Search & Pagination setup
    search_query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    per_page = 20
    skip = (page - 1) * per_page

    query_filter = {}
    if search_query:
        # Case-insensitive search in MongoDB
        query_filter = {"name": {"$regex": search_query, "$options": "i"}}

    media_list = list(collection.find(query_filter).sort("_id", -1).skip(skip).limit(per_page))
    
    return render_template_string(DASHBOARD_TEMPLATE, media_list=media_list, page=page, search_query=search_query)

# --- API ROUTES FOR ADMIN CONTROLS ---

@app.route('/api/delete/<item_id>', methods=['POST'])
def api_delete(item_id):
    if session.get('role') == 'admin':
        collection.delete_one({"_id": ObjectId(item_id)})
        return jsonify({"status": "success"})
    return jsonify({"status": "unauthorized"}), 403

@app.route('/api/rename/<item_id>', methods=['POST'])
def api_rename(item_id):
    if session.get('role') == 'admin':
        new_name = request.json.get('name')
        collection.update_one({"_id": ObjectId(item_id)}, {"$set": {"name": new_name}})
        return jsonify({"status": "success"})
    return jsonify({"status": "unauthorized"}), 403

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- BOT COMMANDS (Unchanged, keep your existing handle_message logic here) ---
# ... [Paste your existing bot.message_handler blocks here] ...

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    bot.polling(none_stop=True)
