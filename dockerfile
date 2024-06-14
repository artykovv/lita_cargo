FROM python:3.9

RUN mkdir /api
WORKDIR /api

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Добавляем задержку на 10 секунд для того, чтобы дать время файлам полностью скопироваться
RUN sleep 10

# Продолжаем сборку и настройку
RUN chmod a+x api/docker/one.sh

CMD ["/api/docker/one.sh"]
