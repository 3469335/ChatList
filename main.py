"""
Главный модуль приложения ChatList
Графический интерфейс для отправки промтов в несколько нейросетей
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QCheckBox,
    QListWidget, QListWidgetItem, QLineEdit, QLabel, QSplitter,
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QComboBox,
    QHeaderView, QProgressBar, QGroupBox, QFileDialog, QSpinBox,
    QStyledItemDelegate, QTextBrowser, QMenu
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QIcon, QPalette
from datetime import datetime
import db
import models
from models import send_prompt_to_models
import logger
import json
import os
import markdown
from prompt_improver import improve_prompt, APIError as PromptImproverError
from config import get_api_key
import version


class MarkdownViewerDialog(QDialog):
    """Диалог для просмотра ответа в форматированном markdown"""
    
    def __init__(self, parent=None, model_name="", response_text=""):
        super().__init__(parent)
        self.setWindowTitle(f"Ответ модели: {model_name}")
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui(model_name, response_text)
    
    def init_ui(self, model_name, response_text):
        layout = QVBoxLayout()
        
        # Заголовок с названием модели
        header_label = QLabel(f"<h2>{model_name}</h2>")
        layout.addWidget(header_label)
        
        # Текстовый браузер для отображения HTML (конвертированный markdown)
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        
        # Конвертировать markdown в HTML
        try:
            # Попробовать с расширениями, если не получится - без них
            try:
                html_content = markdown.markdown(
                    response_text,
                    extensions=['extra', 'codehilite', 'tables', 'fenced_code']
                )
            except:
                # Если расширения недоступны, использовать базовый markdown
                html_content = markdown.markdown(response_text)
            # Добавить базовые стили для лучшего отображения
            styled_html = f"""
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    padding: 20px;
                }}
                pre {{
                    background-color: #f4f4f4;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 10px;
                    overflow-x: auto;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }}
                pre code {{
                    background-color: transparent;
                    padding: 0;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 10px 0;
                }}
                table th, table td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                table th {{
                    background-color: #f2f2f2;
                    font-weight: bold;
                }}
                blockquote {{
                    border-left: 4px solid #ddd;
                    margin: 0;
                    padding-left: 20px;
                    color: #666;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    margin-top: 20px;
                    margin-bottom: 10px;
                }}
            </style>
            {html_content}
            """
            self.text_browser.setHtml(styled_html)
        except Exception as e:
            # Если ошибка конвертации, показать как обычный текст
            self.text_browser.setPlainText(response_text)
            logger.log_error(f"Error converting markdown to HTML: {str(e)}")
        
        layout.addWidget(self.text_browser)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.close)
        layout.addWidget(buttons)
        
        self.setLayout(layout)


class ModelDialog(QDialog):
    """Диалог для добавления/редактирования модели"""
    
    def __init__(self, parent=None, model_data=None):
        super().__init__(parent)
        self.model_data = model_data
        self.setWindowTitle("Редактировать модель" if model_data else "Добавить модель")
        self.setModal(True)
        self.init_ui()
        
        if model_data:
            self.load_model_data()
    
    def init_ui(self):
        layout = QFormLayout()
        
        # Список популярных бесплатных моделей
        preset_label = QLabel("Выбрать из популярных бесплатных моделей:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("-- Выберите модель --", None)
        
        # Бесплатные модели OpenRouter (проверенные и работающие)
        free_models = [
            # Meta Llama модели (бесплатные)
            ("meta-llama/llama-3.3-70b-instruct:free", "Meta Llama 3.3 70B Instruct (OpenRouter, бесплатно)"),
            ("meta-llama/llama-3.1-405b-instruct:free", "Meta Llama 3.1 405B Instruct (OpenRouter, бесплатно)"),
            ("meta-llama/llama-3.2-3b-instruct:free", "Meta Llama 3.2 3B Instruct (OpenRouter, бесплатно)"),
            # Xiaomi модели (бесплатные)
            ("xiaomi/mimo-v2-flash:free", "Xiaomi MiMo V2 Flash (OpenRouter, бесплатно)"),
            # NVIDIA модели (бесплатные)
            ("nvidia/nemotron-3-nano-30b-a3b:free", "NVIDIA Nemotron 3 Nano 30B (OpenRouter, бесплатно)"),
            # Nous Research модели (бесплатные)
            ("nousresearch/hermes-3-llama-3.1-405b:free", "Nous Hermes 3 405B (OpenRouter, бесплатно)"),
            # Google модели (бесплатные)
            ("google/gemini-flash-1.5-8b:free", "Google Gemini Flash 1.5 8B (OpenRouter, бесплатно)"),
            # ByteDance модели (работает, но может требовать кредиты)
            ("bytedance-seed/seed-1.6-flash", "ByteDance Seed 1.6 Flash (OpenRouter)"),
        ]
        
        for model_id, display_name in free_models:
            self.preset_combo.addItem(display_name, {
                'name': model_id,
                'api_url': 'https://openrouter.ai/api/v1/chat/completions',
                'api_id': 'OPENROUTER_API_KEY',
                'model_type': 'openrouter'
            })
        
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        layout.addRow(preset_label)
        layout.addRow(self.preset_combo)
        
        # Разделитель
        separator = QLabel("─" * 40)
        layout.addRow(separator)
        
        self.name_edit = QLineEdit()
        self.api_url_edit = QLineEdit()
        self.api_id_edit = QLineEdit()
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems([
            "openai",
            "openrouter",
            "deepseek",
            "groq",
            "anthropic",
            "google",
            "mistral",
            "cohere",
            "perplexity",
            "together",
            "replicate",
            "huggingface",
            "azure-openai",
            "ollama",
            "localai",
            "other"
        ])
        self.is_active_checkbox = QCheckBox()
        self.is_active_checkbox.setChecked(True)
        
        layout.addRow("Название модели:", self.name_edit)
        layout.addRow("API URL:", self.api_url_edit)
        layout.addRow("API Key (env var):", self.api_id_edit)
        layout.addRow("Тип модели:", self.model_type_combo)
        layout.addRow("Активна:", self.is_active_checkbox)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def on_preset_changed(self, index):
        """Обработчик выбора предустановленной модели"""
        if index > 0:  # Не первый элемент "-- Выберите модель --"
            preset_data = self.preset_combo.currentData()
            if preset_data:
                self.name_edit.setText(preset_data['name'])
                self.api_url_edit.setText(preset_data['api_url'])
                self.api_id_edit.setText(preset_data['api_id'])
                model_type_index = self.model_type_combo.findText(preset_data['model_type'])
                if model_type_index >= 0:
                    self.model_type_combo.setCurrentIndex(model_type_index)
    
    def load_model_data(self):
        if self.model_data:
            self.name_edit.setText(self.model_data.get('name', ''))
            self.api_url_edit.setText(self.model_data.get('api_url', ''))
            self.api_id_edit.setText(self.model_data.get('api_id', ''))
            index = self.model_type_combo.findText(self.model_data.get('model_type', ''))
            if index >= 0:
                self.model_type_combo.setCurrentIndex(index)
            self.is_active_checkbox.setChecked(bool(self.model_data.get('is_active', 1)))
    
    def get_data(self):
        return {
            'name': self.name_edit.text(),
            'api_url': self.api_url_edit.text(),
            'api_id': self.api_id_edit.text(),
            'model_type': self.model_type_combo.currentText(),
            'is_active': 1 if self.is_active_checkbox.isChecked() else 0
        }


class RequestThread(QThread):
    """Поток для асинхронной отправки запросов"""
    finished = pyqtSignal(list)
    progress = pyqtSignal(str)
    
    def __init__(self, prompt, model_list):
        super().__init__()
        self.prompt = prompt
        self.model_list = model_list
    
    def run(self):
        self.progress.emit("Отправка запросов...")
        results = send_prompt_to_models(self.prompt, self.model_list)
        self.finished.emit(results)


class PromptImprovementThread(QThread):
    """Поток для асинхронного улучшения промта"""
    finished = pyqtSignal(dict)  # Результат: {'improved': str, 'variants': list}
    error = pyqtSignal(str)  # Сообщение об ошибке
    progress = pyqtSignal(str)
    
    def __init__(self, prompt_text, model_name, api_key, task_type='general'):
        super().__init__()
        self.prompt_text = prompt_text
        self.model_name = model_name
        self.api_key = api_key
        self.task_type = task_type
    
    def run(self):
        try:
            self.progress.emit("Улучшение промта...")
            result = improve_prompt(self.prompt_text, self.model_name, self.api_key, self.task_type)
            self.finished.emit(result)
        except PromptImproverError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Неожиданная ошибка: {str(e)}")


class PromptImprovementDialog(QDialog):
    """Диалог для улучшения промтов"""
    
    def __init__(self, parent=None, original_prompt=""):
        super().__init__(parent)
        self.original_prompt = original_prompt
        self.selected_prompt = None  # Выбранный пользователем промт для подстановки
        self.setWindowTitle("Улучшить промт")
        self.setModal(True)
        self.resize(900, 700)
        self.improvement_thread = None
        self.init_ui()
        self.load_models()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Исходный промт
        original_group = QGroupBox("Исходный промт")
        original_layout = QVBoxLayout()
        self.original_text = QTextEdit()
        self.original_text.setPlainText(self.original_prompt)
        self.original_text.setReadOnly(True)
        self.original_text.setMaximumHeight(100)
        original_layout.addWidget(self.original_text)
        original_group.setLayout(original_layout)
        layout.addWidget(original_group)
        
        # Выбор модели и типа адаптации
        settings_group = QGroupBox("Настройки улучшения")
        settings_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        settings_layout.addRow("Модель для улучшения:", self.model_combo)
        
        self.task_type_combo = QComboBox()
        self.task_type_combo.addItem("Общее улучшение", "general")
        self.task_type_combo.addItem("Код (программирование)", "code")
        self.task_type_combo.addItem("Анализ", "analysis")
        self.task_type_combo.addItem("Креатив", "creative")
        settings_layout.addRow("Тип адаптации:", self.task_type_combo)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Индикатор загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Улучшенный промт
        improved_group = QGroupBox("Улучшенный промт")
        improved_layout = QVBoxLayout()
        self.improved_text = QTextEdit()
        self.improved_text.setReadOnly(True)
        improved_layout.addWidget(self.improved_text)
        improved_btn_layout = QHBoxLayout()
        self.use_improved_btn = QPushButton("Подставить в поле ввода")
        self.use_improved_btn.clicked.connect(lambda: self.use_prompt(self.improved_text.toPlainText()))
        self.use_improved_btn.setEnabled(False)
        improved_btn_layout.addWidget(self.use_improved_btn)
        improved_layout.addLayout(improved_btn_layout)
        improved_group.setLayout(improved_layout)
        layout.addWidget(improved_group)
        
        # Альтернативные варианты
        variants_group = QGroupBox("Альтернативные варианты")
        variants_layout = QVBoxLayout()
        self.variants_list = QListWidget()
        variants_layout.addWidget(self.variants_list)
        variants_btn_layout = QHBoxLayout()
        self.use_variant_btn = QPushButton("Подставить выбранный вариант")
        self.use_variant_btn.clicked.connect(self.use_selected_variant)
        self.use_variant_btn.setEnabled(False)
        variants_btn_layout.addWidget(self.use_variant_btn)
        variants_layout.addLayout(variants_btn_layout)
        variants_group.setLayout(variants_layout)
        layout.addWidget(variants_group)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.improve_btn = QPushButton("Улучшить промт")
        self.improve_btn.clicked.connect(self.start_improvement)
        button_layout.addWidget(self.improve_btn)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        button_layout.addWidget(buttons)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Обработчик выбора варианта
        self.variants_list.itemSelectionChanged.connect(self.on_variant_selected)
    
    def load_models(self):
        """Загрузить список доступных моделей"""
        try:
            models_list = db.get_active_models()
            self.model_combo.clear()
            
            if not models_list:
                QMessageBox.warning(self, "Предупреждение", "Нет доступных активных моделей. Добавьте модели в настройках.")
                return
            
            # Добавляем только модели OpenRouter (они поддерживают системные промпты)
            for model in models_list:
                if 'openrouter' in model.get('api_url', '').lower() or model.get('model_type', '').lower() == 'openrouter':
                    self.model_combo.addItem(model['name'], model)
            
            if self.model_combo.count() == 0:
                QMessageBox.warning(self, "Предупреждение", 
                                  "Нет доступных моделей OpenRouter. Функция улучшения промтов работает только с OpenRouter моделями.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить модели: {str(e)}")
    
    def on_variant_selected(self):
        """Обработчик выбора варианта"""
        self.use_variant_btn.setEnabled(self.variants_list.currentItem() is not None)
    
    def use_selected_variant(self):
        """Подставить выбранный вариант"""
        current_item = self.variants_list.currentItem()
        if current_item:
            self.selected_prompt = current_item.text()
            self.accept()
    
    def use_prompt(self, prompt_text):
        """Подставить промт"""
        self.selected_prompt = prompt_text
        self.accept()
    
    def start_improvement(self):
        """Начать улучшение промта"""
        if not self.original_prompt or not self.original_prompt.strip():
            QMessageBox.warning(self, "Предупреждение", "Исходный промт не может быть пустым!")
            return
        
        if self.model_combo.count() == 0:
            QMessageBox.warning(self, "Предупреждение", "Нет доступных моделей для улучшения!")
            return
        
        # Получить выбранную модель
        model_data = self.model_combo.currentData()
        if not model_data:
            QMessageBox.warning(self, "Предупреждение", "Выберите модель для улучшения!")
            return
        
        model_name = model_data['name']
        api_id = model_data['api_id']
        api_key = get_api_key(api_id)
        
        if not api_key:
            QMessageBox.critical(self, "Ошибка", f"API ключ не найден для переменной {api_id}. Проверьте файл .env")
            return
        
        # Получить тип задачи
        task_type = self.task_type_combo.currentData()
        
        # Заблокировать UI
        self.improve_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        self.improved_text.clear()
        self.variants_list.clear()
        
        # Запустить поток улучшения
        self.improvement_thread = PromptImprovementThread(
            self.original_prompt,
            model_name,
            api_key,
            task_type
        )
        self.improvement_thread.finished.connect(self.on_improvement_finished)
        self.improvement_thread.error.connect(self.on_improvement_error)
        self.improvement_thread.progress.connect(lambda msg: self.progress_bar.setFormat(msg))
        self.improvement_thread.start()
    
    def on_improvement_finished(self, result):
        """Обработчик завершения улучшения"""
        self.progress_bar.setVisible(False)
        self.improve_btn.setEnabled(True)
        
        improved = result.get('improved', '')
        variants = result.get('variants', [])
        
        # Отобразить улучшенный промт
        self.improved_text.setPlainText(improved)
        self.use_improved_btn.setEnabled(bool(improved))
        
        # Отобразить варианты
        self.variants_list.clear()
        for i, variant in enumerate(variants, 1):
            item = QListWidgetItem(f"Вариант {i}: {variant}")
            item.setData(Qt.UserRole, variant)
            self.variants_list.addItem(item)
        
        if variants:
            QMessageBox.information(self, "Успех", f"Промт улучшен! Получено {len(variants)} альтернативных вариантов.")
        else:
            QMessageBox.information(self, "Успех", "Промт улучшен!")
    
    def on_improvement_error(self, error_msg):
        """Обработчик ошибки улучшения"""
        self.progress_bar.setVisible(False)
        self.improve_btn.setEnabled(True)
        QMessageBox.critical(self, "Ошибка", f"Не удалось улучшить промт:\n{error_msg}")
    
    def get_selected_prompt(self):
        """Получить выбранный промт для подстановки"""
        return self.selected_prompt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.temp_results = []  # Временная таблица результатов в памяти
        self.current_prompt_id = None
        self.init_database()
        self.init_ui()
        self.load_prompts()
        self.load_models()
    
    def init_database(self):
        """Инициализировать базу данных"""
        try:
            db.init_database()
            logger.log_info("Database initialized")
        except Exception as e:
            QMessageBox.critical(self, "Критическая ошибка", f"Не удалось инициализировать БД: {str(e)}")
            logger.log_error("Database initialization failed", e)
            raise
    
    def init_ui(self):
        self.setWindowTitle(f"ChatList v{version.__version__} - Сравнение ответов нейросетей")
        self.setGeometry(100, 100, 1400, 900)
        
        # Установить иконку окна
        icon_path = os.path.join(os.path.dirname(__file__), "app.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Применить настройки темы и шрифта
        self.apply_settings()
        
        # Создать меню
        self.create_menu()
        
        # Главный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Создаем сплиттеры для разделения окна
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель: история промтов
        left_panel = self.create_prompts_panel()
        main_splitter.addWidget(left_panel)
        
        # Центральная область: ввод промта и результаты
        center_panel = self.create_center_panel()
        main_splitter.addWidget(center_panel)
        
        # Правая панель: управление моделями
        right_panel = self.create_models_panel()
        main_splitter.addWidget(right_panel)
        
        # Устанавливаем пропорции
        main_splitter.setSizes([300, 800, 300])
        
        main_layout.addWidget(main_splitter)
    
    def create_menu(self):
        """Создать меню приложения"""
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        export_md_action = file_menu.addAction("Экспорт в Markdown")
        export_md_action.triggered.connect(lambda: self.export_results("markdown"))
        export_json_action = file_menu.addAction("Экспорт в JSON")
        export_json_action.triggered.connect(lambda: self.export_results("json"))
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Выход")
        exit_action.triggered.connect(self.close)
        
        # Меню Настройки
        settings_menu = menubar.addMenu("Настройки")
        app_settings_action = settings_menu.addAction("Настройки приложения")
        app_settings_action.triggered.connect(self.show_settings_dialog)
        
        # Меню Справка
        help_menu = menubar.addMenu("Справка")
        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(self.show_about)
    
    def create_prompts_panel(self):
        """Создать панель истории промтов"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Заголовок
        title = QLabel("История промтов")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Поиск
        self.prompt_search = QLineEdit()
        self.prompt_search.setPlaceholderText("Поиск промтов...")
        self.prompt_search.textChanged.connect(self.filter_prompts)
        layout.addWidget(self.prompt_search)
        
        # Список промтов
        self.prompts_list = QListWidget()
        self.prompts_list.itemDoubleClicked.connect(self.select_prompt)
        self.prompts_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.prompts_list.customContextMenuRequested.connect(self.show_prompt_context_menu)
        layout.addWidget(self.prompts_list)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.delete_prompt_btn = QPushButton("Удалить")
        self.delete_prompt_btn.clicked.connect(self.delete_selected_prompt)
        btn_layout.addWidget(self.delete_prompt_btn)
        layout.addLayout(btn_layout)
        
        return panel
    
    def create_center_panel(self):
        """Создать центральную панель с вводом промта и результатами"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Группа ввода промта
        prompt_group = QGroupBox("Ввод промта")
        prompt_layout = QVBoxLayout()
        
        # Выбор сохраненного промта
        self.prompt_combo = QComboBox()
        self.prompt_combo.addItem("-- Новый промт --")
        self.prompt_combo.currentIndexChanged.connect(self.on_prompt_combo_changed)
        prompt_layout.addWidget(QLabel("Выбрать сохраненный промт:"))
        prompt_layout.addWidget(self.prompt_combo)
        
        # Поле ввода промта
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Введите ваш промт здесь...")
        self.prompt_input.setMinimumHeight(150)
        prompt_layout.addWidget(QLabel("Текст промта:"))
        prompt_layout.addWidget(self.prompt_input)
        
        # Поле для тегов
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Теги (через запятую)")
        prompt_layout.addWidget(QLabel("Теги:"))
        prompt_layout.addWidget(self.tags_input)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.improve_btn = QPushButton("Улучшить промт")
        self.improve_btn.clicked.connect(self.improve_prompt)
        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self.send_prompt)
        self.save_prompt_btn = QPushButton("Сохранить промт")
        self.save_prompt_btn.clicked.connect(self.save_prompt)
        btn_layout.addWidget(self.improve_btn)
        btn_layout.addWidget(self.send_btn)
        btn_layout.addWidget(self.save_prompt_btn)
        prompt_layout.addLayout(btn_layout)
        
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Группа результатов
        results_group = QGroupBox("Результаты")
        results_layout = QVBoxLayout()
        
        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Модель", "Ответ", "Выбрано"])
        self.results_table.horizontalHeader().setStretchLastSection(False)
        self.results_table.setColumnWidth(0, 200)  # Модель - немного шире для длинных имен
        self.results_table.setColumnWidth(1, 600)  # Ответ - основное пространство
        self.results_table.setColumnWidth(2, 50)   # Выбрано - узкая колонка
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Ответ растягивается
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSortingEnabled(True)  # Включить сортировку
        # Настройка для многострочного отображения
        self.results_table.setWordWrap(True)  # Включить перенос текста
        self.results_table.setTextElideMode(Qt.ElideNone)  # Не обрезать текст
        # Обработчик выбора строки для активации кнопки
        self.results_table.itemSelectionChanged.connect(self.on_results_selection_changed)
        
        # Делегат для колонки с ответами (многострочный текст)
        class WordWrapDelegate(QStyledItemDelegate):
            def sizeHint(self, option, index):
                size = super().sizeHint(option, index)
                text = index.data(Qt.DisplayRole) or ""
                if text:
                    # Вычислить высоту с учетом переноса текста
                    font_metrics = option.fontMetrics
                    text_width = option.rect.width() - 20  # Отступы
                    if text_width > 0:
                        wrapped_text = font_metrics.boundingRect(
                            0, 0, text_width, 0,
                            Qt.TextWordWrap | Qt.AlignTop,
                            text
                        )
                        size.setHeight(max(60, wrapped_text.height() + 20))
                return size
        
        # Применить делегат только к колонке с ответами (колонка 1)
        self.results_table.setItemDelegateForColumn(1, WordWrapDelegate(self.results_table))
        results_layout.addWidget(self.results_table)
        
        # Кнопки управления результатами
        buttons_layout = QHBoxLayout()
        
        self.open_markdown_btn = QPushButton("Открыть в Markdown")
        self.open_markdown_btn.clicked.connect(self.open_selected_markdown)
        self.open_markdown_btn.setEnabled(False)
        buttons_layout.addWidget(self.open_markdown_btn)
        
        self.save_results_btn = QPushButton("Сохранить выбранные результаты")
        self.save_results_btn.clicked.connect(self.save_selected_results)
        self.save_results_btn.setEnabled(False)
        buttons_layout.addWidget(self.save_results_btn)
        
        results_layout.addLayout(buttons_layout)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        return panel
    
    def create_models_panel(self):
        """Создать панель управления моделями"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Заголовок
        title = QLabel("Модели нейросетей")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Список моделей
        self.models_list = QListWidget()
        self.models_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.models_list.customContextMenuRequested.connect(self.show_model_context_menu)
        layout.addWidget(self.models_list)
        
        # Кнопки
        btn_layout = QVBoxLayout()
        self.add_model_btn = QPushButton("Добавить модель")
        self.add_model_btn.clicked.connect(self.add_model)
        self.edit_model_btn = QPushButton("Редактировать")
        self.edit_model_btn.clicked.connect(self.edit_model)
        self.delete_model_btn = QPushButton("Удалить")
        self.delete_model_btn.clicked.connect(self.delete_model)
        btn_layout.addWidget(self.add_model_btn)
        btn_layout.addWidget(self.edit_model_btn)
        btn_layout.addWidget(self.delete_model_btn)
        layout.addLayout(btn_layout)
        
        return panel
    
    # ========== Методы для работы с промтами ==========
    
    def load_prompts(self):
        """Загрузить список промтов"""
        prompts = db.get_all_prompts()
        self.prompts_list.clear()
        self.prompt_combo.clear()
        self.prompt_combo.addItem("-- Новый промт --")
        
        for prompt in prompts:
            # В список
            item_text = f"{prompt['date']}: {prompt['prompt'][:50]}..."
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, prompt['id'])
            self.prompts_list.addItem(item)
            
            # В комбобокс
            self.prompt_combo.addItem(item_text, prompt['id'])
    
    def filter_prompts(self, text):
        """Фильтровать промты по тексту"""
        for i in range(self.prompts_list.count()):
            item = self.prompts_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def select_prompt(self, item):
        """Выбрать промт из списка"""
        prompt_id = item.data(Qt.UserRole)
        prompt = db.get_prompt_by_id(prompt_id)
        if prompt:
            self.prompt_input.setPlainText(prompt['prompt'])
            self.tags_input.setText(prompt.get('tags', ''))
            self.current_prompt_id = prompt_id
            # Выбрать в комбобоксе
            index = self.prompt_combo.findData(prompt_id)
            if index >= 0:
                self.prompt_combo.setCurrentIndex(index)
    
    def on_prompt_combo_changed(self, index):
        """Обработчик изменения выбора в комбобоксе"""
        if index == 0:  # "-- Новый промт --"
            self.prompt_input.clear()
            self.tags_input.clear()
            self.current_prompt_id = None
        else:
            prompt_id = self.prompt_combo.currentData()
            if prompt_id:
                prompt = db.get_prompt_by_id(prompt_id)
                if prompt:
                    self.prompt_input.setPlainText(prompt['prompt'])
                    self.tags_input.setText(prompt.get('tags', ''))
                    self.current_prompt_id = prompt_id
    
    def improve_prompt(self):
        """Открыть диалог улучшения промта"""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Предупреждение", "Введите промт для улучшения!")
            return
        
        dialog = PromptImprovementDialog(self, prompt_text)
        if dialog.exec_() == QDialog.Accepted:
            selected_prompt = dialog.get_selected_prompt()
            if selected_prompt:
                self.prompt_input.setPlainText(selected_prompt)
                logger.log_info("Improved prompt applied to input field")
    
    def save_prompt(self):
        """Сохранить промт в БД"""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Ошибка", "Промт не может быть пустым!")
            return
        
        try:
            tags = self.tags_input.text().strip()
            db.create_prompt(prompt_text, tags)
            self.load_prompts()
            QMessageBox.information(self, "Успех", "Промт сохранен!")
            logger.log_info(f"Prompt saved: {prompt_text[:50]}...")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить промт: {str(e)}")
            logger.log_error("Failed to save prompt", e)
    
    def delete_selected_prompt(self):
        """Удалить выбранный промт"""
        current_item = self.prompts_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите промт для удаления!")
            return
        
        prompt_id = current_item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить этот промт?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            db.delete_prompt(prompt_id)
            self.load_prompts()
    
    def show_prompt_context_menu(self, position):
        """Показать контекстное меню для промта"""
        # Реализация контекстного меню (можно расширить)
        pass
    
    # ========== Методы для работы с моделями ==========
    
    def load_models(self):
        """Загрузить список моделей"""
        models_list = db.get_all_models()
        self.models_list.clear()
        
        for model in models_list:
            item_text = f"{'✓' if model['is_active'] else '✗'} {model['name']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, model)
            self.models_list.addItem(item)
    
    def add_model(self):
        """Добавить новую модель"""
        dialog = ModelDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not all([data['name'], data['api_url'], data['api_id']]):
                QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
                return
            db.create_model(
                data['name'], data['api_url'], data['api_id'],
                data['is_active'], data['model_type']
            )
            self.load_models()
    
    def edit_model(self):
        """Редактировать модель"""
        current_item = self.models_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите модель для редактирования!")
            return
        
        model_data = current_item.data(Qt.UserRole)
        dialog = ModelDialog(self, model_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not all([data['name'], data['api_url'], data['api_id']]):
                QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
                return
            db.update_model(
                model_data['id'],
                data['name'], data['api_url'], data['api_id'],
                data['is_active'], data['model_type']
            )
            self.load_models()
            QMessageBox.information(self, "Успех", "Модель обновлена!")
    
    def delete_model(self):
        """Удалить модель"""
        current_item = self.models_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите модель для удаления!")
            return
        
        model_data = current_item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить модель '{model_data['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            db.delete_model(model_data['id'])
            self.load_models()
    
    def show_model_context_menu(self, position):
        """Показать контекстное меню для модели"""
        # Реализация контекстного меню (можно расширить)
        pass
    
    # ========== Методы для работы с запросами ==========
    
    def send_prompt(self):
        """Отправить промт в модели"""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Ошибка", "Введите промт!")
            return
        
        # Очистить временную таблицу
        self.temp_results = []
        self.results_table.setRowCount(0)
        self.save_results_btn.setEnabled(False)
        
        # Получить активные модели
        try:
            active_models = models.get_active_models_list()
            if not active_models:
                QMessageBox.warning(self, "Ошибка", "Нет активных моделей!")
                logger.log_info("No active models found")
                return
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке моделей: {str(e)}")
            logger.log_error("Failed to load models", e)
            return
        
        # Показать прогресс
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        self.send_btn.setEnabled(False)
        
        # Запустить поток для отправки запросов
        self.request_thread = RequestThread(prompt_text, active_models)
        self.request_thread.finished.connect(self.on_requests_finished)
        self.request_thread.progress.connect(lambda msg: self.statusBar().showMessage(msg))
        self.request_thread.start()
    
    def on_requests_finished(self, results):
        """Обработчик завершения запросов"""
        self.progress_bar.setVisible(False)
        self.send_btn.setEnabled(True)
        
        # Сохранить результаты во временную таблицу с правильным сопоставлением
        self.temp_results = []
        
        # Отобразить в таблице
        self.results_table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            # Убедиться, что данные правильно сопоставлены
            model_name = result.get('model_name', f'Модель {row+1}')
            model_id = result.get('model_id', None)
            response_text = result.get('response', '')
            success = result.get('success', False)
            error = result.get('error', '')
            
            # Сохранить в temp_results с правильным сопоставлением
            temp_result = {
                'model_id': model_id,
                'model_name': model_name,
                'response': response_text if success else '',
                'error': error if not success else '',
                'success': success,
                'selected': False
            }
            self.temp_results.append(temp_result)
            
            # Модель - колонка 0 (выравнивание по верхнему краю)
            model_item = QTableWidgetItem(model_name)
            model_item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)  # Выравнивание сверху слева
            model_item.setToolTip(model_name)  # Подсказка при наведении
            self.results_table.setItem(row, 0, model_item)
            
            # Ответ - колонка 1 (многострочный)
            if success:
                response_item = QTableWidgetItem(response_text)
            else:
                response_item = QTableWidgetItem(f"Ошибка: {error}")
                response_item.setForeground(Qt.red)  # Красный цвет для ошибок
            
            # Настройка для многострочного отображения
            response_item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)  # Выравнивание сверху слева
            
            # Подсказка с полным текстом
            full_text = response_text if success else f"Ошибка: {error}"
            response_item.setToolTip(full_text[:1000] if len(full_text) > 1000 else full_text)
            
            self.results_table.setItem(row, 1, response_item)
            
            # Логирование
            logger.log_api_request(
                model_name,
                self.prompt_input.toPlainText()[:100],
                success,
                error if not success else None
            )
            
            # Чекбокс - колонка 2 (выравнивание по верхнему краю)
            checkbox = QCheckBox()
            checkbox.setChecked(False)
            # Используем замыкание для правильного сохранения индекса строки
            checkbox.stateChanged.connect(lambda state, r=row: self.on_checkbox_changed(r, state))
            # Создать контейнер для выравнивания чекбокса по верху
            checkbox_widget = QWidget()
            checkbox_layout = QVBoxLayout()
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.addStretch()  # Растянуть пространство вниз для выравнивания по верху
            checkbox_widget.setLayout(checkbox_layout)
            self.results_table.setCellWidget(row, 2, checkbox_widget)
        
        # Автоматически подогнать высоту строк под содержимое (с учетом многострочного текста)
        for row in range(self.results_table.rowCount()):
            self.results_table.resizeRowToContents(row)
            # Убедиться, что минимальная высота достаточна
            current_height = self.results_table.rowHeight(row)
            if current_height < 60:
                self.results_table.setRowHeight(row, 60)
        
        self.save_results_btn.setEnabled(True)
        self.open_markdown_btn.setEnabled(False)  # Будет активирована при выборе строки
        self.statusBar().showMessage(f"Запросы завершены. Получено ответов: {sum(1 for r in results if r.get('success', False))}/{len(results)}", 3000)
    
    def on_checkbox_changed(self, row, state):
        """Обработчик изменения чекбокса"""
        if row < len(self.temp_results):
            self.temp_results[row]['selected'] = (state == Qt.Checked)
    
    def on_results_selection_changed(self):
        """Обработчик изменения выбора строки в таблице результатов"""
        selected_rows = self.results_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            if row >= 0 and row < len(self.temp_results):
                result = self.temp_results[row]
                # Активировать кнопку только если ответ успешный
                self.open_markdown_btn.setEnabled(result.get('success', False))
            else:
                self.open_markdown_btn.setEnabled(False)
        else:
            self.open_markdown_btn.setEnabled(False)
    
    def open_selected_markdown(self):
        """Открыть диалог просмотра markdown для выбранной строки"""
        selected_rows = self.results_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите строку с ответом для просмотра")
            return
        
        row = selected_rows[0].row()
        self.open_markdown_viewer(row)
    
    def open_markdown_viewer(self, row):
        """Открыть диалог просмотра markdown для выбранной строки"""
        if row < 0 or row >= len(self.temp_results):
            return
        
        result = self.temp_results[row]
        model_name = result.get('model_name', 'Неизвестная модель')
        response_text = result.get('response', '')
        
        if not response_text:
            QMessageBox.warning(self, "Ошибка", "Нет ответа для отображения")
            return
        
        dialog = MarkdownViewerDialog(self, model_name, response_text)
        dialog.exec_()
    
    def save_selected_results(self):
        """Сохранить выбранные результаты в БД"""
        selected_results = [r for r in self.temp_results if r.get('selected', False)]
        if not selected_results:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один результат!")
            return
        
        # Сохранить промт, если он новый
        if not self.current_prompt_id:
            prompt_text = self.prompt_input.toPlainText().strip()
            tags = self.tags_input.text().strip()
            self.current_prompt_id = db.create_prompt(prompt_text, tags)
            self.load_prompts()
        
        # Подготовить данные для сохранения
        results_to_save = []
        for result in selected_results:
            if result['success']:
                results_to_save.append({
                    'prompt_id': self.current_prompt_id,
                    'model_id': result['model_id'],
                    'response': result['response'],
                    'selected': 1
                })
        
        if results_to_save:
            try:
                db.save_results(results_to_save)
                QMessageBox.information(self, "Успех", f"Сохранено результатов: {len(results_to_save)}")
                logger.log_info(f"Saved {len(results_to_save)} results to database")
                
                # Очистить временную таблицу
                self.temp_results = []
                self.results_table.setRowCount(0)
                self.save_results_btn.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить результаты: {str(e)}")
                logger.log_error("Failed to save results", e)
    
    # ========== Методы для экспорта ==========
    
    def export_results(self, format_type: str):
        """Экспортировать результаты в файл"""
        if not self.temp_results:
            QMessageBox.warning(self, "Ошибка", "Нет результатов для экспорта!")
            return
        
        if format_type == "markdown":
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить как Markdown", "", "Markdown Files (*.md)"
            )
            if filename:
                self.export_to_markdown(filename)
        elif format_type == "json":
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить как JSON", "", "JSON Files (*.json)"
            )
            if filename:
                self.export_to_json(filename)
    
    def export_to_markdown(self, filename: str):
        """Экспортировать результаты в Markdown"""
        try:
            prompt_text = self.prompt_input.toPlainText()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# Результаты сравнения моделей\n\n")
                f.write(f"## Промт\n\n{prompt_text}\n\n")
                f.write(f"## Ответы моделей\n\n")
                f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                
                for result in self.temp_results:
                    if result.get('success'):
                        f.write(f"### {result['model_name']}\n\n")
                        f.write(f"{result['response']}\n\n")
                        f.write("---\n\n")
                    else:
                        f.write(f"### {result['model_name']} (Ошибка)\n\n")
                        f.write(f"*{result['error']}*\n\n")
                        f.write("---\n\n")
            
            QMessageBox.information(self, "Успех", f"Результаты экспортированы в {filename}")
            logger.log_info(f"Exported results to Markdown: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте: {str(e)}")
            logger.log_error("Export to Markdown failed", e)
    
    def export_to_json(self, filename: str):
        """Экспортировать результаты в JSON"""
        try:
            export_data = {
                'prompt': self.prompt_input.toPlainText(),
                'tags': self.tags_input.text(),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'results': []
            }
            
            for result in self.temp_results:
                export_data['results'].append({
                    'model_name': result['model_name'],
                    'model_id': result.get('model_id'),
                    'response': result.get('response', ''),
                    'success': result.get('success', False),
                    'error': result.get('error'),
                    'selected': result.get('selected', False)
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "Успех", f"Результаты экспортированы в {filename}")
            logger.log_info(f"Exported results to JSON: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте: {str(e)}")
            logger.log_error("Export to JSON failed", e)
    
    # ========== Методы для настроек ==========
    
    def apply_settings(self):
        """Применить настройки темы и шрифта"""
        # Применить тему
        theme = db.get_setting('theme', 'light')
        self.apply_theme(theme)
        
        # Применить размер шрифта
        font_size = int(db.get_setting('font_size', '10'))
        self.apply_font_size(font_size)
    
    def apply_theme(self, theme: str):
        """Применить тему (light/dark)"""
        app = QApplication.instance()
        if theme == 'dark':
            # Темная тема
            app.setStyle('Fusion')
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
        else:
            # Светлая тема (по умолчанию)
            app.setStyle('Fusion')
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, Qt.white)
            palette.setColor(QPalette.AlternateBase, QColor(233, 233, 233))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.black)
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.white)
            app.setPalette(palette)
    
    def apply_font_size(self, font_size: int):
        """Применить размер шрифта к панелям"""
        font = QFont()
        font.setPointSize(font_size)
        
        # Применить ко всем виджетам в главном окне
        self.setFont(font)
        
        # Применить к дочерним виджетам
        for widget in self.findChildren(QWidget):
            if isinstance(widget, (QLabel, QLineEdit, QTextEdit, QPushButton, QListWidget, QTableWidget)):
                widget.setFont(font)
    
    def show_settings_dialog(self):
        """Показать диалог настроек"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки")
        dialog.setModal(True)
        dialog.resize(400, 300)
        layout = QVBoxLayout()
        
        # Группа внешнего вида
        appearance_group = QGroupBox("Внешний вид")
        appearance_layout = QFormLayout()
        
        # Выбор темы
        theme_combo = QComboBox()
        theme_combo.addItem("Светлая", "light")
        theme_combo.addItem("Темная", "dark")
        current_theme = db.get_setting('theme', 'light')
        theme_index = theme_combo.findData(current_theme)
        if theme_index >= 0:
            theme_combo.setCurrentIndex(theme_index)
        appearance_layout.addRow("Тема:", theme_combo)
        
        # Размер шрифта
        font_size_spin = QSpinBox()
        font_size_spin.setRange(8, 20)
        font_size_spin.setValue(int(db.get_setting('font_size', '10')))
        font_size_spin.setSuffix(" pt")
        appearance_layout.addRow("Размер шрифта:", font_size_spin)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Группа параметров запросов
        requests_group = QGroupBox("Параметры запросов")
        requests_layout = QFormLayout()
        
        # Таймаут запросов
        timeout_spin = QSpinBox()
        timeout_spin.setRange(10, 300)
        timeout_spin.setValue(int(db.get_setting('request_timeout', '30')))
        timeout_spin.setSuffix(" сек")
        requests_layout.addRow("Таймаут запросов:", timeout_spin)
        
        # Максимум результатов
        max_results_spin = QSpinBox()
        max_results_spin.setRange(1, 100)
        max_results_spin.setValue(int(db.get_setting('max_results_per_request', '10')))
        requests_layout.addRow("Максимум результатов:", max_results_spin)
        
        requests_group.setLayout(requests_layout)
        layout.addWidget(requests_group)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            # Сохранить настройки
            theme = theme_combo.currentData()
            font_size = font_size_spin.value()
            timeout = timeout_spin.value()
            max_results = max_results_spin.value()
            
            db.set_setting('theme', theme)
            db.set_setting('font_size', str(font_size))
            db.set_setting('request_timeout', str(timeout))
            db.set_setting('max_results_per_request', str(max_results))
            
            # Применить настройки немедленно
            self.apply_theme(theme)
            self.apply_font_size(font_size)
            
            QMessageBox.information(self, "Успех", "Настройки сохранены!")
            logger.log_info("Settings updated")
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = f"""
        <h2>ChatList v{version.__version__}</h2>
        <p><b>Приложение для сравнения ответов различных нейросетей</b></p>
        
        <p>ChatList позволяет отправлять один и тот же промт в несколько AI-моделей 
        и сравнивать их ответы в удобном интерфейсе.</p>
        
        <h3>Основные возможности:</h3>
        <ul>
            <li>Отправка промтов в несколько моделей одновременно</li>
            <li>Сравнение ответов в таблице результатов</li>
            <li>Сохранение промтов и результатов в базе данных</li>
            <li>Управление моделями нейросетей</li>
            <li>Экспорт результатов в Markdown и JSON</li>
            <li>AI-ассистент для улучшения промтов</li>
            <li>Настройка темы и размера шрифта</li>
        </ul>
        
        <h3>Поддерживаемые провайдеры:</h3>
        <p>OpenAI, OpenRouter, DeepSeek, Groq, Anthropic, Google, Mistral и другие</p>
        
        <p><i>Разработано с использованием PyQt5 и Python</i></p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"О программе ChatList v{version.__version__}")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about_text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec_()


def main():
    app = QApplication(sys.argv)
    
    # Установить иконку приложения
    icon_path = os.path.join(os.path.dirname(__file__), "app.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
