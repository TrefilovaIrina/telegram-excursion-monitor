FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY telegram_excursion_bot/ ./telegram_excursion_bot/

CMD ["python", "telegram_excursion_bot/bot.py"] 