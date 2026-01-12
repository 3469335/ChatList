#!/bin/bash
echo "Установка зависимостей..."
pip install -r requirements.txt

echo ""
VERSION=$(python -c "import version; print(version.__version__)")
echo "Сборка исполняемого файла версии $VERSION..."
pyinstaller PyQtApp.spec

echo ""
echo "Готово! Исполняемый файл находится в папке dist/ChatList-v${VERSION}"

