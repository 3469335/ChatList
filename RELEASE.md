# Инструкция по публикации ChatList на GitHub

## Подготовка к релизу

### 1. Обновление версии

1. Откройте файл `version.py`
2. Обновите версию (например, с `1.0.0` на `1.0.1`):
   ```python
   __version__ = "1.0.1"
   ```
3. Сохраните файл

### 2. Сборка приложения

```bash
# Windows
build.bat

# Linux/Mac
./build.sh
```

Проверьте, что файл `dist/ChatList-v{version}.exe` создан успешно.

### 3. Создание инсталлятора

```bash
# Windows
create_installer.bat
```

Проверьте, что файл `installer/ChatList-Setup-{version}.exe` создан успешно.

### 4. Подготовка релизных заметок

1. Откройте файл `CHANGELOG.md` (создайте, если его нет)
2. Добавьте описание изменений для новой версии
3. Используйте формат:
   ```markdown
   ## [1.0.1] - 2026-01-12
   
   ### Добавлено
   - Улучшена обработка ошибок OpenRouter API
   
   ### Исправлено
   - Исправлена ошибка "No cookie auth credentials found"
   ```

## Публикация на GitHub Release (вручную)

### Шаг 1: Создание тега

```bash
# Создать тег с версией
git tag -a v1.0.1 -m "Release version 1.0.1"

# Отправить тег на GitHub
git push origin v1.0.1
```

### Шаг 2: Создание Release на GitHub

1. Перейдите на GitHub в репозиторий
2. Нажмите "Releases" → "Draft a new release"
3. Выберите созданный тег (например, `v1.0.1`)
4. Заголовок: `ChatList v1.0.1`
5. Описание: скопируйте из `CHANGELOG.md` или используйте шаблон из `RELEASE_NOTES_TEMPLATE.md`
6. Загрузите файлы:
   - `installer/ChatList-Setup-{version}.exe` (основной инсталлятор)
   - `dist/ChatList-v{version}.exe` (опционально, для прямого запуска)
7. Нажмите "Publish release"

## Публикация на GitHub Pages

### Шаг 1: Подготовка файлов

1. Убедитесь, что файл `docs/index.html` существует (лендинг)
2. Проверьте, что все ссылки в HTML корректны

### Шаг 2: Настройка GitHub Pages

1. Перейдите в Settings → Pages
2. Source: выберите "Deploy from a branch"
3. Branch: выберите `main` или `gh-pages`
4. Folder: выберите `/docs` или `/root`
5. Нажмите "Save"

### Шаг 3: Проверка

1. Подождите несколько минут
2. Перейдите на `https://{username}.github.io/{repository-name}/`
3. Проверьте, что лендинг отображается корректно

## Автоматическая публикация (GitHub Actions)

Для автоматической публикации используйте workflow файл `.github/workflows/release.yml`.

### Настройка

1. Создайте Personal Access Token (PAT) на GitHub:
   - Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Создайте токен с правами `repo` и `workflow`
2. Добавьте токен в Secrets репозитория:
   - Settings → Secrets and variables → Actions
   - Создайте секрет `GH_TOKEN` с вашим PAT

### Использование

1. Обновите версию в `version.py`
2. Создайте коммит и тег:
   ```bash
   git add version.py
   git commit -m "Bump version to 1.0.1"
   git tag v1.0.1
   git push origin main
   git push origin v1.0.1
   ```
3. GitHub Actions автоматически:
   - Соберет приложение
   - Создаст инсталлятор
   - Опубликует Release
   - Обновит GitHub Pages

## Структура файлов для релиза

```
ChatList/
├── dist/
│   └── ChatList-v{version}.exe      # Исполняемый файл
├── installer/
│   └── ChatList-Setup-{version}.exe # Инсталлятор
├── docs/
│   └── index.html                   # Лендинг для GitHub Pages
├── .github/
│   └── workflows/
│       └── release.yml              # Автоматический релиз
├── version.py                       # Версия приложения
├── CHANGELOG.md                     # История изменений
└── RELEASE_NOTES_TEMPLATE.md        # Шаблон релизных заметок
```

## Чеклист перед релизом

- [ ] Версия обновлена в `version.py`
- [ ] Приложение собрано и протестировано
- [ ] Инсталлятор создан и протестирован
- [ ] CHANGELOG.md обновлен
- [ ] Все изменения закоммичены
- [ ] Тег создан и отправлен на GitHub
- [ ] Release создан на GitHub
- [ ] Файлы загружены в Release
- [ ] GitHub Pages обновлен (если нужно)
- [ ] Лендинг проверен и работает

## Полезные ссылки

- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
