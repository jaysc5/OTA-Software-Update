from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import asyncio
import websockets

COMMAND_MAP = {
    "Up": "앞으로",
    "Down": "뒤로",
    "Left": "왼쪽",
    "Right": "오른쪽",
    "Reset": "중앙",
    "Start": "앞으로",
    "Stop": "정지"
}

class DrivePage(QWidget):
    def __init__(self, back_callback=None):
        super().__init__()

        self.ws_uri = "ws://192.168.137.205:7890"  # 서버 주소 수정 가능

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # === 왼쪽: Command Table + Start/Stop ===
        left_layout = QVBoxLayout()

        self.command_label = QLabel("Command Table")
        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)

        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")

        for btn in [self.btn_start, self.btn_stop]:
            btn.setFixedSize(80, 40)
            self._add_shadow_effect(btn)

        self.btn_start.clicked.connect(lambda: self.append_command("Start"))
        self.btn_stop.clicked.connect(lambda: self.append_command("Stop"))

        left_layout.addWidget(self.command_label)
        left_layout.addWidget(self.command_output)
        left_layout.addWidget(self.btn_start)
        left_layout.addWidget(self.btn_stop)

        if back_callback:
            btn_back = QPushButton("Back")
            btn_back.setFixedSize(80, 40)
            btn_back.clicked.connect(back_callback)
            self._add_shadow_effect(btn_back)
            left_layout.addWidget(btn_back)

        left_layout.addStretch()

        # === 오른쪽: 방향 버튼 ===
        right_layout = QVBoxLayout()

        self.btn_up = QPushButton("↑")
        self.btn_down = QPushButton("↓")
        self.btn_left = QPushButton("←")
        self.btn_right = QPushButton("→")
        self.btn_reset = QPushButton("Reset")

        for btn in [self.btn_up, self.btn_down, self.btn_left, self.btn_right, self.btn_reset]:
            btn.setFixedSize(60, 40)
            self._add_shadow_effect(btn)
            btn.pressed.connect(lambda b=btn: b.setStyleSheet("background-color: lightgray;"))
            btn.released.connect(lambda b=btn: b.setStyleSheet(""))

        self.btn_up.clicked.connect(lambda: self.append_command("Up"))
        self.btn_down.clicked.connect(lambda: self.append_command("Down"))
        self.btn_left.clicked.connect(lambda: self.append_command("Left"))
        self.btn_right.clicked.connect(lambda: self.append_command("Right"))
        self.btn_reset.clicked.connect(lambda: self.append_command("Reset"))

        arrow_layout = QVBoxLayout()
        arrow_layout.addWidget(self.btn_up, alignment=Qt.AlignCenter)

        mid_layout = QHBoxLayout()
        mid_layout.addWidget(self.btn_left)
        mid_layout.addWidget(self.btn_reset)
        mid_layout.addWidget(self.btn_right)

        arrow_layout.addLayout(mid_layout)
        arrow_layout.addWidget(self.btn_down, alignment=Qt.AlignCenter)

        right_layout.addLayout(arrow_layout)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

    def append_command(self, text):
        self.command_output.append(f"→ {text}")
        print(f"[LOG] 명령 추가됨: {text}")
        command_kor = COMMAND_MAP.get(text, text)
        try:
            asyncio.run(self.send_websocket_command(command_kor))
        except RuntimeError as e:
            print(f"[ERROR] asyncio.run() 실패: {e}")

    async def send_websocket_command(self, command: str):
        try:
            print(f"[INFO] 서버 연결 시도 중: {self.ws_uri}")
            async with websockets.connect(self.ws_uri) as ws:
                print(f"[INFO] 서버 연결 성공")
                await ws.send(command)
                print(f"[TX] 전송: {command}")
                response = await ws.recv()
                print(f"[RX] 응답: {response}")
        except Exception as e:
            print(f"[ERROR] 웹소켓 전송 실패: {e}")

    def _add_shadow_effect(self, button):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 160))
        button.setGraphicsEffect(shadow)
