# Быстрый старт: Публикация на GitHub

## 🚀 За 5 минут до релиза

### 1. Обновите версию
```bash
# Отредактируйте version.py
__version__ = "1.0.1"  # Новая версия
```

### 2. Соберите и создайте инсталлятор
```bash
build.bat
create_installer.bat
```

### 3. Создайте тег и отправьте на GitHub
```bash
git add .
git commit -m "Release v1.0.1"
git tag v1.0.1
git push origin main
git push origin v1.0.1
```

### 4. Создайте Release на GitHub
1. Перейдите: https://github.com/YOUR_USERNAME/YOUR_REPO/releases/new
2. Выберите тег `v1.0.1`
3. Заголовок: `ChatList v1.0.1`
4. Загрузите: `installer/ChatList-Setup-1.0.1.exe`
5. Нажмите "Publish release"

### 5. Настройте GitHub Pages (один раз)
1. Settings → Pages
2. Source: `Deploy from a branch`
3. Branch: `main`, Folder: `/docs`
4. Сохраните

Готово! 🎉

---

**Подробная инструкция:** [RELEASE.md](RELEASE.md)
