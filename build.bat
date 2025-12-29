@echo off
echo Установка зависимостей...
pip install -r requirements.txt

echo.
echo Сборка исполняемого файла...
pyinstaller PyQtApp.spec

echo.
echo Готово! Исполняемый файл находится в папке dist\PyQtApp.exe
pause

