"""
Тестовая программа для просмотра и редактирования SQLite баз данных
"""
import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
    QLineEdit, QLabel, QDialog, QDialogButtonBox, QFormLayout, QMessageBox,
    QFileDialog, QHeaderView, QSpinBox, QGroupBox, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class EditRecordDialog(QDialog):
    """Диалог для редактирования записи"""
    
    def __init__(self, parent=None, table_name="", record_data=None, columns=None):
        super().__init__(parent)
        self.table_name = table_name
        self.record_data = record_data
        self.columns = columns or []
        self.is_new = record_data is None
        
        title = f"Редактировать запись: {table_name}" if not self.is_new else f"Новая запись: {table_name}"
        self.setWindowTitle(title)
        self.setModal(True)
        self.init_ui()
        
        if self.record_data:
            self.load_data()
    
    def init_ui(self):
        layout = QFormLayout()
        self.fields = {}
        
        for col in self.columns:
            col_name = col[1]  # Имя колонки
            col_type = col[2]   # Тип колонки
            col_notnull = col[3]  # NOT NULL
            col_pk = col[5]  # Primary key
            
            # Для новых записей: пропустить AUTOINCREMENT колонки (обычно это ID с INTEGER PRIMARY KEY)
            if self.is_new and col_pk and 'integer' in col_type.lower():
                # Это автоинкремент - пропускаем
                continue
            
            # Для существующих записей: не показывать ID/PK колонки
            if not self.is_new and (col_name.lower() in ['id', 'rowid'] or col_pk):
                continue
            
            # Для таблицы prompts: пропустить поле date при создании (будет заполнено автоматически)
            if self.is_new and self.table_name.lower() == 'prompts' and col_name.lower() == 'date':
                continue
            
            if 'text' in col_type.lower() or 'varchar' in col_type.lower() or 'char' in col_type.lower():
                field = QLineEdit()
            elif 'integer' in col_type.lower() or 'int' in col_type.lower():
                field = QSpinBox()
                field.setRange(-2147483648, 2147483647)
            elif 'real' in col_type.lower() or 'float' in col_type.lower() or 'double' in col_type.lower():
                field = QLineEdit()  # Для простоты используем QLineEdit для float
            elif 'blob' in col_type.lower():
                field = QLineEdit()
                field.setPlaceholderText("BLOB данные не редактируются")
                field.setReadOnly(True)
            else:
                field = QLineEdit()
            
            self.fields[col_name] = field
            layout.addRow(f"{col_name}:", field)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Загрузить данные в поля"""
        if not self.record_data:
            return
        
        for i, col in enumerate(self.columns):
            col_name = col[1]
            if col_name in self.fields:
                value = self.record_data[i]
                if value is not None:
                    if isinstance(self.fields[col_name], QSpinBox):
                        try:
                            self.fields[col_name].setValue(int(value))
                        except (ValueError, TypeError):
                            pass
                    else:
                        self.fields[col_name].setText(str(value))
    
    def get_data(self):
        """Получить данные из полей"""
        data = {}
        for col_name, field in self.fields.items():
            if isinstance(field, QSpinBox):
                data[col_name] = field.value()
            else:
                data[col_name] = field.text()
        return data


class DatabaseViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_path = None
        self.db_conn = None
        self.current_table = None
        self.current_page = 0
        self.page_size = 50
        self.total_records = 0
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("SQLite Database Viewer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Левая панель: выбор файла и список таблиц
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Правая панель: данные таблицы
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 3)
    
    def create_left_panel(self):
        """Создать левую панель с выбором БД и списком таблиц"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Заголовок
        title = QLabel("База данных")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Выбор файла БД
        file_group = QGroupBox("Выбор базы данных")
        file_layout = QVBoxLayout()
        
        self.file_label = QLabel("Файл не выбран")
        file_layout.addWidget(self.file_label)
        
        self.open_file_btn = QPushButton("Выбрать файл БД")
        self.open_file_btn.clicked.connect(self.select_database)
        file_layout.addWidget(self.open_file_btn)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Список таблиц
        tables_group = QGroupBox("Таблицы")
        tables_layout = QVBoxLayout()
        
        self.tables_list = QListWidget()
        self.tables_list.itemClicked.connect(self.on_table_selected)
        tables_layout.addWidget(self.tables_list)
        
        self.open_table_btn = QPushButton("Открыть")
        self.open_table_btn.clicked.connect(self.open_selected_table)
        self.open_table_btn.setEnabled(False)
        tables_layout.addWidget(self.open_table_btn)
        
        tables_group.setLayout(tables_layout)
        layout.addWidget(tables_group)
        
        layout.addStretch()
        
        return panel
    
    def create_right_panel(self):
        """Создать правую панель с данными таблицы"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Заголовок
        self.table_title = QLabel("Выберите таблицу")
        self.table_title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.table_title)
        
        # Информация о пагинации
        pagination_info = QWidget()
        pagination_layout = QHBoxLayout()
        pagination_info.setLayout(pagination_layout)
        
        self.page_info_label = QLabel("")
        pagination_layout.addWidget(self.page_info_label)
        
        pagination_layout.addStretch()
        
        # Размер страницы
        pagination_layout.addWidget(QLabel("Записей на странице:"))
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setRange(10, 500)
        self.page_size_spin.setValue(50)
        self.page_size_spin.valueChanged.connect(self.on_page_size_changed)
        pagination_layout.addWidget(self.page_size_spin)
        
        layout.addWidget(pagination_info)
        
        # Кнопки управления данными
        buttons_layout = QHBoxLayout()
        
        self.create_btn = QPushButton("Создать")
        self.create_btn.clicked.connect(self.create_record)
        self.create_btn.setEnabled(False)
        buttons_layout.addWidget(self.create_btn)
        
        self.update_btn = QPushButton("Изменить")
        self.update_btn.clicked.connect(self.update_record)
        self.update_btn.setEnabled(False)
        buttons_layout.addWidget(self.update_btn)
        
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_record)
        self.delete_btn.setEnabled(False)
        buttons_layout.addWidget(self.delete_btn)
        
        buttons_layout.addStretch()
        
        # Навигация по страницам
        self.first_page_btn = QPushButton("<<")
        self.first_page_btn.clicked.connect(lambda: self.go_to_page(0))
        self.first_page_btn.setEnabled(False)
        buttons_layout.addWidget(self.first_page_btn)
        
        self.prev_page_btn = QPushButton("<")
        self.prev_page_btn.clicked.connect(self.prev_page)
        self.prev_page_btn.setEnabled(False)
        buttons_layout.addWidget(self.prev_page_btn)
        
        self.page_label = QLabel("Страница: 1")
        buttons_layout.addWidget(self.page_label)
        
        self.next_page_btn = QPushButton(">")
        self.next_page_btn.clicked.connect(self.next_page)
        self.next_page_btn.setEnabled(False)
        buttons_layout.addWidget(self.next_page_btn)
        
        self.last_page_btn = QPushButton(">>")
        self.last_page_btn.clicked.connect(lambda: self.go_to_page(-1))
        self.last_page_btn.setEnabled(False)
        buttons_layout.addWidget(self.last_page_btn)
        
        layout.addLayout(buttons_layout)
        
        # Таблица данных
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Запретить прямое редактирование
        self.data_table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.data_table)
        
        return panel
    
    def select_database(self):
        """Выбрать файл базы данных"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл базы данных SQLite", "", "SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        
        if filename:
            self.db_path = filename
            self.file_label.setText(f"Файл: {filename.split('/')[-1]}")
            self.load_tables()
    
    def load_tables(self):
        """Загрузить список таблиц из БД"""
        try:
            if self.db_conn:
                self.db_conn.close()
            
            self.db_conn = sqlite3.connect(self.db_path)
            self.db_conn.row_factory = sqlite3.Row
            cursor = self.db_conn.cursor()
            
            # Получить список таблиц
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            
            self.tables_list.clear()
            for table in tables:
                item = QListWidgetItem(table[0])
                self.tables_list.addItem(item)
            
            self.open_table_btn.setEnabled(len(tables) > 0)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить таблицы: {str(e)}")
    
    def on_table_selected(self, item):
        """Обработчик выбора таблицы"""
        self.open_table_btn.setEnabled(True)
    
    def open_selected_table(self):
        """Открыть выбранную таблицу"""
        current_item = self.tables_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите таблицу!")
            return
        
        self.current_table = current_item.text()
        self.current_page = 0
        self.load_table_data()
    
    def load_table_data(self):
        """Загрузить данные таблицы с пагинацией"""
        if not self.current_table or not self.db_conn:
            return
        
        try:
            cursor = self.db_conn.cursor()
            
            # Получить информацию о колонках
            cursor.execute(f'PRAGMA table_info("{self.current_table}")')
            columns = cursor.fetchall()
            
            if not columns:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить информацию о колонках")
                return
            
            # Подсчитать общее количество записей
            cursor.execute(f'SELECT COUNT(*) FROM "{self.current_table}"')
            self.total_records = cursor.fetchone()[0]
            
            # Вычислить пагинацию
            total_pages = (self.total_records + self.page_size - 1) // self.page_size if self.total_records > 0 else 1
            offset = self.current_page * self.page_size
            
            # Получить данные с пагинацией
            cursor.execute(f'SELECT * FROM "{self.current_table}" LIMIT ? OFFSET ?', (self.page_size, offset))
            rows = cursor.fetchall()
            
            # Настроить таблицу
            column_names = [col[1] for col in columns]
            self.data_table.setColumnCount(len(column_names))
            self.data_table.setHorizontalHeaderLabels(column_names)
            self.data_table.setRowCount(len(rows))
            
            # Заполнить таблицу
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    self.data_table.setItem(row_idx, col_idx, item)
            
            self.data_table.resizeColumnsToContents()
            self.columns_info = columns
            
            # Обновить интерфейс
            self.table_title.setText(f"Таблица: {self.current_table}")
            self.update_pagination_info()
            self.create_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")
    
    def update_pagination_info(self):
        """Обновить информацию о пагинации"""
        total_pages = (self.total_records + self.page_size - 1) // self.page_size if self.total_records > 0 else 1
        current_page_display = self.current_page + 1
        
        start_record = self.current_page * self.page_size + 1
        end_record = min((self.current_page + 1) * self.page_size, self.total_records)
        
        self.page_info_label.setText(
            f"Показано записей: {start_record}-{end_record} из {self.total_records}"
        )
        self.page_label.setText(f"Страница: {current_page_display} из {total_pages}")
        
        # Включить/выключить кнопки навигации
        self.first_page_btn.setEnabled(self.current_page > 0)
        self.prev_page_btn.setEnabled(self.current_page > 0)
        self.next_page_btn.setEnabled(self.current_page < total_pages - 1)
        self.last_page_btn.setEnabled(self.current_page < total_pages - 1)
    
    def on_page_size_changed(self, value):
        """Обработчик изменения размера страницы"""
        self.page_size = value
        self.current_page = 0
        if self.current_table:
            self.load_table_data()
    
    def go_to_page(self, page):
        """Перейти на указанную страницу"""
        total_pages = (self.total_records + self.page_size - 1) // self.page_size if self.total_records > 0 else 1
        if page == -1:
            page = total_pages - 1
        
        if 0 <= page < total_pages:
            self.current_page = page
            self.load_table_data()
    
    def prev_page(self):
        """Перейти на предыдущую страницу"""
        if self.current_page > 0:
            self.current_page -= 1
            self.load_table_data()
    
    def next_page(self):
        """Перейти на следующую страницу"""
        total_pages = (self.total_records + self.page_size - 1) // self.page_size if self.total_records > 0 else 1
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.load_table_data()
    
    def on_selection_changed(self):
        """Обработчик изменения выбора строки"""
        has_selection = len(self.data_table.selectedItems()) > 0
        self.update_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def create_record(self):
        """Создать новую запись"""
        if not self.current_table:
            return
        
        dialog = EditRecordDialog(self, self.current_table, None, self.columns_info)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self.insert_record(data)
    
    def insert_record(self, data):
        """Вставить новую запись в БД"""
        try:
            cursor = self.db_conn.cursor()
            
            # Для таблицы prompts автоматически добавить поле date с текущей датой и временем
            if self.current_table.lower() == 'prompts':
                # Проверить, есть ли колонка date
                has_date_column = False
                for col_info in self.columns_info:
                    if col_info[1].lower() == 'date':
                        has_date_column = True
                        if 'date' not in data or not data['date']:
                            # Автоматически заполнить текущей датой и временем
                            data['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        break
            
            # Фильтруем пустые значения и ID колонки
            columns = []
            values = []
            for col_name, value in data.items():
                # Пропускаем пустые строки, но включаем 0 и False
                if value == "" or value is None:
                    continue
                
                # Проверяем, не является ли это автоинкремент колонкой
                is_autoincrement = False
                for col_info in self.columns_info:
                    if col_info[1] == col_name and col_info[5] and 'integer' in col_info[2].lower():
                        is_autoincrement = True
                        break
                
                if not is_autoincrement:
                    columns.append(col_name)
                    # Преобразуем значение в правильный тип
                    if isinstance(value, str):
                        # Попробовать преобразовать в число, если нужно
                        for col_info in self.columns_info:
                            if col_info[1] == col_name:
                                if 'integer' in col_info[2].lower():
                                    try:
                                        value = int(value)
                                    except ValueError:
                                        pass
                                elif 'real' in col_info[2].lower() or 'float' in col_info[2].lower():
                                    try:
                                        value = float(value)
                                    except ValueError:
                                        pass
                                break
                    values.append(value)
            
            if not columns:
                QMessageBox.warning(self, "Ошибка", "Нет данных для вставки!")
                return
            
            placeholders = ','.join(['?' for _ in columns])
            columns_str = ','.join([f'"{col}"' for col in columns])  # Экранируем имена колонок
            
            cursor.execute(f'INSERT INTO "{self.current_table}" ({columns_str}) VALUES ({placeholders})', values)
            self.db_conn.commit()
            
            QMessageBox.information(self, "Успех", "Запись создана!")
            self.load_table_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать запись: {str(e)}")
            self.db_conn.rollback()
    
    def update_record(self):
        """Изменить выбранную запись"""
        selected_rows = self.data_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования!")
            return
        
        row = selected_rows[0].row()
        
        # Получить данные текущей строки
        record_data = []
        for col in range(self.data_table.columnCount()):
            item = self.data_table.item(row, col)
            record_data.append(item.text() if item else None)
        
        # Найти ID колонку (первичный ключ)
        id_column = None
        id_value = None
        id_index = None
        
        # Сначала ищем колонку с pk=1
        for i, col in enumerate(self.columns_info):
            if col[5]:  # col[5] - это pk (primary key), 1 = True
                id_column = col[1]
                id_index = i
                if i < len(record_data):
                    id_value = record_data[i]
                break
        
        # Если не найдена, ищем колонку с именем id или rowid
        if not id_column:
            for i, col in enumerate(self.columns_info):
                if col[1].lower() in ['id', 'rowid']:
                    id_column = col[1]
                    id_index = i
                    if i < len(record_data):
                        id_value = record_data[i]
                    break
        
        if not id_column or id_value is None:
            QMessageBox.warning(self, "Ошибка", "Не найден первичный ключ для редактирования!")
            return
        
        dialog = EditRecordDialog(self, self.current_table, record_data, self.columns_info)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self.update_record_in_db(id_column, id_value, data)
    
    def update_record_in_db(self, id_column, id_value, data):
        """Обновить запись в БД"""
        try:
            cursor = self.db_conn.cursor()
            
            # Исключить ID из обновления и пустые значения
            update_data = {}
            for k, v in data.items():
                if k.lower() != id_column.lower():
                    if v == "" or v is None:
                        continue  # Пропускаем пустые значения
                    update_data[k] = v
            
            if not update_data:
                QMessageBox.warning(self, "Ошибка", "Нет данных для обновления!")
                return
            
            # Преобразовать значения в правильные типы
            typed_values = []
            for col_name, value in update_data.items():
                typed_value = value
                # Найти тип колонки
                for col_info in self.columns_info:
                    if col_info[1] == col_name:
                        if 'integer' in col_info[2].lower():
                            try:
                                typed_value = int(value)
                            except (ValueError, TypeError):
                                typed_value = value
                        elif 'real' in col_info[2].lower() or 'float' in col_info[2].lower():
                            try:
                                typed_value = float(value)
                            except (ValueError, TypeError):
                                typed_value = value
                        break
                typed_values.append(typed_value)
            
            set_clause = ','.join([f'"{col}"=?' for col in update_data.keys()])
            values = typed_values + [id_value]
            
            cursor.execute(f'UPDATE "{self.current_table}" SET {set_clause} WHERE "{id_column}"=?', values)
            self.db_conn.commit()
            
            QMessageBox.information(self, "Успех", "Запись обновлена!")
            self.load_table_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить запись: {str(e)}")
            self.db_conn.rollback()
    
    def delete_record(self):
        """Удалить выбранную запись"""
        selected_rows = self.data_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить выбранную запись?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        row = selected_rows[0].row()
        
        # Найти ID колонку (первичный ключ)
        id_column = None
        id_value = None
        id_index = None
        
        # Сначала ищем колонку с pk=1
        for i, col in enumerate(self.columns_info):
            if col[5]:  # col[5] - это pk (primary key), 1 = True
                id_column = col[1]
                id_index = i
                break
        
        # Если не найдена, ищем колонку с именем id или rowid
        if not id_column:
            for i, col in enumerate(self.columns_info):
                if col[1].lower() in ['id', 'rowid']:
                    id_column = col[1]
                    id_index = i
                    break
        
        if id_index is not None:
            item = self.data_table.item(row, id_index)
            id_value = item.text() if item else None
        
        if not id_column or not id_value:
            QMessageBox.warning(self, "Ошибка", "Не найден первичный ключ для удаления!")
            return
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(f'DELETE FROM "{self.current_table}" WHERE "{id_column}"=?', (id_value,))
            self.db_conn.commit()
            
            QMessageBox.information(self, "Успех", "Запись удалена!")
            self.load_table_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить запись: {str(e)}")
            self.db_conn.rollback()
    
    def closeEvent(self, event):
        """Закрыть соединение с БД при закрытии приложения"""
        if self.db_conn:
            self.db_conn.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = DatabaseViewer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

