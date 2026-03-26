@echo off
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\stern_bot_hidden.vbs" >nul 2>&1
del "%APPDATA%\stern_bot_hidden.vbs" >nul 2>&1
wmic process where "commandline like '%%tts_telegram_bot%%'" call terminate >nul 2>&1
echo Бот удалён из автозапуска и остановлен.
pause
