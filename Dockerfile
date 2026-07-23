FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Kyiv

WORKDIR /app

RUN apt-get update && apt-get install -y cron tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY batch_runner_cron.sh /app/batch_runner_cron.sh
RUN chmod +x /app/batch_runner_cron.sh

RUN mkdir -p /app/logs

RUN echo "0 * * * * /app/batch_runner_cron.sh >> /app/logs/cron.log 2>&1" > /etc/cron.d/news_batch_cron && \
    chmod 0644 /etc/cron.d/news_batch_cron && \
    crontab /etc/cron.d/news_batch_cron

CMD ["sh", "-c", "cron && python3 -m src.bot.main"]