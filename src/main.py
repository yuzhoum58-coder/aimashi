"""
多模态医学影像手动配准浏览器 — 主入口
Python桌面端 (PySide6 + VTK + SimpleITK)
"""
import sys
from PySide6.QtWidgets import QApplication
from src.viewer.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("多模态医学影像手动配准浏览器")
    app.setOrganizationName("Hermes Medical Imaging")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
