from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QSpinBox, QPushButton, QComboBox, QTextEdit
)
from PyQt5.QtCore import pyqtSignal
from ..utils.preferences import load_prefs, save_prefs


class PreferencesPanel(QWidget):
    changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._prefs = load_prefs()
        self._build()

    def _build(self):
        lay = QFormLayout(self)
        # 위치(도시명)
        self.city_edit = QLineEdit(self)
        self.city_edit.setPlaceholderText("지역명 (예: 서울, 경주)")
        self.city_edit.setText(str(self._prefs.get("city", "")))

        # 최근 먹었던 음식
        self.last_foods = QTextEdit(self)
        self.last_foods.setPlaceholderText("콤마(,)로 구분하여 입력: 비빔밥, 파스타")
        self.last_foods.setFixedHeight(48)
        self.last_foods.setText(
            ", ".join(self._prefs.get("last_foods", []))
        )

        # 기분 상태
        self.mood = QComboBox(self)
        self.mood.addItems(["보통", "기쁨", "피곤", "스트레스", "슬픔", "설렘"]) 
        self.mood.setCurrentText(self._prefs.get("mood", "보통"))

        # 반경
        self.radius = QSpinBox(self)
        self.radius.setRange(100, 10000)
        self.radius.setSingleStep(100)
        self.radius.setValue(int(self._prefs.get("search_radius_m", 2000)))

        save_btn = QPushButton("저장", self)
        save_btn.clicked.connect(self._on_save)

        lay.addRow("지역", self.city_edit)
        lay.addRow("최근 음식", self.last_foods)
        lay.addRow("기분", self.mood)
        lay.addRow("검색 반경(m)", self.radius)
        lay.addRow("", save_btn)

    def _on_save(self):
        prefs = {
            "city": self.city_edit.text().strip(),
            "last_foods": [s.strip() for s in self.last_foods.toPlainText().split(",") if s.strip()],
            "mood": self.mood.currentText(),
            "search_radius_m": int(self.radius.value()),
        }
        save_prefs(prefs)
        self._prefs = prefs
        self.changed.emit(prefs)
