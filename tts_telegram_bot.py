"""
Telegram-бот для озвучки текста голосом Якова Борисовича (ElevenLabs).
Работает на Render.com (бесплатно) через webhook.
"""

import os
import io
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv(Path(__file__).parent / ".env")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
VOICE_ID = "ZGrbqCZtSzXfcK2bXLPd"
MODEL_ID = "eleven_multilingual_v2"
PORT = int(os.getenv("PORT", 10000))
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL", "https://stern-voice-bot.onrender.com")
ALLOWED_USERS: list[int] = []

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)


def voice_text(text: str) -> bytes:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    response = client.text_to_speech.convert(
        text=text, voice_id=VOICE_ID, model_id=MODEL_ID,
        voice_settings=VoiceSettings(
            stability=0.75, similarity_boost=1.0,
            style=0.0, use_speaker_boost=True,
        ),
    )
    return b"".join(chunk for chunk in response)


def is_allowed(user_id: int) -> bool:
    return not ALLOWED_USERS or user_id in ALLOWED_USERS


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

    await update.message.reply_voice(
        voice=io.BytesIO(audio),
        caption=f"{len(text)} симв. / {size_kb:.0f} КБ",
    )

    buf = io.BytesIO(audio)
    buf.name = "voice.mp3"
    await update.message.reply_document(
        document=buf, caption="MP3 для скачивания",
    )


def main():
    if not TELEGRAM_BOT_TOKEN or not ELEVENLABS_API_KEY:
        log.error("Нет ключей!")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    webhook_url = f"{WEBHOOK_URL}/webhook"
    log.info(f"Starting webhook: {webhook_url} on port {PORT}")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=webhook_url,
        url_path="/webhook",
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.exception(f"Бот упал: {e}")
