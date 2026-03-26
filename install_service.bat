@echo off
echo Создаю автозапуск бота "Озвучка Штерн"...

:: Создаём VBS-скрипт, который запускает бота СКРЫТО (без окна)
echo Set WshShell = CreateObject("WScript.Shell") > "%APPDATA%\stern_bot_hidden.vbs"
echo WshShell.Run "cmd /c cd /d C:\Users\natam\Desktop\Skills\инструменты\tts-bot && python tts_telegram_bot.py", 0, False >> "%APPDATA%\stern_bot_hidden.vbs"

:: Копируем VBS в автозагрузку
copy "%APPDATA%\stern_bot_hidden.vbs" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\stern_bot_hidden.vbs" >nul

:: Запускаем прямо сейчас
start "" wscript "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\stern_bot_hidden.vbs"

echo.
echo ГОТОВО! Бот теперь:
echo  - Работает прямо сейчас (без окна)
echo  - Будет запускаться автоматически при включении компьютера
echo.
echo Чтобы ОСТАНОВИТЬ: запусти stop_bot.bat
echo Чтобы УДАЛИТЬ из автозапуска: запусти uninstall_service.bat
pause
