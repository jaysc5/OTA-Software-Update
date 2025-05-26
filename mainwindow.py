# -*- coding: utf-8 -*-

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QStackedWidget,
    QWidget, QVBoxLayout, QHBoxLayout
)
from PySide6.QtGui import QPixmap, QFontDatabase, QFont
from PySide6.QtCore import Qt

from pages import MapPage, DrivePage, VoiceControlPage, VoiceMode

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ota.ota_signal import setup_signal_handling
from ota.download_window import DownloadWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map & Update Navigation")
        self.setGeometry(100, 100, 800, 420)

        # 폰트 설정
        font_id = QFontDatabase.addApplicationFont("app/assets/font/malgun.ttf")
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            app_font = QFont(font_family, 10)
            QApplication.setFont(app_font)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.stacked_widget = QStackedWidget()

        # 이미지 로딩
        image_path_map = os.path.abspath("app/assets/img/map.png")
        image_path_control = os.path.abspath("app/assets/img/steering-wheel.png")
        image_path_mic = os.path.abspath("app/assets/img/mic.png")
        pixmap_map = QPixmap(image_path_map)
        pixmap_control = QPixmap(image_path_control)
        pixmap_mic = QPixmap(image_path_mic)

        self.page_home = QWidget()

        # --- 위젯 생성 함수 ---
        def create_icon_widget(pixmap, text, callback):
            label_icon = QLabel()
            label_icon.setPixmap(pixmap)
            label_icon.setFixedSize(128, 128)
            label_icon.setScaledContents(True)
            label_icon.setAlignment(Qt.AlignCenter)
            label_icon.mousePressEvent = callback

            label_text = QLabel(text)
            label_text.setAlignment(Qt.AlignCenter)

            layout = QVBoxLayout()
            layout.addWidget(label_icon)
            layout.addWidget(label_text)
            layout.setAlignment(Qt.AlignHCenter)

            container = QWidget()
            container.setLayout(layout)
            return container

        # 각 버튼 위젯 구성
        control_widget = create_icon_widget(pixmap_control, "수동 제어", self.goto_control_page)
        map_widget = create_icon_widget(pixmap_map, "지도", self.goto_map_page)
        voice_widget = create_icon_widget(pixmap_mic, "음성 제어", self.goto_voice_page)

        # 홈 페이지 상단 레이아웃 구성
        top_layout = QHBoxLayout()
        top_layout.addStretch(1)
        top_layout.addWidget(control_widget)
        top_layout.addSpacing(80)
        top_layout.addWidget(map_widget)
        top_layout.addSpacing(80)
        top_layout.addWidget(voice_widget)
        top_layout.addStretch(1)

        layout_home = QVBoxLayout()
        layout_home.addStretch(1)
        layout_home.addLayout(top_layout)
        layout_home.addStretch(1)
        self.page_home.setLayout(layout_home)

        # 페이지 정의   
        self.page_control = DrivePage(back_callback=self.goto_home_page)
        self.page_map = MapPage(back_callback=self.goto_home_page)
        self.page_voice = VoiceControlPage(back_callback=self.goto_home_page)  # 먼저 정의하고
        self.voice_mode = VoiceMode(self.page_voice)

        # 페이지 스택에 추가
        self.stacked_widget.addWidget(self.page_home)    # index 0
        self.stacked_widget.addWidget(self.page_control) # index 1
        self.stacked_widget.addWidget(self.page_map)     # index 2
        self.stacked_widget.addWidget(self.page_voice)   # index 3

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.central_widget.setLayout(main_layout)

        self.stacked_widget.setCurrentIndex(0)

        # OTA 창 핸들링
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

    # 페이지 전환 함수들
    def goto_control_page(self, event):
        self.stacked_widget.setCurrentIndex(1)

    def goto_map_page(self, event):
        self.stacked_widget.setCurrentIndex(2)

    def goto_voice_page(self, event):
        self.stacked_widget.setCurrentIndex(3)

    def goto_home_page(self):
        self.stacked_widget.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
