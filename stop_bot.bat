@echo off
taskkill /f /im python.exe /fi "WINDOWTITLE eq *tts_telegram*" >nul 2>&1
:: На случай если по имени не найдёт — убиваем по командной строке
wmic process where "commandline like '%%tts_telegram_bot%%'" call terminate >nul 2>&1
echo Бот остановлен.
pause
