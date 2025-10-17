from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QFileDialog, QDockWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from .map_widget import MapWidget
from ..api.openai_vision import analyze_image
from .preferences_panel import PreferencesPanel
from ..utils.preferences import load_prefs


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Food Recommender")
        self.resize(1200, 800)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        # 상단 검색창 제거, 최소한의 컨트롤만 유지
        self.open_img_btn = QPushButton("이미지 선택", self)
        self.search_btn = QPushButton("지역 주변 음식 찾기", self)
        self.result_label = QLabel("태그 결과: -", self)
        self.result_label.setWordWrap(True)
        # 태그 표시를 가볍고 작게 (약 1/5 체감) - 작은 폰트와 낮은 최대 높이
        self.result_label.setStyleSheet("font-size: 8pt; color: #555;")
        self.result_label.setMaximumHeight(50)
        # 최근 분석된 쿼리(검색어) 캐시
        self._last_query = ""
        # 이미지 미리보기 영역(작은 정사각형)
        self.image_preview = QLabel("미리보기", self)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setFixedSize(140, 140)
        self.image_preview.setStyleSheet(
            "border: 1px solid #ddd; background: #fafafa; color: #888;"
        )
        self._orig_pixmap = None  # 원본 QPixmap 캐시

        top = QHBoxLayout()
        top.addWidget(self.open_img_btn)
        top.addWidget(self.search_btn)
        top.addStretch(1)

        self.map = MapWidget(self)

        root = QVBoxLayout(central)
        root.addLayout(top)
        # 중앙에는 지도와 결과만 배치
        root.addWidget(self.map)
        root.addWidget(self.result_label)

        self.open_img_btn.clicked.connect(self._on_open_image)
        self.search_btn.clicked.connect(self._on_search_clicked)

        # 좌측 도킹: 사용자 선호/상태 입력 패널
        dock = QDockWidget("내 정보", self)
        dock.setObjectName("preferencesDock")
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.pref_panel = PreferencesPanel(self)
        # 도킹 컨테이너에 환경설정 패널 아래로 미리보기 정사각형 배치
        dock_container = QWidget(self)
        dock_layout = QVBoxLayout(dock_container)
        dock_layout.setContentsMargins(6, 6, 6, 6)
        dock_layout.setSpacing(6)
        dock_layout.addWidget(self.pref_panel)
        dock_layout.addWidget(self.image_preview, alignment=Qt.AlignHCenter)
        dock_layout.addStretch(1)
        dock.setWidget(dock_container)
        self.addDockWidget(0x1, dock)  # LeftDockWidgetArea
        # 현재 저장된 prefs 캐시
        self._prefs = load_prefs()
        # 패널에서 값이 바뀌면 즉시 캐시 갱신
        self.pref_panel.changed.connect(self._on_prefs_changed)
        # 도킹 패널 너비를 절반으로 축소(측정 불가 시 창의 25%로 설정)
        total_w = max(1, self.width())
        curr = dock.width()
        if curr > 0:
            target_w = max(150, int(curr * 0.5))
        else:
            target_w = max(150, int(total_w * 0.25))
        self.resizeDocks([dock], [target_w], Qt.Horizontal)


    def _on_open_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "음식 이미지 선택", "", "Images (*.jpg *.jpeg *.png)")
        if not path:
            return
        # 1) 선택 즉시 이미지 미리보기 표시
        self._set_preview_image(path)
        tags = analyze_image(path)
        # 태그만 표시
        cat = ", ".join(tags.get("category", []))
        dishes = ", ".join(tags.get("dishes", []))
        taste = ", ".join(tags.get("taste", []))
        nut = ", ".join(tags.get("nutrition", []))
        self.result_label.setText(f"태그 결과: category=[{cat}] dishes=[{dishes}] taste=[{taste}] nutrition=[{nut}]")
        # 자동 검색 금지: 분석된 결과에서 검색어만 캐시하고 실제 검색은 버튼 클릭 시 수행
        dishes_list = tags.get("dishes", []) or []
        if dishes_list:
            self._last_query = dishes_list[0]
        else:
            cats = tags.get("category", []) or []
            self._last_query = cats[0] if cats else ""

    def _set_preview_image(self, path: str):
        pm = QPixmap(path)
        if pm.isNull():
            self.image_preview.setText("이미지를 불러오지 못했습니다")
            self._orig_pixmap = None
            return
        self._orig_pixmap = pm
        self._update_preview_scaled()

    def _update_preview_scaled(self):
        if not self._orig_pixmap:
            return
        area = self.image_preview.size()
        if area.width() <= 0 or area.height() <= 0:
            return
        scaled = self._orig_pixmap.scaled(area, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_preview.setPixmap(scaled)
        self.image_preview.setText("")

    def _on_search_clicked(self):
        # 버튼 클릭 시에만 검색 수행: 지역 + 마지막 분석 쿼리
        query = (self._last_query or "").strip()
        if not query:
            # 분석된 쿼리가 없다면 아무 것도 하지 않음
            return
        city = (self._prefs.get("city") or "").strip()
        final_query = f"{city} {query}".strip() if city else query
        self.map.search_by_url(final_query)

    def _on_prefs_changed(self, prefs: dict):
        # UI에서 변경된 환경을 캐시에 반영
        self._prefs = dict(prefs or {})

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 창 크기 변경 시 미리보기 이미지도 부드럽게 리스케일
        self._update_preview_scaled()
