"""
Configuration Management
Dastur sozlamalari
"""
import os
import configparser
from pathlib import Path
from typing import Optional


# Paths
CONFIG_FILE = Path(__file__).parent / 'config.ini'


class Config:
    """Dastur sozlamalarini boshqarish"""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Konfiguratsiyani yuklash"""
        self._config = configparser.ConfigParser()

        # Fayl mavjud bo'lsa, o'qish
        if CONFIG_FILE.exists():
            try:
                self._config.read(CONFIG_FILE, encoding='utf-8')  # ✅ encoding qo'shing
                print(f"✅ Config yuklandi: {CONFIG_FILE}")
            except Exception as e:
                print(f"❌ Config yuklashda xato: {e}")
        else:
            print(f"⚠️ Config fayl topilmadi: {CONFIG_FILE}")
            self._create_default_config()  # ✅ Default yaratish

    def _create_default_config(self):
        """Default config yaratish"""
        self._config['AUTH'] = {
            'admin_password': '123'
        }
        self._config['API'] = {
            'base_url': 'http://127.0.0.1:8000/api/v1/'
        }
        self.save()

    def get(self, section: str, key: str, fallback: str = None) -> Optional[str]:
        """Qiymat olish"""
        try:
            return self._config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback

    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Integer qiymat olish"""
        try:
            return self._config.getint(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback

    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Boolean qiymat olish"""
        try:
            return self._config.getboolean(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback

    def set(self, section: str, key: str, value: str):
        """Qiymat o'rnatish"""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = str(value)

    def save(self):
        """Config faylga saqlash"""
        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                self._config.write(f)
            print(f"✅ Config saqlandi: {CONFIG_FILE}")
        except Exception as e:
            print(f"❌ Config saqlashda xato: {e}")

    # Shortcut properties
    @property
    def api_base_url(self) -> str:
        """API base URL"""
        return self.get("API", "base_url", fallback="http://127.0.0.1:8000/api/v1/")

    @property
    def admin_password(self) -> str:
        """Admin paroli"""
        return self.get("AUTH", "admin_password", fallback="123")

    # Face Monitoring properties
    @property
    def face_detection_interval(self) -> int:
        """Face detection intervali (soniyada)"""
        return self.getint("FACE_MONITORING", "detection_interval", fallback=30)

    @property
    def face_detection_max_fail(self) -> int:
        """Face detection maksimal fail soni"""
        return self.getint("FACE_MONITORING", "detection_max_fail", fallback=5)

    @property
    def face_identification_interval(self) -> int:
        """Face identification intervali (soniyada)"""
        return self.getint("FACE_MONITORING", "identification_interval", fallback=60)

    @property
    def face_identification_max_fail(self) -> int:
        """Face identification maksimal fail soni"""
        return self.getint("FACE_MONITORING", "identification_max_fail", fallback=5)

    @property
    def face_warning_timeout(self) -> int:
        """Warning timeout (soniyada)"""
        return self.getint("FACE_MONITORING", "warning_timeout", fallback=30)


# Singleton instance
config = Config()
