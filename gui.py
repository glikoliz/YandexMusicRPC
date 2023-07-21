import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QCheckBox, QSystemTrayIcon, \
    QSpacerItem, QSizePolicy, QMenu, QAction, QStyle, qApp, QPushButton
from PyQt5.QtCore import QSize, QEvent, Qt
from PIL import Image
import configparser
import main
class MainWindow(QMainWindow):
    """
        Объявление чекбокса и иконки системного трея.
        Инициализироваться будут в конструкторе.
    """

    tray_icon = Image.open('ok\ym.ico')
    # Переопределяем конструктор класса
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("conf.ini")
        try:
            check_box = config.getboolean("SETTINGS", "change_status")
        except:
            check_box=False
            print("govno jopa")
        # Обязательно нужно вызвать метод супер класса
        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(300, 150))             # Устанавливаем размеры
        self.setWindowTitle("Яндекс музычка")  # Устанавливаем заголовок окна
        central_widget = QWidget(self)                  # Создаём центральный виджет
        self.setCentralWidget(central_widget)           # Устанавливаем центральный виджет
 
        grid_layout = QGridLayout(self)         # Создаём QGridLayout
        central_widget.setLayout(grid_layout)   # Устанавливаем данное размещение в центральный виджет
        # grid_layout.addWidget(QLabel("Хуй", self), 0, 0)

        # Добавляем чекбокс, от которого будет зависеть поведение программы при закрытии окна
        self.check_box = QCheckBox('Статус')
        self.check_box.setChecked(check_box)
        self.check_box.clicked.connect(main.change_config_status)
        grid_layout.addWidget(self.check_box, 1, 0)
        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 2, 0)

        self.button=QPushButton("Старт")
        grid_layout.addWidget(self.button, 2, 0)
        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 3, 2)
        self.button.clicked.connect(main.start_everything)
        # button.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 3, 0)
        # Инициализируем QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        # show_action = QAction("Открыть", self)
        quit_action = QAction("Закрыть", self)
        # hide_action = QAction("Остановить", self)
        # show_action.triggered.connect(self.show)
        # hide_action.triggered.connect(main.stop_loop)
        quit_action.triggered.connect(qApp.quit) 
        tray_menu = QMenu()
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # tray_menu.addAction(show_action)
        # tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        # self.windowStateChanged.connect(self.window_state_changed)
        
    # Переопределение метода closeEvent, для перехвата события закрытия окна
    def closeEvent(self, event):
        # event.ignore()
        main.stop_loop()
    def changeEvent(self, event):
        # Проверяем, было ли изменено состояние окна (в том числе сворачивание)
        if event.type() == QEvent.WindowStateChange:
            # Проверяем, является ли новое состояние окна свернутым
            if self.isMinimized():
                # Скрываем окно в трей
                self.hide()
                self.tray_icon.showMessage(
                    "Яндекс Музыка RPC",
                    "Приложение свёрнуто в трей",
                    QSystemTrayIcon.Information,
                    2000
                )

        # Вызываем родительский метод для обработки других типов событий
        super().changeEvent(event)
    def window_state_changed(self, state):
        # Проверяем, является ли состояние окна свернутым (Minimized)
        if state == self.WindowMinimized:
            # self.WindowMinimized=False
            # Выполняем желаемые действия при сворачивании окна
            self.hide()
            self.tray_icon.showMessage(
                "Яндекс Музыка RPC",
                "Приложение свёрнуто в трей",
                QSystemTrayIcon.Information,
                2000
            )
    def tray_icon_activated(self, reason):
        # Если произошел двойной клик на иконке
        if reason == QSystemTrayIcon.DoubleClick:
            # Показываем/скрываем приложение
            if self.isHidden():
                self.show()
            else:
                self.hide()
 
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    
    sys.exit(app.exec())