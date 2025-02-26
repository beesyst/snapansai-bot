#!/bin/bash

echo "🚀 Стартуем!"

CONFIG_FILE="config.json"

# Проверка Python3
echo "🔎 Чекаю есть ли Python3..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 где? Ставь по-быстрому и будет четко (sudo apt install python3)."
    exit 1
fi
echo "✅ Python3 найден!"

# Проверка наличия config.json
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Фейл — config.json куда-то слился!"
    exit 1
fi

# Функция обновления config.json
update_config() {
    jq "$1" "$CONFIG_FILE" > tmp.json && mv tmp.json "$CONFIG_FILE"
}

# Ввод bot_token через терминал
BOT_TOKEN=$(jq -r '.telegram.bot_token' "$CONFIG_FILE")
while [[ "$BOT_TOKEN" == "null" || -z "$BOT_TOKEN" ]]; do
    echo "🔔 Йо! Telegram Bot API token не найден! Забери в @BotFather и вбивай сюда:"
    read -r TOKEN_INPUT
    if [[ -n "$TOKEN_INPUT" ]]; then
        update_config ".telegram.bot_token = \"$TOKEN_INPUT\""
        echo "✅ Telegram Bot API token красиво залетел в config.json!"
        BOT_TOKEN="$TOKEN_INPUT"
    fi
done
echo "✅ Telegram Bot API token найден!"

# Определяем ОС
OS_SETTING=$(jq -r '.screenshot.os' "$CONFIG_FILE")
if [[ "$OS_SETTING" == "auto" || -z "$OS_SETTING" ]]; then
    UNAME_OUT="$(uname -s)"
    case "${UNAME_OUT}" in
        Linux*)     OS_TYPE=ubuntu;;
        Darwin*)    OS_TYPE=macos;;
        CYGWIN*|MINGW*) OS_TYPE=windows;;
        *)          OS_TYPE="unknown"
    esac
else
    OS_TYPE="$OS_SETTING"
fi
echo "💽 ОС спалена: $OS_TYPE"

if [[ "$OS_TYPE" == "unknown" ]]; then
    echo "❌ Ошибка: Чёт непонятная ОС. Подкинь параметр 'os' в config.json."
    exit 1
fi

# Скрытый сброс GTK_PATH для Ubuntu
if [[ "$OS_TYPE" == "ubuntu" ]]; then
    UNSET_CMD=$(jq -r ".screenshot.commands.$OS_TYPE.unset" "$CONFIG_FILE")
    if [[ "$UNSET_CMD" != "null" && -n "$UNSET_CMD" ]]; then
        eval "$UNSET_CMD" &> /dev/null
    fi
fi

# Проверка и установка скриншот-утилиты
CHECK_CMD=$(jq -r ".screenshot.commands.$OS_TYPE.check" "$CONFIG_FILE")
INSTALL_CMD=$(jq -r ".screenshot.commands.$OS_TYPE.install" "$CONFIG_FILE")

if ! eval "$CHECK_CMD" &> /dev/null; then
    echo "💾 Утилу для скринов не нашел — ща закину по-быстрому..."
    eval "$INSTALL_CMD"
    echo "✅ Утила засетапена!"
else
    echo "✅ Утилита для скринов уже засетапена!"
fi

# Виртуальное окружение
if [ ! -d "venv" ]; then
    echo "💾 Создаю виртуалочку..."
    python3 -m venv venv
    echo "✅ Виртуалочка поднята!"
fi
source venv/bin/activate

# Установка зависимостей
if [ ! -f "venv/installed.lock" ] || [ requirements.txt -nt venv/installed.lock ]; then
    echo "💾 Закидываю зависимости..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/installed.lock
    echo "✅ Зависимости подъехали!"
fi

# Остановка старых процессов
pkill -9 -f bot.py
pkill -9 -f screenshot_sender.py

# Получение chat_id
nohup python3 bot.py > bot.log 2>&1 &
sleep 5

CHAT_ID=$(jq -r '.telegram.chat_id' "$CONFIG_FILE")
if [[ "$CHAT_ID" == "0" || "$CHAT_ID" == "null" ]]; then
    echo "🔔 Йо! Залетай в Телегу и в боте жми /start! Жду..."
    until [[ "$CHAT_ID" != "0" && "$CHAT_ID" != "null" && -n "$CHAT_ID" ]]; do
        sleep 5
        CHAT_ID=$(jq -r '.telegram.chat_id' "$CONFIG_FILE")
    done
    echo "✅ chat_id четкий: $CHAT_ID"
fi

# Проверка api_key
API_KEY=$(jq -r '.openai.api_key' "$CONFIG_FILE")
while [[ "$API_KEY" == "null" || -z "$API_KEY" ]]; do
    echo "🔔 Йо! Подкинь API key от ИИ сюда, плиз:"
    read -r KEY_INPUT
    if [[ -n "$KEY_INPUT" ]]; then
        if [[ "$KEY_INPUT" == sk-* ]]; then
            update_config ".openai.api_key = \"$KEY_INPUT\""
            echo "✅ OpenAI ключ по кайфу влетел в config.json!"
            API_KEY="$KEY_INPUT"
        else
            update_config ".deepseek.api_key = \"$KEY_INPUT\""
            echo "✅ Deepseek ключ по кайфу влетел в config.json!"
            API_KEY="$KEY_INPUT"
        fi
    fi
done

# Запуск screenshot_sender.py
HOTKEY=$(jq -r '.screenshot.hotkey' "$CONFIG_FILE")
nohup python3 screenshot_sender.py >> bot.log 2>&1 &
echo "✅ Все четко! Жми ${HOTKEY} и скрин летит в Телегу."
