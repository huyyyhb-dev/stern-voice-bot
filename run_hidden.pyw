"""Запускает бота. .pyw = без окна на Windows."""
import runpy, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.argv = [os.path.join(os.path.dirname(__file__), "tts_telegram_bot.py")]
runpy.run_path("tts_telegram_bot.py", run_name="__main__")
