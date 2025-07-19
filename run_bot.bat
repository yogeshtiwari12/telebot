@echo off
echo 🤖 Starting Dating Bot...
echo.
echo 🔹 Make sure you have configured your bot token!
echo 🔹 If not configured, run: python setup.py
echo.
echo Starting bot in 3 seconds...
timeout /t 3 /nobreak >nul
echo.
python bot.py
pause
