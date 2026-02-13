"""
Logger utility - SafeBrowser uchun logging tizimi
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _get_log_dir() -> Path:
    """
    OS ga mos log papkasini aniqlash

    Windows:  %LOCALAPPDATA%/SafeBrowser/logs
    Linux:    ~/.local/share/safebrowser/logs
    macOS:    ~/Library/Logs/SafeBrowser
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "SafeBrowser" / "logs"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Logs" / "SafeBrowser"
    else:
        return Path.home() / ".local" / "share" / "safebrowser" / "logs"


def setup_logger(
    name: str = "SafeBrowser",
    log_dir: str = None,
    log_level: int = logging.DEBUG,
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Logger yaratish va sozlash

    Args:
        name: Logger nomi
        log_dir: Log fayllar joylashadigan papka (None bo'lsa OS standart joyi)
        log_level: Logging darajasi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Har bir log fayl maksimal hajmi
        backup_count: Saqlanadigan eski log fayllar soni

    Returns:
        logging.Logger: Sozlangan logger
    """
    # Logger olish
    logger = logging.getLogger(name)

    # Agar allaqachon handler qo'shilgan bo'lsa, qayta qo'shmaslik
    if logger.handlers:
        return logger

    logger.setLevel(log_level)

    # Log papkasini yaratish
    log_path = Path(log_dir) if log_dir else _get_log_dir()
    log_path.mkdir(parents=True, exist_ok=True)

    # Log fayl nomi - kunlik
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"safebrowser_{today}.log"

    # Formatter - log format
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler - faylga yozish (rotating)
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler - terminalga chiqarish
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Consolega faqat INFO va yuqori
    console_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Propagate off - parent logger ga uzatmaslik
    logger.propagate = False

    logger.info(f"Logger ishga tushdi: {log_file}")

    return logger


# Global logger instance
_logger = None


def get_logger() -> logging.Logger:
    """
    Global logger olish (singleton pattern)

    Returns:
        logging.Logger: SafeBrowser logger
    """
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger


# Qisqa metodlar - import qilish oson bo'lishi uchun
def debug(msg: str, *args, **kwargs):
    """Debug level log"""
    get_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """Info level log"""
    get_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """Warning level log"""
    get_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """Error level log"""
    get_logger().error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """Critical level log"""
    get_logger().critical(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs):
    """Exception log - avtomatik stack trace qo'shadi"""
    get_logger().exception(msg, *args, **kwargs)
