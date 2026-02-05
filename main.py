import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from utils.logger import get_logger, info, error

# Logger ni ishga tushirish
logger = get_logger()


class SafeBrowserApp:
    def __init__(self, argv: list = None):
        self.argv = argv or sys.argv
        self.app = None
        self.main_window = None

    def run(self) -> int:
        """Dasturni ishga tushirish"""
        try:
            info("SafeBrowser ishga tushmoqda...")

            # High DPI scaling
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )

            self.app = QApplication(self.argv)
            self.app.setApplicationName("SafeBrowser")
            self.app.setApplicationVersion("1.0.0")
            self.app.setOrganizationName("SafeBrowser Team")

            # Main window
            self.main_window = MainWindow()
            self.main_window.show()

            info("SafeBrowser muvaffaqiyatli ishga tushdi")
            return self.app.exec()

        except Exception as e:
            error(f"SafeBrowser ishga tushishda xatolik: {e}")
            raise

    @staticmethod
    def create_app(argv: list = None) -> 'SafeBrowserApp':
        """Factory method"""
        return SafeBrowserApp(argv)


def main():
    """Entry point"""
    app = SafeBrowserApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()