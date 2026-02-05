"""
Graphics utilities - QPainter bilan rasm yaratish
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QFont, QPen, QBrush,
    QLinearGradient, QRadialGradient
)


def create_success_pixmap(width: int = 520, height: int = 390) -> QPixmap:
    """
    Yuz tasdiqlanganda ko'rsatiladigan success effekti
    """
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Background gradient - yashil
    gradient = QLinearGradient(0, 0, 0, height)
    gradient.setColorAt(0, QColor(16, 185, 129, 230))
    gradient.setColorAt(1, QColor(5, 150, 105, 230))
    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(0, 0, width, height, 20, 20)

    # Checkmark doira
    cx, cy = width // 2, height // 2 - 30
    radius = 70

    # Oq doira
    painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
    painter.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)

    # Checkmark
    pen = QPen(QColor(255, 255, 255))
    pen.setWidth(8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)

    # Checkmark chiziqlari
    painter.drawLine(cx - 30, cy, cx - 5, cy + 25)
    painter.drawLine(cx - 5, cy + 25, cx + 35, cy - 20)

    # "TASDIQLANDI" text
    painter.setPen(QColor(255, 255, 255))
    font = QFont("Segoe UI", 28, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(0, cy + radius + 30, width, 50,
                     Qt.AlignmentFlag.AlignCenter, "TASDIQLANDI")

    # Subtitle
    font.setPointSize(14)
    font.setWeight(QFont.Weight.Normal)
    painter.setFont(font)
    painter.setPen(QColor(255, 255, 255, 200))
    painter.drawText(0, cy + radius + 75, width, 30,
                     Qt.AlignmentFlag.AlignCenter, "Yuz muvaffaqiyatli aniqlandi")

    painter.end()
    return pixmap


def create_id_card_pixmap(width: int = 320, height: int = 200) -> QPixmap:
    """
    JSHSHIR sahifasi uchun ID karta dizayni
    """
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Karta background - gradient
    gradient = QLinearGradient(0, 0, width, height)
    gradient.setColorAt(0, QColor(59, 130, 246))
    gradient.setColorAt(0.5, QColor(37, 99, 235))
    gradient.setColorAt(1, QColor(29, 78, 216))
    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(0, 0, width, height, 16, 16)

    # Chip (oltin rang)
    chip_x, chip_y = 25, 50
    chip_w, chip_h = 50, 40
    chip_gradient = QLinearGradient(chip_x, chip_y, chip_x + chip_w, chip_y + chip_h)
    chip_gradient.setColorAt(0, QColor(251, 191, 36))
    chip_gradient.setColorAt(0.5, QColor(245, 158, 11))
    chip_gradient.setColorAt(1, QColor(217, 119, 6))
    painter.setBrush(QBrush(chip_gradient))
    painter.drawRoundedRect(chip_x, chip_y, chip_w, chip_h, 6, 6)

    # Chip chiziqlari
    painter.setPen(QPen(QColor(180, 120, 20), 1))
    painter.drawLine(chip_x + 15, chip_y + 5, chip_x + 15, chip_y + chip_h - 5)
    painter.drawLine(chip_x + 35, chip_y + 5, chip_x + 35, chip_y + chip_h - 5)
    painter.drawLine(chip_x + 5, chip_y + 20, chip_x + chip_w - 5, chip_y + 20)

    # User icon placeholder
    icon_x = width - 90
    icon_y = 35
    icon_size = 65
    painter.setBrush(QBrush(QColor(255, 255, 255, 30)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(icon_x, icon_y, icon_size, icon_size, 8, 8)

    # User silhouette
    painter.setBrush(QBrush(QColor(255, 255, 255, 80)))
    head_r = 12
    painter.drawEllipse(icon_x + icon_size // 2 - head_r, icon_y + 12, head_r * 2, head_r * 2)
    painter.drawEllipse(icon_x + 12, icon_y + 38, icon_size - 24, 22)

    # "ID CARD" text
    painter.setPen(QColor(255, 255, 255, 180))
    font = QFont("Segoe UI", 10, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(25, 25, "ID CARD")

    # JSHSHIR placeholder
    painter.setPen(QColor(255, 255, 255))
    font.setPointSize(16)
    font.setWeight(QFont.Weight.Bold)
    font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
    painter.setFont(font)
    painter.drawText(25, height - 55, "JSHSHIR")

    # Number placeholder
    font.setPointSize(20)
    font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
    painter.setFont(font)
    painter.drawText(25, height - 25, "_ _ _ _ _ _ _ _ _ _ _ _ _ _")

    painter.end()
    return pixmap


def create_lock_icon(width: int = 70, height: int = 70, color: str = None) -> QPixmap:
    """
    Qulf ikonkasi chizish - katta va aniq
    color: hex rang kodi (masalan "#3AA985" - mint yashil)
    """
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Markazlash uchun offset
    cx = width // 2
    cy = height // 2 + 3

    # Rang tanlash
    if color:
        main_color = QColor(color)
        # Darker variant for gradient
        dark_color = main_color.darker(120)
        border_color = main_color.darker(150)
        hole_color = main_color.darker(200)
    else:
        main_color = QColor(217, 119, 6)
        dark_color = QColor(180, 83, 9)
        border_color = QColor(120, 53, 15)
        hole_color = QColor(68, 51, 17)

    # Qulf halqasi - outline style (HTML ga mos)
    pen = QPen(main_color)
    pen.setWidth(int(width * 0.12))  # Proporsional qalinlik
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    arc_w = int(width * 0.45)
    arc_h = int(height * 0.42)
    arc_x = cx - arc_w // 2
    arc_y = cy - int(height * 0.38)
    painter.drawArc(arc_x, arc_y, arc_w, arc_h, 0, 180 * 16)

    # Qulf tanasi - outline style (HTML ga mos)
    body_w = int(width * 0.6)
    body_h = int(height * 0.45)
    body_x = cx - body_w // 2
    body_y = cy - int(height * 0.05)

    pen.setWidth(int(width * 0.12))
    painter.setPen(pen)
    # Ichki fill - shaffof rang bilan
    painter.setBrush(QBrush(QColor(main_color.red(), main_color.green(), main_color.blue(), 20)))
    painter.drawRoundedRect(body_x, body_y, body_w, body_h, int(width * 0.12), int(width * 0.12))

    # Kalit teshigi (vertikal chiziq)
    pen.setWidth(int(width * 0.12))
    painter.setPen(pen)
    key_x = cx
    key_y1 = body_y + int(body_h * 0.35)
    key_y2 = body_y + int(body_h * 0.7)
    painter.drawLine(key_x, key_y1, key_x, key_y2)

    painter.end()
    return pixmap
