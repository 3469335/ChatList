import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Минимальное PyQt приложение")
        self.setGeometry(100, 100, 400, 300)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Вертикальный layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Метка
        self.label = QLabel("Привет, PyQt!")
        layout.addWidget(self.label)
        
        # Кнопка
        self.button = QPushButton("Нажми меня")
        self.button.clicked.connect(self.on_button_clicked)
        layout.addWidget(self.button)
    
    def on_button_clicked(self):
        self.label.setText("Минимальная программа на Python")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

