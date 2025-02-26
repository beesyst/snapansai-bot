import json

with open("config.json", "r") as f:
    config = json.load(f)

TELEGRAM_TOKEN = config["telegram"]["bot_token"]
CHAT_ID = config["telegram"]["chat_id"]
OPENAI_API_KEY = config["openai"]["api_key"]
OPENAI_MODEL = config["openai"].get("model", "gpt-4o-mini")
