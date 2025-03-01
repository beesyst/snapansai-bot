#!/bin/bash

CONFIG_FILE="config.json"
LANG_FILE="lang.json"

# Функция обновления config.json
update_config() {
    jq "$1" "$CONFIG_FILE" > tmp.json && mv tmp.json "$CONFIG_FILE"
}

# Запрос языка, если он не задан в config.json
LANG_SETTING=$(jq -r '.language' "$CONFIG_FILE")
while [[ "$LANG_SETTING" == "null" || -z "$LANG_SETTING" ]]; do
    echo "Select language: en, ru, de"
    read -r LANG_INPUT
    case "$LANG_INPUT" in
        en|ru|de)
            update_config ".language = \"$LANG_INPUT\""
            LANG_SETTING="$LANG_INPUT"
            ;;
    esac
done

# Функция перевода строк
translate() {
    local text="$1"
    jq -r --arg lang "$LANG_SETTING" --arg txt "$text" '.[$lang][$txt] // $txt' "$LANG_FILE"
}

echo "$(translate "🚀 Стартуем!")"

# Проверка Python3
echo "$(translate "🔎 Чекаю есть ли Python3...")"
if ! command -v python3 &> /dev/null; then
    echo "$(translate "❌ Python3 где? Ставь по-быстрому и будет четко (sudo apt install python3).")"
    exit 1
fi
echo "$(translate "✅ Python3 найден!")"

# Проверка наличия config.json
if [ ! -f "$CONFIG_FILE" ]; then
    echo "$(translate "❌ Фейл — config.json куда-то слился!")"
    exit 1
fi

# Ввод bot_token через терминал с проверкой формата
BOT_TOKEN=$(jq -r '.telegram.bot_token' "$CONFIG_FILE")
while [[ "$BOT_TOKEN" == "null" || -z "$BOT_TOKEN" || ! "$BOT_TOKEN" =~ ^[0-9]+:[A-Za-z0-9_-]{35,}$ ]]; do
    echo "$(translate "🔔 Йо! Telegram Bot API token не найден! Забери в @BotFather и вбивай сюда:")"
    read -r TOKEN_INPUT
    if [[ "$TOKEN_INPUT" =~ ^[0-9]+:[A-Za-z0-9_-]{35,}$ ]]; then
        update_config ".telegram.bot_token = \"$TOKEN_INPUT\""
        echo "$(translate "✅ Telegram Bot API token красиво залетел в config.json!")"
        BOT_TOKEN="$TOKEN_INPUT"
    fi
done
echo "$(translate "✅ Telegram Bot API token найден!")"

# Определяем ОС
OS_SETTING=$(jq -r '.screenshot.os' "$CONFIG_FILE")
if [[ "$OS_SETTING" == "auto" || -z "$OS_SETTING" ]]; then
    UNAME_OUT="$(uname -s)"
    case "${UNAME_OUT}" in
        Linux*)     OS_TYPE="ubuntu";;
        Darwin*)    OS_TYPE="macos";;
        CYGWIN*|MINGW*) OS_TYPE="windows";;
        *)          OS_TYPE="unknown"
    esac
    jq --arg os "$OS_TYPE" '.screenshot.os = $os' "$CONFIG_FILE" > tmp.json && mv tmp.json "$CONFIG_FILE"
else
    OS_TYPE="$OS_SETTING"
fi

echo "$(translate "💽 ОС спалена:") $OS_TYPE"


if [[ "$OS_TYPE" == "unknown" ]]; then
    echo "$(translate "❌ Ошибка: Чёт непонятная ОС. Подкинь параметр 'os' в config.json.")"
    exit 1
fi

# Скрытый сброс
UNSET_CMD=$(jq -r ".screenshot.commands.$OS_TYPE.unset" "$CONFIG_FILE")
if [[ "$UNSET_CMD" != "null" && -n "$UNSET_CMD" ]]; then
    eval "$UNSET_CMD" &> /dev/null
fi

# Проверка и установка скриншот-утилиты
CHECK_CMD=$(jq -r ".screenshot.commands.$OS_TYPE.check" "$CONFIG_FILE")
INSTALL_CMD=$(jq -r ".screenshot.commands.$OS_TYPE.install" "$CONFIG_FILE")

if ! eval "$CHECK_CMD" &> /dev/null; then
    echo "$(translate "💾 Утилу для скринов не нашел — ща закину по-быстрому...")"
    eval "$INSTALL_CMD"
    echo "$(translate "✅ Утила засетапена!")"
else
    echo "$(translate "✅ Утилита для скринов уже засетапена!")"
fi

# Виртуальное окружение
if [ ! -d "venv" ]; then
    echo "$(translate "💾 Создаю виртуалочку...")"
    python3 -m venv venv
    echo "$(translate "✅ Виртуалочка поднята!")"
fi
source venv/bin/activate

# Установка зависимостей
if [ ! -f "venv/installed.lock" ] || [ requirements.txt -nt venv/installed.lock ]; then
    echo "$(translate "💾 Закидываю зависимости...")"
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/installed.lock
    echo "$(translate "✅ Зависимости подъехали!")"
fi

# Остановка старых процессов
pkill -9 -f bot.py
pkill -9 -f screenshot_sender.py

# Запуск bot.py
nohup python3 bot.py > bot.log 2>&1 &
sleep 5

# Получение chat_id
CHAT_ID=$(jq -r '.telegram.chat_id' "$CONFIG_FILE")
if [[ "$CHAT_ID" == "0" || "$CHAT_ID" == "null" ]]; then
    echo "$(translate "🔔 Йо! Залетай в Телегу и в боте жми /start! Жду...")"
    until [[ "$CHAT_ID" != "0" && "$CHAT_ID" != "null" && -n "$CHAT_ID" ]]; do
        sleep 5
        CHAT_ID=$(jq -r '.telegram.chat_id' "$CONFIG_FILE")
    done
    echo "$(translate "✅ chat_id четкий:") $CHAT_ID"
fi

# Проверка API-ключа OpenAI и DeepSeek
API_KEY=$(jq -r '.openai.api_key' "$CONFIG_FILE")
while [[ "$API_KEY" == "null" || -z "$API_KEY" || ! "$API_KEY" =~ ^sk-[A-Za-z0-9_-]{30,}$ ]]; do
    echo "$(translate "🔔 Йо! Подкинь API key от ИИ сюда, плиз:")"
    read -r KEY_INPUT
    if [[ "$KEY_INPUT" =~ ^sk-[A-Za-z0-9_-]{30,}$ ]]; then
        update_config ".openai.api_key = \"$KEY_INPUT\""
        echo "$(translate "✅ OpenAI/DeepSeek ключ по кайфу влетел в config.json!")"
        API_KEY="$KEY_INPUT"
    fi
done

# Запуск screenshot_sender.py
nohup python3 screenshot_sender.py >> bot.log 2>&1 &
HOTKEY=$(jq -r '.screenshot.hotkey' "$CONFIG_FILE")
echo "$(translate "✅ Все четко! Жми") ${HOTKEY} $(translate "и скрин летит в Телегу.")"
