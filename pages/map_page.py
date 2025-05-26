from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, QTimer

class MapPage(QWidget):
    def __init__(self, back_callback=None):
        super().__init__()

        layout = QVBoxLayout()

        # 뒤로 가기 버튼
        btn_back = QPushButton("Back")
        if back_callback:
            btn_back.clicked.connect(back_callback)
        layout.addWidget(btn_back)

        # WebEngineView 생성
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(500)  # 중요!
        layout.addWidget(self.web_view)

        # Google Maps HTML (실행 안정성 고려하여 defer + window.onload 사용)
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Google Map</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                html, body, #map {
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }
                #map {
                    min-height: 400px;
                }
            </style>
            <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBVn01br_JrzWGxA0eRNDV9uHe3C_ZbkvQ" defer></script>
            <script>
                function initMap() {
                    const map = new google.maps.Map(document.getElementById("map"), {
                        center: { lat: 37.50136, lng: 127.0396 },
                        zoom: 15
                    });

                    new google.maps.Marker({
                        position: { lat: 37.50136, lng: 127.0396 },
                        map: map,
                        title: "멀티캠퍼스"
                    });
                }

                window.onload = initMap;
            </script>
        </head>
        <body>
            <div id="map"></div>
        </body>
        </html>
        """

        # 지도가 WebEngine 내부에서 확실히 준비되도록 딜레이 적용
        QTimer.singleShot(100, lambda: self.web_view.setHtml(html, baseUrl=QUrl("https://maps.googleapis.com/")))

        self.setLayout(layout)
