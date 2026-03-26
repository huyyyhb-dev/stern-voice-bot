"""
Telegram-бот для озвучки текста голосом Якова Борисовича (ElevenLabs).
Отправляешь текст — получаешь аудио. Не нравится — отправляешь снова.

Настройка:
1. pip install python-telegram-bot elevenlabs
2. Создай бота через @BotFather, получи токен
3. Впиши токен в .env (TELEGRAM_BOT_TOKEN=...)
4. python tts_telegram_bot.py
"""

import os
import io
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Настройки ---
SCRIPT_DIR = Path(__file__).parent
os.chdir(SCRIPT_DIR)
load_dotenv(SCRIPT_DIR / ".env")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
VOICE_ID = "ZGrbqCZtSzXfcK2bXLPd"  # Яков Борисович итоговый
MODEL_ID = "eleven_multilingual_v2"

# Кто может пользоваться ботом (Telegram user ID). Пустой список = все.
# Узнать свой ID: отправь /start боту @userinfobot
ALLOWED_USERS: list[int] = []

LOG_FILE = Path(__file__).parent / "bot.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def voice_text(text: str) -> bytes:
    """Озвучивает текст через ElevenLabs, возвращает MP3 bytes."""
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    response = client.text_to_speech.convert(
        text=text,
        voice_id=VOICE_ID,
        model_id=MODEL_ID,
        voice_settings=VoiceSettings(
            stability=0.3,
            similarity_boost=0.75,
            style=0.7,
            use_speaker_boost=True,
        ),
    )

    # response — генератор байтов
    audio = b"".join(chunk for chunk in response)
    return audio


def is_allowed(user_id: int) -> bool:
    if not ALLOWED_USERS:
        return True
    return user_id in ALLOWED_USERS


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь текст — я озвучу голосом Якова Борисовича.\n\n"
        "Не понравилось — отправь тот же текст ещё раз.\n"
        "Понравилось — просто сохрани аудио."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        await update.message.reply_text("Нет доступа.")
        return

    text = update.message.text.strip()
    if not text:
        return

    if len(text) > 5000:
        await update.message.reply_text(
            f"Текст слишком длинный ({len(text)} символов). Максимум 5000."
        )
        return

    msg = await update.message.reply_text("Озвучиваю...")
    log.info(f"[{user.first_name}] {len(text)} символов")

    try:
        audio = voice_text(text)
    except Exception as e:
        log.error(f"Ошибка: {e}")
        await msg.edit_text(f"Ошибка озвучки: {e}")
        return

    size_kb = len(audio) / 1024
    await msg.delete()

    # Отправляем как голосовое (можно прослушать прямо в чате)
    await update.message.reply_voice(
        voice=io.BytesIO(audio),
        caption=f"{len(text)} симв. / {size_kb:.0f} КБ",
    )

    # И как файл (чтобы скачать MP3)
    buf = io.BytesIO(audio)
    buf.name = "voice.mp3"
    await update.message.reply_document(
        document=buf,
        caption="MP3 для скачивания",
    )


def main():
    if not TELEGRAM_BOT_TOKEN:
        log.error("Нет TELEGRAM_BOT_TOKEN в .env")
        return

    if not ELEVENLABS_API_KEY:
        log.error("Нет ELEVENLABS_API_KEY в .env")
        return

    log.info("Бот запущен! Отправь текст в Telegram.")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.exception(f"Бот упал: {e}")
