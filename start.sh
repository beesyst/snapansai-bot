#!/bin/bash

echo "🚀 Запуск"

CONFIG_FILE="config.json"

# 🔹 Проверка Python3
echo "🔎 Проверка наличия Python3..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден! Установите Python3 (пример для Ubuntu: sudo apt install python3 python3-venv python3-pip)."
    exit 1
fi
echo "✅ Python3 найден!"

# 🔹 Проверка config.json
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Ошибка: config.json не найден!"
    exit 1
fi

BOT_TOKEN=$(jq -r '.telegram.bot_token' "$CONFIG_FILE")
if [[ "$BOT_TOKEN" == "null" || -z "$BOT_TOKEN" ]]; then
    echo "❌ Ошибка: bot_token не найден в config.json! Инструкция:"
    echo "   1. Перейди в @BotFather в Telegram."
    echo "   2. Введи команду /newbot и следуй инструкциям."
    echo "   3. Скопируй полученный токен и добавь его в config.json в bot_token."
    echo "   4. В созданном Telegram-боте нажми /start."
    exit 1
fi
echo "✅ bot_token найден!"

# 🔹 Определяем ОС
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
echo "🖥️ Определена ОС: $OS_TYPE"

if [[ "$OS_TYPE" == "unknown" ]]; then
    echo "❌ Ошибка: Неизвестная ОС. Укажите параметр 'os' в config.json."
    exit 1
fi

# 🔹 Скрытый сброс GTK_PATH для Ubuntu
if [[ "$OS_TYPE" == "ubuntu" ]]; then
    UNSET_CMD=$(jq -r ".screenshot.commands.$OS_TYPE.unset" "$CONFIG_FILE")
    if [[ "$UNSET_CMD" != "null" && -n "$UNSET_CMD" ]]; then
        eval "$UNSET_CMD" &> /dev/null
    fi
fi

# 🔹 Проверка и установка скриншот-утилиты
CHECK_CMD=$(jq -r ".screenshot.commands.$OS_TYPE.check" "$CONFIG_FILE")
INSTALL_CMD=$(jq -r ".screenshot.commands.$OS_TYPE.install" "$CONFIG_FILE")

if ! eval "$CHECK_CMD" &> /dev/null; then
    echo "🔹 Утилита для скриншотов не найдена. Выполняю установку..."
    eval "$INSTALL_CMD"
    echo "✅ Утилита установлена!"
else
    echo "✅ Утилита для скриншотов уже установлена."
fi

# 🔹 Виртуальное окружение
if [ ! -d "venv" ]; then
    echo "🔹 Создаю виртуальное окружение..."
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано!"
fi
source venv/bin/activate

# 🔹 Установка зависимостей
if [ ! -f "venv/installed.lock" ] || [ requirements.txt -nt venv/installed.lock ]; then
    echo "🔹 Устанавливаю зависимости..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/installed.lock
    echo "✅ Зависимости установлены!"
fi

# 🔹 Остановка старых процессов
pkill -f bot.py
pkill -f screenshot_sender.py

# 🔹 Запуск bot.py
nohup python3 bot.py > bot.log 2>&1 &
sleep 3

CHAT_ID=$(jq -r '.telegram.chat_id' "$CONFIG_FILE")
if [[ "$CHAT_ID" != "null" && "$CHAT_ID" != "" && "$CHAT_ID" != "0" ]]; then
    echo "✅ Бот запущен! chat_id: $CHAT_ID"
    # 🔹 Динамическое отображение горячей клавиши
    HOTKEY=$(jq -r '.screenshot.hotkey' "$CONFIG_FILE")
    nohup python3 screenshot_sender.py > sender.log 2>&1 &
    echo "✅ Всё готово! Используйте горячую клавишу: ${HOTKEY} для отправки скриншота."
else
    echo "⚠️  Ты забыл нажать /start в созданном боте. 📩"
fi
