#!/bin/bash
echo "Установка зависимостей..."
pip install -r requirements.txt

echo ""
echo "Сборка исполняемого файла..."
pyinstaller --onefile --windowed --name "PyQtApp" --icon=NONE main.py

echo ""
echo "Готово! Исполняемый файл находится в папке dist/PyQtApp"

