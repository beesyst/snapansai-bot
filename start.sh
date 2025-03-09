#!/bin/bash

CONFIG_FILE="config/config.json"
LANG_FILE="config/lang.json"
LOG_FILE="logs/bot.log"

# Остановка старых процессов
pkill -9 -f "python3 -m src.bot"
pkill -9 -f "python3 -m src.screenshot_sender"
sleep 2

# Функция обновления config.json
update_config() {
    jq "$1" "$CONFIG_FILE" > tmp.json && mv tmp.json "$CONFIG_FILE"
    sync
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

# Ввод bot_token
BOT_TOKEN=$(jq -r '.telegram.bot_token' "$CONFIG_FILE")
BOT_TOKEN_WAS_SET=false

while [[ "$BOT_TOKEN" == "null" || -z "$BOT_TOKEN" || ! "$BOT_TOKEN" =~ ^[0-9]+:[A-Za-z0-9_-]{35,}$ ]]; do
    echo "$(translate "🔔 Йо! Telegram Bot API token не найден! Забери в @BotFather и вбивай сюда:")"
    read -r TOKEN_INPUT
    if [[ "$TOKEN_INPUT" =~ ^[0-9]+:[A-Za-z0-9_-]{35,}$ ]]; then
        update_config ".telegram.bot_token = \"$TOKEN_INPUT\""
        echo "$(translate "✅ Telegram Bot API token красиво залетел в config.json!")"
        BOT_TOKEN="$TOKEN_INPUT"
        BOT_TOKEN_WAS_SET=true
    fi
done

if [ "$BOT_TOKEN_WAS_SET" = false ]; then
    echo "$(translate "✅ Telegram Bot API token найден!")"
fi

# Определение chat_id
CHAT_ID=$(jq -r '.telegram.chat_id' "$CONFIG_FILE")

if [[ "$CHAT_ID" == "null" || "$CHAT_ID" == "0" || -z "$CHAT_ID" ]]; then
    # Очищаем старые обновления только если chat_id не установлен
    echo "$(translate "🔔 Очищаю историю обновлений Telegram...")"
    LATEST_UPDATE_ID=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getUpdates" | jq '.result | map(.update_id) | max // empty')
    if [[ "$LATEST_UPDATE_ID" != "null" && -n "$LATEST_UPDATE_ID" ]]; then
        NEXT_OFFSET=$((LATEST_UPDATE_ID + 1))
        curl -s "https://api.telegram.org/bot$BOT_TOKEN/getUpdates?offset=$NEXT_OFFSET" > /dev/null
    fi

    # Инструкция пользователю
    echo "$(translate "🔔 Напиши /start в Telegram и возвращайся сюда!")"

    for i in {1..20}; do  # Ждем 100 секунд (по 5 секунд)
        UPDATES=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getUpdates?offset=-1")

        # Проверяем, есть ли новые обновления
        if [[ $(echo "$UPDATES" | jq '.result | length') -eq 0 ]]; then
            sleep 5
            continue
        fi

        # Извлекаем chat_id
        CHAT_ID=$(echo "$UPDATES" | jq -r '.result | map(select(.message.chat.id != null)) | last | .message.chat.id')

        if [[ "$CHAT_ID" != "null" && "$CHAT_ID" != "0" && -n "$CHAT_ID" ]]; then
            update_config ".telegram.chat_id = $CHAT_ID"
            echo "$(translate "✅ Chat ID определен:") $CHAT_ID. $(translate "И записан в config.json!")"

            # Отправляем уведомление в Telegram
            curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
                 -d "chat_id=$CHAT_ID" -d "text=🔔 Chat ID определен! Перейди снова в бота для дальнейшей установки." > /dev/null

            break
        fi

        sleep 5
    done

    if [[ -z "$CHAT_ID" || "$CHAT_ID" == "null" || "$CHAT_ID" == "0" ]]; then
        echo "$(translate "❌ Ошибка: chat_id не определен. Попробуй снова.")"
        exit 1
    fi
else
    echo "$(translate "✅ Chat ID найден!")"
fi

# Запрос AI API-ключа
API_KEY=$(jq -r '.openai.api_key' "$CONFIG_FILE")
while [[ "$API_KEY" == "null" || -z "$API_KEY" || ! "$API_KEY" =~ ^sk-[A-Za-z0-9_-]{30,}$ ]]; do
    echo "$(translate "🔔 Йо! Подкинь API key от ИИ сюда, плиз:")"
    read -r KEY_INPUT
    if [[ "$KEY_INPUT" =~ ^sk-[A-Za-z0-9_-]{30,}$ ]]; then
        update_config ".openai.api_key = \"$KEY_INPUT\""
        echo "$(translate "✅ API key по кайфу влетел в config.json!")"
        API_KEY="$KEY_INPUT"
    fi
done

# Определение ОС
OS_SETTING=$(jq -r '.screenshot.os' "$CONFIG_FILE")

if [[ "$OS_SETTING" == "auto" || "$OS_SETTING" == "null" || -z "$OS_SETTING" ]]; then
    UNAME_OUT="$(uname -s)"
    case "${UNAME_OUT}" in
        Linux*)     OS_TYPE="ubuntu";;
        Darwin*)    OS_TYPE="macos";;
        CYGWIN*|MINGW*) OS_TYPE="windows";;
        *)          OS_TYPE="unknown"
    esac
    update_config ".screenshot.os = \"$OS_TYPE\""
    echo "$(translate "💽 ОС спалена:") $OS_TYPE"
else
    echo "$(translate "✅ ОС определена!")"
    OS_TYPE="$OS_SETTING"
fi

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

# Запуск bot.py
nohup python3 -m src.bot > "$LOG_FILE" 2>&1 &
HOTKEY=$(jq -r '.screenshot.hotkey' "$CONFIG_FILE")
echo "$(translate "✅ Все четко! Жми") ${HOTKEY} $(translate "и скрин летит в Телегу.")"
