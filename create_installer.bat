@echo off
echo ========================================
echo ChatList - Создание инсталлятора
echo ========================================
echo.

REM Использование Python скрипта для создания инсталлятора
python create_installer.py

if errorlevel 1 (
    echo.
    echo Ошибка при создании инсталлятора!
    pause
    exit /b 1
)

pause
