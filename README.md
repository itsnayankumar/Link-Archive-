# 🎬 Neon Drive Media Archive

A fully automated, dark-themed media indexer and Telegram bot. This application allows you to forward media links to a Telegram bot, which automatically parses, cleans, and stores them in a MongoDB cluster. The data is then served on a responsive, neon-styled web dashboard.

## ✨ Features
- **Zero-Touch Link Parsing:** Automatically extracts Name, Size, Download, and Watch links from raw text.
- **Incognito Mode:** Toggle `/incognito` in the bot to auto-delete your forwarded messages after saving, keeping your chat perfectly clean.
- **Smart Filename Cleaning:** Automatically strips out promotional tags and normalizes titles to a clean `Title Year Quality` format.
- **Neon Web Dashboard:** A futuristic, glassmorphism UI to browse your archive.
- **Role-Based Access:** Dual-tier login system (Admin and Guest) to protect your links.
- **Admin Web Controls:** Rename or delete entries directly from the web interface.
- **Search & Pagination:** Instantly search your entire MongoDB database and load results efficiently.

## 🛠️ Tech Stack
- **Backend:** Python 3.10, Flask
- **Bot Framework:** pyTelegramBotAPI (Telebot)
- **Database:** MongoDB Atlas
- **Hosting:** Render (Docker / Web Service)

## 🚀 Setup & Deployment

### 1. Prerequisites
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- A free MongoDB Atlas Cluster (M0 Sandbox)
- A GitHub account and a Render account

### 2. Environment Variables
To deploy this successfully on Render, you must configure the following Environment Variables in your Web Service settings:

| Key | Description | Example |
| :--- | :--- | :--- |
| `BOT_TOKEN` | Your Telegram Bot Token | `123456789:ABCDefgh...` |
| `MONGO_URI` | Your MongoDB connection string | `mongodb+srv://<user>:<pass>@cluster0...` |
| `SECRET_KEY` | A random string for Flask sessions | `neon_drive_secure_2026` |
| `ADMIN_USER` | Dashboard Admin Username | `admin` |
| `ADMIN_PASS` | Dashboard Admin Password | `admin123` |
| `GUEST_USER` | Dashboard Guest Username | `user` |
| `GUEST_PASS` | Dashboard Guest Password | `watch123` |

*(Note: Render automatically provides the `PORT` variable, so you do not need to set it manually.)*

### 3. Required Files
Ensure your repository contains the following files before deploying:
- `main.py` (The main application code)
- `requirements.txt` (Dependencies)
- `Dockerfile` (Container configuration for Render)

### 4. Bot Commands
Once deployed, interact with your bot using these commands:
- `/start` or `/help` - View the help menu
- `/incognito` - Toggle message self-destruction
- `/list` - View the last 5 database entries and their IDs
- `/delete <ID>` - Manually delete an entry via the bot

---
*Maintained by @itsnayankumar | Encrypted via MongoDB*
