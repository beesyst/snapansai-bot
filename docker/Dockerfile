# Используем официальный образ Python 3.13.2
FROM python:3.13.2

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта
COPY ../requirements.txt /app/requirements.txt
COPY ../src /app/src
COPY ../config /app/config

# Устанавливаем зависимости
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Запускаем бота
CMD ["python3", "-m", "src.bot"]
