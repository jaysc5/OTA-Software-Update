import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QStackedWidget,
    QWidget, QVBoxLayout, QHBoxLayout
)
from PySide6.QtGui import QPixmap, QFontDatabase, QFont
from PySide6.QtCore import Qt

from pages import MapPage, DrivePage
from ota import setup_signal_handling, DownloadWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map & Update Navigation")
        self.setGeometry(100, 100, 800, 420)

        # 폰트 설정
        font_id = QFontDatabase.addApplicationFont("assets/font/malgun.ttf")
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            app_font = QFont(font_family, 10)
            QApplication.setFont(app_font)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.stacked_widget = QStackedWidget()

        image_path1 = os.path.abspath("assets/img/map.png")
        image_path2 = os.path.abspath("assets/img/steering-wheel.png")
        pixmap1 = QPixmap(image_path1)
        pixmap2 = QPixmap(image_path2)

        self.page_home = QWidget()

        # 수동 제어 버튼
        self.label_control = QLabel()
        self.label_control.setPixmap(pixmap2)
        self.label_control.setFixedSize(128, 128)
        self.label_control.setScaledContents(True)
        self.label_control.setAlignment(Qt.AlignCenter)
        self.label_control.mousePressEvent = self.goto_control_page

        self.label_control_text = QLabel("수동 제어")
        self.label_control_text.setAlignment(Qt.AlignCenter)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.label_control)
        control_layout.addWidget(self.label_control_text)
        control_layout.setAlignment(Qt.AlignHCenter)

        control_widget = QWidget()
        control_widget.setLayout(control_layout)

        # 지도 버튼
        self.label_map = QLabel()
        self.label_map.setPixmap(pixmap1)
        self.label_map.setFixedSize(128, 128)
        self.label_map.setScaledContents(True)
        self.label_map.setAlignment(Qt.AlignCenter)
        self.label_map.mousePressEvent = self.goto_map_page

        self.label_map_text = QLabel("지도")
        self.label_map_text.setAlignment(Qt.AlignCenter)

        map_layout = QVBoxLayout()
        map_layout.addWidget(self.label_map)
        map_layout.addWidget(self.label_map_text)
        map_layout.setAlignment(Qt.AlignHCenter)

        map_widget = QWidget()
        map_widget.setLayout(map_layout)

        # 홈 레이아웃 구성
        top_layout = QHBoxLayout()
        top_layout.addStretch(1)
        top_layout.addWidget(control_widget)
        top_layout.addSpacing(150)
        top_layout.addWidget(map_widget)
        top_layout.addStretch(1)

        layout_home = QVBoxLayout()
        layout_home.addStretch(1)
        layout_home.addLayout(top_layout)
        layout_home.addStretch(1)
        self.page_home.setLayout(layout_home)

        self.page_control = DrivePage(back_callback=self.goto_home_page)
        self.page_map = MapPage(back_callback=self.goto_home_page)

        self.stacked_widget.addWidget(self.page_home)
        self.stacked_widget.addWidget(self.page_control)
        self.stacked_widget.addWidget(self.page_map)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.central_widget.setLayout(main_layout)

        self.stacked_widget.setCurrentIndex(0)

        self.download_window = None
        setup_signal_handling(self, self.show_download_window)

    def show_download_window(self):
        if self.download_window is None or not self.download_window.isVisible():
            self.download_window = DownloadWindow(parent=self)
            self.download_window.setWindowModality(Qt.ApplicationModal)

            parent_geom = self.geometry()
            center_x = parent_geom.x() + (parent_geom.width() - self.download_window.width()) // 2
            center_y = parent_geom.y() + (parent_geom.height() - self.download_window.height()) // 2
            self.download_window.move(center_x, center_y)

            self.download_window.show()

    def goto_control_page(self, event):
        self.stacked_widget.setCurrentIndex(1)

    def goto_map_page(self, event):
        self.stacked_widget.setCurrentIndex(2)

    def goto_home_page(self):
        self.stacked_widget.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
