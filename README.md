# 📸 SnapAnsAI Bot

## 📌 Project Description

**SnapAnsAI Bot** is a tool for instant answers based on screenshots. The user presses a hotkey, and the screenshot is automatically sent to a Telegram bot, which analyzes the image using **OpenAI API** and other services, then returns a text response.

## ⚙️ Key Features

✅ **Hotkeys** — automatic screenshot capture (multiple key combinations can be set in `config.json`).

✅ **Automatic sending** of images to the Telegram bot.

✅ **AI selection** — supports **OpenAI** and **DeepSeek** for image processing.

✅ **Flexible settings** in `config.json` (modify API, hotkeys, OS settings, etc.).

✅ **Cross-platform compatibility**: **Windows, Linux, macOS** (automatic OS detection).

✅ **Logging** in `bot.log` for debugging (all errors and events are recorded in the log).

✅ **Multilingual support** — the bot allows **language switching** via `config.json` and adding new languages in `lang.json`.

## 🌍 Use Cases

📚 **Education:** Screenshots of assignments and instant explanations.

💼 **Work:** Capturing important data from the screen and quick analysis.

🧪 **Research:** Extracting text from charts and documents.

💬 **Communication:** Processing texts and images in real-time.

🏃 **Everyday use:** Quickly getting text from any screen.

🔍 **Proctoring:** ?

## 🛠️ Tech Stack

🐍 **Python** — main programming language.

🤖 **Telegram Bot API** — bot interaction.

🧠 **OpenAI API / DeepSeek API** — image and text processing.

🖥️ **PyAutoGUI** — screenshot capture (Windows).

🐧 **gnome-screenshot** — screenshot capture (Ubuntu).

🍏 **screencapture** — screenshot capture (macOS).

⌨️ **pynput** — hotkey handler.

🔗 **Requests** — API interaction.

📜 **Logging** — logging system.

## 📂 Project Structure

``` 
snapansai-bot/
│── config/                   # Configuration files
│   ├── config.json           # Config file
│   ├── lang.json             # Translation file for multilingual support
│── logs/                     # Logs
│   │── session_temp/         # Temporary files (screenshots and cache)
│   ├── bot.log               # Bot log file
│── src/                      # Source code
│   ├── ai_api.py             # AI API handler
│   ├── bot.py                # Main Telegram bot
│   ├── config_handler.py     # Configuration management (loading, saving)
│   ├── screenshot_sender.py  # Screenshot sending script
│── test/                     # AI testing script
│   ├── test_ai.py            # Test script for the project
│── venv/                     # Virtual environment
│── README.md                 # Project documentation
│── requirements.txt          # Dependencies file
│── start.sh                  # Project startup script
```

## 🔧 Installation & Setup

### 🔄 Running the project

```bash
bash start.sh
```

During setup, you will need to specify:

- Telegram Bot token
- OpenAI (DeepSeek) API key

After setup, press the assigned hotkeys, and screenshots will be sent to the Telegram bot for AI processing.

### 🔄 Configuration

In `config.json`, you can modify:

- `"bot_token": ""` - Telegram Bot API token
- `"chat_id": 0` - Telegram Chat ID (auto-detected)
- `"language": ""` - Language (available: en, ru, de)
- `"api_key": ""` - AI API key (supports OpenAI, DeepSeek)
- `"hotkey": ""` - Hotkeys (one or multiple, e.g., `"hotkey": "alt+s, ctrl+m, p, /"`).
- `"os": ""` - OS (auto-detected)

In `lang.json`, you can modify:

- `"prompt": ""` - AI prompt
- Add new languages

## 📌 Future Improvements

- Testing has been conducted ONLY with OpenAI. Need to test with DeepSeek API.
- Tested ONLY on Ubuntu 24.04.2 LTS (Wayland). Need to check compatibility with Windows, macOS, and other Linux distributions.

💡 If you want to contribute to testing or improvements, I’d be happy to collaborate!

## 💰 Donate

- **USDT (TRC20)**/**USDC (TRC20)**: `TUQj3sguQjmKFJEMotyb3kERVgnfvhzG7o`
- **SOL (Solana)**: `6VA9oJbkszteTZJbH6mmLioKTSq4r4E3N1bsoPaxQgr4`
- **XRP (XRP)**: `rDkEZehHFqSjiGdBHsseR64fCcRXuJbgfr`

---

**✨ Designed for convenience and quick access to answers.**
