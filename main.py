import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # Look for media files
    valid_exts = ('.mkv', '.mp4', '.avi', '.webm')
    files = [f for f in os.listdir('.') if f.lower().endswith(valid_exts)]
    
    # Build a simple HTML webpage
    html = "<h1>🎬 My Media Server</h1>"
    
    if not files:
        html += "<p>No media files found in the directory right now.</p>"
    else:
        html += "<ul>"
        for f in files:
            html += f"<li>{f}</li>"
        html += "</ul>"
        
    return html

if __name__ == "__main__":
    # Render requires web services to bind to host 0.0.0.0
    # and usually uses a dynamic PORT environment variable.
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
