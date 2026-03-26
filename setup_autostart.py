"""Настройка автозапуска бота через Windows Task Scheduler."""
import subprocess, sys

TASK_NAME = "SternVoiceBot"
PYTHON = sys.executable.replace("python.exe", "pythonw.exe")
SCRIPT = r"C:\Users\natam\Desktop\Skills\инструменты\tts-bot\tts_telegram_bot.py"

# Удалим старую задачу если есть
subprocess.run(["schtasks.exe", "/delete", "/tn", TASK_NAME, "/f"],
               capture_output=True)

# Создаём новую: запуск при входе в систему
result = subprocess.run([
    "schtasks.exe", "/create",
    "/tn", TASK_NAME,
    "/tr", f'"{PYTHON}" "{SCRIPT}"',
    "/sc", "onlogon",
    "/rl", "highest",
    "/f",
], capture_output=True, text=True)

print(result.stdout)
if result.returncode != 0:
    print("ОШИБКА:", result.stderr)
else:
    print("Автозапуск настроен!")

# Запускаем прямо сейчас
subprocess.run(["schtasks.exe", "/run", "/tn", TASK_NAME])
print("Бот запущен!")
