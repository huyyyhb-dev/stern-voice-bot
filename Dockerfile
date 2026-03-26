FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY tts_telegram_bot.py .
CMD ["python", "tts_telegram_bot.py"]
