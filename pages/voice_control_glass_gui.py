# SSAFY 13 embedded proj. + PySide6 GUI (for integration)

import os
import threading
import asyncio
import queue
import pyaudio

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton 
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal

from google.cloud import speech
from google.oauth2 import service_account  # 인증용
import websockets

# ---------- Qt GUI ---------- #
class MainWindow(QWidget):
    update_text_signal = Signal(str, bool)  # (명령어 문자열, 전송 여부)

    def __init__(self, back_callback=None):
        super().__init__()
        self.back_callback = back_callback
        self.setWindowTitle("음성 명령 디스플레이")
        self.setGeometry(100, 100, 800, 440)

        layout = QVBoxLayout()

        mic_path = os.path.abspath("assets/img/mic.png")
        self.image = QLabel()
        self.image.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(mic_path)
        if not pixmap.isNull():
            self.image.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
        else:
            self.image.setText("[mic.png 없음]")
        layout.addWidget(self.image)

        self.label = QLabel("명령을 기다리는 중...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.label)
        
        if self.back_callback:
            back_btn = QPushButton("뒤로가기")
            back_btn.clicked.connect(self.back_callback)
            layout.addWidget(back_btn)

        self.setLayout(layout)

        self.update_text_signal.connect(self.update_command)


    def update_command(self, command: str, sent=False):
        if sent:
            self.label.setText(f"전송된 명령: {command}")
        else:
            self.label.setText(f"인식된 명령: {command}")

# ---------- 음성 입력 클래스 ---------- #
class MicrophoneStream:
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True
        self.frame_count = 0

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            data = []
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            self.frame_count += 1
            yield b''.join(data)

# ---------- Voice Recognition + WebSocket Client ---------- #
class VoiceMode:
    def __init__(self, gui: MainWindow):
      self.gui = gui
      self.command_list = []
      self.lasttime_you_said = []

      self.rate = 16000
      self.chunk = int(self.rate / 10)

      # 정확한 인증 설정
      key_path = "/home/pi/second/ssafy-embedded-project-460003-3c46ffba0430.json"
      self.credentials = service_account.Credentials.from_service_account_file(key_path)
      self.client = speech.SpeechClient(credentials=self.credentials)

      self.client_config = speech.RecognitionConfig(
        encoding='LINEAR16',
        sample_rate_hertz=self.rate,
        max_alternatives=1,
        language_code='ko-KR'
      )
      self.streaming_config = speech.StreamingRecognitionConfig(
          config=self.client_config,
          interim_results=True
      )

      self.serverURI = 'ws://192.168.137.205:7890'
      self.is_websocket_active = True

      threading.Thread(target=self.do_voice_recognition, daemon=True).start()
      threading.Thread(target=self.do_websocket_client, daemon=True).start()


    def do_voice_recognition(self):
        with MicrophoneStream(self.rate, self.chunk) as stream:
            while not stream.closed:
                audio_generator = stream.generator()
                requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
                responses = self.client.streaming_recognize(self.streaming_config, requests)
                self.listen_print_loop(responses, stream)

    def listen_print_loop(self, responses, stream):
        for response in responses:
            if stream.frame_count > 60 * self.rate / self.chunk:
                stream.frame_count = 0
                break
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript
            tr = transcript.split()

            if tr == self.lasttime_you_said or not tr:
                continue

            self.lasttime_you_said = tr
            self.command_list = tr
            print(f"[RECOGNIZED] {tr}")

            # 가장 최근 단어만 표시
            self.gui.update_text_signal.emit(tr[-1], False)

    def do_websocket_client(self):
        asyncio.run(self.websocket_client())

    async def websocket_client(self):
        try:
            async with websockets.connect(self.serverURI) as websocket:
                print("[DEBUG] WebSocket 연결됨")
                while self.is_websocket_active:
                    if self.command_list:
                        for command in self.command_list:
                            await websocket.send(command)
                            print(f'[TX] "{command}" 전송됨')
                            resp = await websocket.recv()
                            print(f'[RX] 응답 수신: {resp}')

                        self.gui.update_text_signal.emit(self.command_list[-1], True)
                        self.command_list = []
        except Exception as e:
            print(f'[ERROR] WebSocket 오류: {e}')
