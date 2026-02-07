"""
Monitor Checker Worker
Qo'shimcha monitorlarni aniqlash (cheating prevention)
"""
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QGuiApplication
from utils.logger import error
import sys


class MonitorWorker(QThread):
    """Qo'shimcha monitorlarni aniqlovchi worker"""
    result = pyqtSignal(bool)

    def __init__(self, interval: int = 5):
        super().__init__()
        self.interval = interval
        self._running = True
        self.last_status = None

    @staticmethod
    def check_cheating_monitor() -> int:
        """Qo'shimcha monitor borligini tekshirish"""
        try:
            screens = QGuiApplication.screens()
            return len(screens)
        except Exception as e:
            error(f"Monitor check error: {e}")
            return 1

    @staticmethod
    def get_windows_monitor_count():
        import win32api
        import win32con
        count = 0
        i = 0
        while True:
            try:
                device = win32api.EnumDisplayDevices(None, i, 0)
                if not device:
                    break
                # DISPLAY_DEVICE_ATTACHED_TO_DESKTOP flagi fizik ulanishni bildiradi
                if device.StateFlags & win32con.DISPLAY_DEVICE_ATTACHED_TO_DESKTOP:
                    count += 1
                i += 1
            except:
                break
        return count

    @staticmethod
    def get_linux_monitor_count():
        # 'python-xlib' kutubxonasi kerak
        try:
            from Xlib import display
            from Xlib.ext import randr

            d = display.Display()
            s = d.screen()
            window = s.root
            res = randr.get_screen_resources(window)

            active_outputs = 0
            for output in res.outputs:
                info = randr.get_output_info(window, output, res.config_timestamp)
                if info.connection == 0:  # 0: Connected
                    active_outputs += 1
            return active_outputs
        except Exception:
            return 1

    # @staticmethod
    # def get_macos_monitor_count():
    #     # 'pyobjc-framework-Quartz' kutubxonasi kerak
    #     try:
    #         from Quartz import CGGetActiveDisplayList
    #         # Maksimal 10 ta monitorni qidiramiz
    #         error, ids, count = CGGetActiveDisplayList(10, None, None)
    #         if error == 0:
    #             return count
    #         return 1
    #     except Exception:
    #         return 1

    def get_cheating_monitor(self) -> bool:
        import platform
        os_name = platform.system()
        print(f"OS name: {os_name}")

        if os_name == "Windows":
            return self.get_windows_monitor_count() > 1
        elif os_name == "Linux":
            count_window = self.get_linux_monitor_count()
            print(f"Linux monitor count: {count_window}")
            return count_window > 1
        elif os_name == "Darwin":  # macOS
            #return self.get_macos_monitor_count()
            return self.check_cheating_monitor() > 1
        else:
            # Agar OS aniqlanmasa, PyQt dagi mantiqiy usulga qaytamiz
            return self.check_cheating_monitor() > 1


    def run(self):
        while self._running:
            status = self.get_cheating_monitor()
            if status != self.last_status:
                self.last_status = status
                self.result.emit(status)
            self.msleep(self.interval * 1000)

    def stop(self):
        self._running = False
        self.wait()
