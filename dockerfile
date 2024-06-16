# Используем базовый образ Python
FROM python:3.9

# Создаем директорию для приложения
RUN mkdir /api
WORKDIR /api

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем все файлы в рабочую директорию
COPY . .

# Добавляем задержку на 10 секунд для того, чтобы дать время файлам полностью скопироваться
RUN sleep 10

# Устанавливаем исполняемые права на скрипт
RUN chmod +x one.sh

# Устанавливаем команду запуска по умолчанию
CMD ["./one.sh"]
