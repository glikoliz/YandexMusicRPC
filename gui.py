import sys
import configparser
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QCheckBox, QSystemTrayIcon, \
    QSpacerItem, QSizePolicy, QMenu, QAction, QStyle, qApp, QPushButton, QMenuBar
from PyQt5.QtCore import QSize, QEvent, QUrl
from PyQt5 import QtGui
from PyQt5.QtGui import QDesktopServices
class MainWindow(QMainWindow):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("conf.ini")
        try:
            check_box = config.getboolean("SETTINGS", "change_status")
        except:
            check_box=False

        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(300, 150))          
        self.setWindowTitle("Яндекс музыка RPC") 
        central_widget = QWidget(self)               
        self.setCentralWidget(central_widget)          
 
        grid_layout = QGridLayout(self)        
        central_widget.setLayout(grid_layout)  

        self.check_box = QCheckBox('Транслировать текст песни в статус')
        self.check_box.setChecked(check_box)
        # self.check_box.clicked.connect(main.change_config_status)
        grid_layout.addWidget(self.check_box, 1, 0)
        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 2, 0)

        self.main_button=QPushButton("Старт")
        grid_layout.addWidget(self.main_button, 2, 0)
        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 3, 0)
        # self.button.clicked.connect(main.start_everything)

        self.loglabel=QLabel("")
        grid_layout.addWidget(self.loglabel, 3, 0)
        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 3, 0)


        self.tray_icon = QSystemTrayIcon(self)
        quit_action = QAction("Закрыть", self)
        quit_action.triggered.connect(qApp.quit) 
        tray_menu = QMenu()
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        menuBar = QMenuBar(self)
        action = QAction('GitHub', self)
        menuBar.addAction(action)
        self.setMenuBar(menuBar)
        action.triggered.connect(self.open_link)
        self.app_name_action = QAction("My App", self)
        self.app_name_action.setEnabled(False)
        # self.menu.addAction(self.app_name_action)
        
    # Переопределение метода closeEvent, для перехвата события закрытия окна
    # def closeEvent(self, event):
        # event.ignore()
        # main.stop_loop()
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

    def tray_icon_activated(self, reason):
        # Если произошел двойной клик на иконке
        if reason == QSystemTrayIcon.DoubleClick:
            # Показываем/скрываем приложение
            if self.isHidden():
                self.show()
            else:
                self.hide()
    def open_link(self):
        url = QUrl('https://github.com/glikoliz/YandexMusicRPC')
        QDesktopServices.openUrl(url)
if __name__ == "__main__":
    
    icon_path='src\ym.ico'
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(icon_path))
    mw = MainWindow()
    mw.tray_icon.setIcon(QtGui.QIcon(icon_path))
    mw.show()
    
    sys.exit(app.exec())