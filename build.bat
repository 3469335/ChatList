@echo off
echo ========================================
echo ChatList - Сборка исполняемого файла
echo ========================================
echo.

echo Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo Ошибка при установке зависимостей!
    pause
    exit /b 1
)

echo.
echo Сборка исполняемого файла...
pyinstaller PyQtApp.spec
if errorlevel 1 (
    echo Ошибка при сборке!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Готово! Исполняемый файл находится в папке dist\ChatList.exe
echo ========================================
echo.
echo Не забудьте создать файл .env с вашими API ключами!
pause

