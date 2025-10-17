import sys
from PyQt5.QtWidgets import QApplication

# 패키지로 실행(-m)과 파일 직접 실행 모두 지원
try:
    # 패키지 컨텍스트일 때
    from .gui.main_window import MainWindow  # type: ignore
except Exception:
    # 파일 직접 실행 시: sys.path에 프로젝트 루트를 추가하고 절대 임포트
    import os
    from pathlib import Path
    ROOT = Path(__file__).resolve().parent.parent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from food_recommender.gui.main_window import MainWindow  # type: ignore


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
