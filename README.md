# 📸 SnapAnsAI Bot

## 📌 Project Description

**SnapAnsAI Bot** is a tool for instant answers based on screenshots. The user presses a hotkey, and the screenshot is automatically sent to a Telegram bot, which analyzes the image using **OpenAI API** and returns a text response.

## ⚙️ Key Features

✅ **Hotkeys** — automatic screenshot capture (multiple combinations can be set in `config.json`).  
✅ **Automatic image sending** to the Telegram bot.  
✅ **AI Selection** — support for **OpenAI** for image processing.  
✅ **Flexible settings** in `config.json` (change API, hotkeys, OS, etc.).  
✅ **Cross-platform**: **Windows, Linux, macOS** (auto-detection of OS).  
✅ **Logging** in `bot.log` for easy debugging (all errors and events are recorded in the log).  
✅ **Multilingual support** — the bot supports **language switching** via `config.json` and adding new languages in `lang.json`.

## 🌍 Where It Can Be Used

📚 **Education:** Screenshots of tasks and instant explanations.  
🌝 **Work:** Capturing important on-screen data and quick analysis.  
🧫 **Research:** Extracting text from charts and documents.  
💬 **Communication:** Processing text and images in real time.  
🏃 **Daily use:** Quickly obtaining text from any screen.  
🔍 **Proctoring:** ?

## 🛠️ Technology Stack

🐍 **Python** — main programming language.  
🤖 **Telegram Bot API** — interaction with the bot.  
🧠 **OpenAI API** — image and text processing.  
🖥️ **PyAutoGUI** — screenshot capture (Windows).  
🐧 **gnome-screenshot** — screenshot capture (Ubuntu).  
🍏 **screencapture** — screenshot capture (macOS).  
⌨️ **pynput** — hotkey handler.  
🔗 **Requests** — interaction with APIs.  
📃 **Logging** — logging system.

### 🔐 Integrated Modules:
- [`flameshot`](https://github.com/flameshot-org/flameshot/) — a screenshot tool

## 🧷 Architecture

SnapAnsAI Bot consists of several components:

📌 **System Components:**

1️⃣ **Telegram Bot** — receives AI-processed messages from the bot.  
2️⃣ **AI Processing Module** — sends images to OpenAI or DeepSeek and retrieves a response.  
3️⃣ **Screenshot Capture Module** — operates via PyAutoGUI, `gnome-screenshot`, `flameshot`, or `screencapture`.  
4️⃣ **Logging Module** — records all events and errors in `bot.log`.  
5️⃣ **Configuration Module** — loads and manages `config.json`.

### **🗂️ Project Structure**

```
snapansai-bot/
│── config/                   # Configuration files
│   ├── config.json           # Configuration file
│   ├── lang.json             # Translation file for multilingual support
│── logs/                     # Logs
│   │── session_temp/         # Temporary files (screenshots and cache)
│   ├── bot.log               # Bot log file
│── methods/                  # Screenshot processing modules
│   ├── flameshot.py          # Screenshot handler via flameshot
│── src/                      # Project source code
│   ├── ai_api.py             # AI API handler
│   ├── bot.py                # Main Telegram bot
│   ├── config_handler.py     # Configuration management (loading, saving)
│   ├── screenshot_sender.py  # Screenshot sending script
│── test/                     # AI testing scripts
│   ├── test_ai.py            # Project launch script
│── venv/                     # Virtual environment
│── README.md                 # Project documentation
│── requirements.txt          # Dependencies file
│── start.sh                  # Project launch script
```

## ⚙️ How It Works?

🔹 **System Startup**:
1. The bot starts with `start.sh`.
2. Initializes the Telegram Bot API token.
3. Initializes the Chat ID.
4. Initializes the AI API Key.
5. Detects the user's OS (Windows/Linux/macOS).
6. Loads configuration from `config.json`.
7. Launches the hotkey handler.
8. Waits for a hotkey press (`alt+s`, `ctrl+m`, etc.).

🔹 **Screenshot Processing**:
1. When a hotkey is pressed, a screenshot is taken and saved in the temporary folder `logs/session_temp/`.
2. The image is sent to the AI server for analysis.
3. The received text response is sent to the Telegram bot.
4. The screenshot is deleted from the temporary folder.

🔹 **Using `flameshot`**:
- If `flameshot` is used, the save path can be set in the configuration.
- To disable pop-up notifications about saving, run:
```
flameshot config
```
and uncheck `Show desktop notifications` in the General tab.

## 🛠️ Installation & Launch

### 🔄 Launching the Project

```bash
bash start.sh
```

During installation, you will need to provide the API key for the Telegram bot and AI. After installation, you can press the hotkeys, and screenshots will be processed by AI and sent to the Telegram bot.

### 🔄 Configuration Setup

In `config.json`, you can edit:

- `"bot_token": ""` - Telegram Bot API token
- `"chat_id": 0` - Telegram Chat ID (auto-detection)
- `"language": ""` - Language (available: en, ru, de)
- `"api_key": ""` - AI API key (available: OpenAI, DeepSeek)
- `"model": ""` - AI model (OpenAI: gpt-4o-mini, gpt-4o, o3-mini, gpt-4.5-preview, etc.)
- `"hotkey": ""` - Hotkeys (you can specify one or more, e.g., `"hotkey": "alt+s, ctrl+m, p, /"`)
- `"os": ""` - OS (auto-detection)
- `"method":` - Default is "default" — built-in OS screenshot managers are used. Available: `"flameshot"`.

In `lang.json`, you can edit:

- `"prompt": ""` - Prompt
- Add other languages

## **💀 Roadmap**

✅ **Improved hotkey processing**  
✅ **Integration with OpenAI**  
✅ **Tested on Ubuntu 24.04 (Wayland)**  
✅ **Flexible configuration via `config.json`**  
✅ **Added `flameshot` as an alternative method**  
🔜 **Testing on Windows, MacOS**  
🔜 **Adding Docker**  
🔜 **Integration with other AI models (DeepSeek, Claude, Gemini, etc.)**

## 💰 Donations

- **USDT (TRC20)**/**USDC (TRC20)**: `TUQj3sguQjmKFJEMotyb3kERVgnfvhzG7o`
- **SOL (Solana)**: `6VA9oJbkszteTZJbH6mmLioKTSq4r4E3N1bsoPaxQgr4`
- **XRP (XRP)**: `rDkEZehHFqSjiGdBHsseR64fCcRXuJbgfr`

---

**✨ Designed for convenience and quick access to answers.**