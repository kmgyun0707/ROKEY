from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from urllib.parse import quote


class MapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QWebEngineView(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        # 초기에는 아무 페이지도 로드하지 않음(이미지 태그 분석 후에만 로드)
        self.view.setUrl(QUrl("about:blank"))

    def search_by_url(self, keyword: str):
        # 네이버 지도 v5 검색 URL로 직접 이동
        # 예: https://map.naver.com/v5/search/초밥
        encoded = quote(keyword)
        url = f"https://map.naver.com/v5/search/{encoded}"
        self.view.setUrl(QUrl(url))
