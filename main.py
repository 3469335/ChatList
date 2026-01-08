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
    QHeaderView, QProgressBar, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime
import db
import models
from models import send_prompt_to_models


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
        
        self.name_edit = QLineEdit()
        self.api_url_edit = QLineEdit()
        self.api_id_edit = QLineEdit()
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems(["openai", "deepseek", "groq", "other"])
        self.is_active_checkbox = QCheckBox()
        self.is_active_checkbox.setChecked(True)
        
        layout.addRow("Название:", self.name_edit)
        layout.addRow("API URL:", self.api_url_edit)
        layout.addRow("API Key (env var):", self.api_id_edit)
        layout.addRow("Тип модели:", self.model_type_combo)
        layout.addRow("Активна:", self.is_active_checkbox)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
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
        db.init_database()
    
    def init_ui(self):
        self.setWindowTitle("ChatList - Сравнение ответов нейросетей")
        self.setGeometry(100, 100, 1400, 900)
        
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
        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self.send_prompt)
        self.save_prompt_btn = QPushButton("Сохранить промт")
        self.save_prompt_btn.clicked.connect(self.save_prompt)
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
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setColumnWidth(0, 150)
        self.results_table.setColumnWidth(1, 500)
        self.results_table.setColumnWidth(2, 80)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        results_layout.addWidget(self.results_table)
        
        # Кнопка сохранения результатов
        self.save_results_btn = QPushButton("Сохранить выбранные результаты")
        self.save_results_btn.clicked.connect(self.save_selected_results)
        self.save_results_btn.setEnabled(False)
        results_layout.addWidget(self.save_results_btn)
        
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
    
    def save_prompt(self):
        """Сохранить промт в БД"""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Ошибка", "Промт не может быть пустым!")
            return
        
        tags = self.tags_input.text().strip()
        db.create_prompt(prompt_text, tags)
        self.load_prompts()
        QMessageBox.information(self, "Успех", "Промт сохранен!")
    
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
        active_models = models.get_active_models_list()
        if not active_models:
            QMessageBox.warning(self, "Ошибка", "Нет активных моделей!")
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
        
        # Сохранить результаты во временную таблицу
        self.temp_results = results
        
        # Отобразить в таблице
        self.results_table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            # Модель
            model_item = QTableWidgetItem(result['model_name'])
            self.results_table.setItem(row, 0, model_item)
            
            # Ответ
            response_text = result['response'] if result['success'] else f"Ошибка: {result['error']}"
            response_item = QTableWidgetItem(response_text)
            self.results_table.setItem(row, 1, response_item)
            
            # Чекбокс
            checkbox = QCheckBox()
            checkbox.setChecked(False)
            checkbox.stateChanged.connect(lambda state, r=row: self.on_checkbox_changed(r, state))
            self.results_table.setCellWidget(row, 2, checkbox)
        
        self.results_table.resizeRowsToContents()
        self.save_results_btn.setEnabled(True)
        self.statusBar().showMessage("Запросы завершены", 3000)
    
    def on_checkbox_changed(self, row, state):
        """Обработчик изменения чекбокса"""
        if row < len(self.temp_results):
            self.temp_results[row]['selected'] = (state == Qt.Checked)
    
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
            db.save_results(results_to_save)
            QMessageBox.information(self, "Успех", f"Сохранено результатов: {len(results_to_save)}")
            
            # Очистить временную таблицу
            self.temp_results = []
            self.results_table.setRowCount(0)
            self.save_results_btn.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
