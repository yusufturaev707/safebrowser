"""
System utilities - Tizim funksiyalari
Cross-platform qo'llab-quvvatlash
"""
import sys
import platform
import subprocess
import re
import psutil
from pathlib import Path
from typing import Tuple, Optional
from utils.logger import debug, warning, error


# ============================================
# Frozen / Base Directory
# ============================================

def is_frozen() -> bool:
    """PyInstaller frozen rejimini tekshirish"""
    return getattr(sys, 'frozen', False)


def get_base_dir() -> Path:
    """Dastur ildiz papkasini qaytarish (frozen va dev rejimda)"""
    if is_frozen():
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


# ============================================
# Platform Detection
# ============================================

def get_platform() -> str:
    """
    Operatsion tizimni aniqlash
    Returns: 'windows', 'linux', 'darwin' (macOS)
    """
    return sys.platform


def is_windows() -> bool:
    """Windows tekshirish"""
    return sys.platform == 'win32'


def is_linux() -> bool:
    """Linux tekshirish"""
    return sys.platform.startswith('linux')


def is_macos() -> bool:
    """macOS tekshirish"""
    return sys.platform == 'darwin'


def get_platform_name() -> str:
    """Odam o'qiy oladigan platform nomi"""
    if is_windows():
        return "Windows"
    elif is_macos():
        return "macOS"
    elif is_linux():
        return "Linux"
    else:
        return platform.system()


# ============================================
# Camera Backend Selection
# ============================================

def get_camera_backend() -> int:
    """
    Platformaga mos kamera backend'ini qaytarish

    Returns:
        OpenCV VideoCapture backend constant
    """
    import cv2

    if is_windows():
        # Windows: DirectShow (DSHOW) eng yaxshi ishlaydi
        return cv2.CAP_DSHOW
    elif is_linux():
        # Linux: Video4Linux2 (V4L2)
        return cv2.CAP_V4L2
    elif is_macos():
        # macOS: AVFoundation
        return cv2.CAP_AVFOUNDATION
    else:
        # Boshqa platformalar: default backend
        return cv2.CAP_ANY


def _get_camera_names_windows() -> dict:
    """
    Windows: DirectShow orqali kamera nomlarini olish
    Returns: {index: name} — masalan {0: "HD Webcam", 1: "USB Camera"}
    """
    names = {}
    try:
        import subprocess
        # PowerShell orqali kamera qurilmalarini olish
        result = subprocess.run(
            ['powershell', '-Command',
             'Get-CimInstance Win32_PnPEntity | Where-Object {$_.PNPClass -eq "Camera" -or $_.PNPClass -eq "Image"} | Select-Object -ExpandProperty Name'],
            capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode == 0 and result.stdout.strip():
            for i, name in enumerate(result.stdout.strip().splitlines()):
                name = name.strip()
                if name:
                    names[i] = name
    except Exception as e:
        debug(f"Windows kamera nomlari olishda xatolik: {e}")
    return names


def _get_camera_names_linux() -> dict:
    """
    Linux: /sys/class/video4linux orqali kamera nomlarini olish
    Returns: {index: name}
    """
    names = {}
    try:
        from pathlib import Path
        video_dir = Path("/sys/class/video4linux")
        if video_dir.exists():
            for device in sorted(video_dir.iterdir()):
                # video0, video1, ... dan indexni olish
                dev_name = device.name  # "video0"
                if dev_name.startswith("video"):
                    try:
                        idx = int(dev_name.replace("video", ""))
                    except ValueError:
                        continue
                    name_file = device / "name"
                    if name_file.exists():
                        camera_name = name_file.read_text().strip()
                        if camera_name:
                            names[idx] = camera_name
    except Exception as e:
        debug(f"Linux kamera nomlari olishda xatolik: {e}")
    return names


def _get_camera_names_macos() -> dict:
    """
    macOS: system_profiler orqali kamera nomlarini olish
    Returns: {index: name}
    """
    names = {}
    try:
        import subprocess
        result = subprocess.run(
            ['system_profiler', 'SPCameraDataType'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            idx = 0
            for line in result.stdout.splitlines():
                line = line.strip()
                # Kamera nomi indentatsiyasiz yoki bitta indentatsiya bilan keladi
                # Format: "    Camera Name:" yoki kamera nomi o'zi
                if line and not line.startswith(("Camera", "Unique", "Model", "Resolution")):
                    continue
                if line.endswith(":") and not line.startswith(("Camera", "Unique", "Model", "Resolution")):
                    camera_name = line.rstrip(":")
                    names[idx] = camera_name
                    idx += 1
            # Agar parse ishlamasa, oddiy usul
            if not names:
                idx = 0
                lines = result.stdout.splitlines()
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    # Kamera nomlari odatda 4 space indent bilan va ":" bilan tugaydi
                    if (stripped.endswith(":") and
                            not stripped.startswith(("Camera", "Cameras", "Unique", "Model", "Resolution")) and
                            len(line) - len(line.lstrip()) == 4):
                        camera_name = stripped.rstrip(":")
                        names[idx] = camera_name
                        idx += 1
    except Exception as e:
        debug(f"macOS kamera nomlari olishda xatolik: {e}")
    return names


def get_available_cameras(max_index: int = 5) -> list:
    """
    Mavjud kameralarni haqiqiy nomlari bilan ro'yxatlash

    Args:
        max_index: Tekshiriladigan maksimal kamera indeksi

    Returns:
        [(index, name), ...] — masalan [(0, "HD Webcam"), (1, "USB Camera")]
    """
    import cv2

    # Platform bo'yicha kamera nomlarini olish
    if is_windows():
        device_names = _get_camera_names_windows()
    elif is_linux():
        device_names = _get_camera_names_linux()
    elif is_macos():
        device_names = _get_camera_names_macos()
    else:
        device_names = {}

    cameras = []
    backend = get_camera_backend()

    for i in range(max_index):
        try:
            cap = cv2.VideoCapture(i, backend)
            if cap.isOpened():
                name = device_names.get(i, f"Camera {i}")
                cameras.append((i, name))
                cap.release()
        except Exception:
            continue

    return cameras


def open_camera(camera_index: int = 0, width: int = 640, height: int = 480, fps: int = 30):
    """
    Cross-platform kamera ochish

    Args:
        camera_index: Kamera indeksi (default: 0)
        width: Frame kengligi
        height: Frame balandligi
        fps: Frames per second

    Returns:
        cv2.VideoCapture instance yoki None
    """
    import cv2

    backend = get_camera_backend()

    try:
        cap = cv2.VideoCapture(camera_index, backend)

        if not cap.isOpened():
            # Fallback: default backend bilan urinish
            warning(f"Backend {backend} bilan ochilmadi, default bilan urinilmoqda...")
            cap = cv2.VideoCapture(camera_index)

        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FPS, fps)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            return cap
        else:
            warning(f"Kamera {camera_index} ochilmadi")
            return None

    except Exception as e:
        error(f"Kamera ochishda xatolik: {e}")
        return None


# ============================================
# Path Utilities
# ============================================

def get_app_data_dir() -> Path:
    """
    Platformaga mos application data papkasini qaytarish
    """
    if is_windows():
        # Windows: %APPDATA%
        import os
        app_data = os.environ.get('APPDATA', '')
        if app_data:
            return Path(app_data) / 'SafeBrowser'
        return Path.home() / 'AppData' / 'Roaming' / 'SafeBrowser'
    elif is_macos():
        # macOS: ~/Library/Application Support
        return Path.home() / 'Library' / 'Application Support' / 'SafeBrowser'
    else:
        # Linux: ~/.local/share
        return Path.home() / '.local' / 'share' / 'safebrowser'


def get_config_dir() -> Path:
    """
    Platformaga mos config papkasini qaytarish
    """
    if is_windows():
        return get_app_data_dir() / 'config'
    elif is_macos():
        return Path.home() / 'Library' / 'Preferences' / 'SafeBrowser'
    else:
        # Linux: ~/.config
        return Path.home() / '.config' / 'safebrowser'


def get_models_dir() -> Path:
    """
    InsightFace modellar papkasini qaytarish
    """
    # Loyiha papkasida modellar
    project_root = get_base_dir()
    models_dir = project_root / 'insightface_models'

    # Agar mavjud bo'lsa
    if models_dir.exists():
        return models_dir

    # Aks holda app data papkasida
    app_models = get_app_data_dir() / 'models' / 'insightface'
    app_models.mkdir(parents=True, exist_ok=True)
    return app_models


def get_recordings_dir() -> Path:
    """
    Yozuvlar papkasini qaytarish
    """
    if is_windows():
        # Windows: Videos papkasi
        videos = Path.home() / 'Videos' / 'SafeBrowser'
    elif is_macos():
        # macOS: Movies papkasi
        videos = Path.home() / 'Movies' / 'SafeBrowser'
    else:
        # Linux: Videos papkasi
        videos = Path.home() / 'Videos' / 'SafeBrowser'

    videos.mkdir(parents=True, exist_ok=True)
    return videos


# ============================================
# Disk Utilities
# ============================================

def get_disk_with_most_free_space() -> Tuple[Optional[str], int]:
    """
    Eng ko'p bo'sh joy bo'lgan diskni aniqlash

    Returns:
        Tuple[path, free_bytes]
    """
    max_free = 0
    best_path = None

    partitions = psutil.disk_partitions()
    for part in partitions:
        try:
            usage = psutil.disk_usage(part.mountpoint)
            if usage.free > max_free:
                max_free = usage.free
                best_path = part.mountpoint
        except PermissionError:
            continue

    return best_path, max_free


def _parse_windows_ipconfig() -> str:
    """
    Windows: ipconfig outputdan gateway bilan bir subnetdagi IPv4 ni topish.
    vEthernet/WSL adapterlarni o'tkazib yuboradi.
    """
    result = subprocess.run(
        ['ipconfig'], capture_output=True, timeout=5,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    text = result.stdout.decode('cp866', errors='replace')
    lines = text.splitlines()

    # Adapter bloklarini ajratish (bo'sh qator = blok chegarasi, header = indent yo'q)
    adapter_blocks = []
    current_header = ""
    current_lines = []
    for line in lines:
        if line and not line.startswith(' '):
            # Yangi adapter header
            if current_lines:
                adapter_blocks.append((current_header, current_lines))
            current_header = line
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        adapter_blocks.append((current_header, current_lines))

    for header, block_lines in adapter_blocks:
        # Virtual adapterlarni o'tkazish
        if any(x in header for x in ['vEthernet', 'WSL', 'Loopback', 'VPN']):
            continue

        # Blokdan IPv4 va Gateway olish
        ipv4_list = []
        gateway = None
        for line in block_lines:
            ip_match = re.search(r'IPv4.*?:\s*(\d+\.\d+\.\d+\.\d+)', line)
            if ip_match:
                ipv4_list.append(ip_match.group(1))
                continue
            # Gateway qatori: subnet emas (255.x bo'lmagan), IPv4 emas
            if 'IPv4' not in line and '255.' not in line:
                gw_match = re.search(r':\s*(\d+\.\d+\.\d+\.\d+)', line)
                if gw_match:
                    gateway = gw_match.group(1)

        if not gateway or not ipv4_list:
            continue

        # Gateway bilan bir subnetdagi IP ni tanlash (birinchi 3 oktet mos)
        gw_prefix = gateway.rsplit('.', 1)[0]  # "192.168.0"
        for ip in ipv4_list:
            if ip.rsplit('.', 1)[0] == gw_prefix:
                return ip

        # Agar subnet match bo'lmasa, oxirgi IPv4 ni qaytarish
        return ipv4_list[-1]

    return ""


def get_ip_address() -> str:
    """
    OS darajasida local IP addressni olish
    Windows: ipconfig, Linux: ip route, macOS: ipconfig getifaddr
    """
    try:
        if is_windows():
            ip = _parse_windows_ipconfig()
            if ip:
                return ip

        elif is_linux():
            result = subprocess.run(
                ['ip', 'route', 'get', '8.8.8.8'],
                capture_output=True, text=True, timeout=5
            )
            match = re.search(r'src\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
            if match:
                return match.group(1)

        elif is_macos():
            for iface in ('en0', 'en1'):
                result = subprocess.run(
                    ['ipconfig', 'getifaddr', iface],
                    capture_output=True, text=True, timeout=5
                )
                ip = result.stdout.strip()
                if ip and re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                    return ip

    except Exception as e:
        debug(f"OS orqali IP olishda xatolik: {e}")

    return "0.0.0.0"


def get_mac_address() -> str:
    """
    OS darajasida MAC addressni olish (XX:XX:XX:XX:XX:XX formatda)
    Windows: getmac, Linux: ip link, macOS: ifconfig
    """
    try:
        if is_windows():
            result = subprocess.run(
                ['powershell', '-Command',
                 "(Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object -First 1).MacAddress"],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            mac = result.stdout.strip()
            if mac:
                # Windows format: AA-BB-CC-DD-EE-FF -> AA:BB:CC:DD:EE:FF
                return mac.replace('-', ':').lower()

        elif is_linux():
            # Default route interface ni topib, uning MAC ini olish
            result = subprocess.run(
                ['ip', 'route', 'get', '8.8.8.8'],
                capture_output=True, text=True, timeout=5
            )
            dev_match = re.search(r'dev\s+(\S+)', result.stdout)
            if dev_match:
                iface = dev_match.group(1)
                result = subprocess.run(
                    ['ip', 'link', 'show', iface],
                    capture_output=True, text=True, timeout=5
                )
                mac_match = re.search(r'link/ether\s+([\da-f:]+)', result.stdout)
                if mac_match:
                    return mac_match.group(1)

        elif is_macos():
            # en0 yoki en1 interface MAC ni olish
            result = subprocess.run(
                ['ifconfig', 'en0'],
                capture_output=True, text=True, timeout=5
            )
            mac_match = re.search(r'ether\s+([\da-f:]+)', result.stdout)
            if mac_match:
                return mac_match.group(1)
            # en0 bo'lmasa en1
            result = subprocess.run(
                ['ifconfig', 'en1'],
                capture_output=True, text=True, timeout=5
            )
            mac_match = re.search(r'ether\s+([\da-f:]+)', result.stdout)
            if mac_match:
                return mac_match.group(1)

    except Exception as e:
        debug(f"OS orqali MAC olishda xatolik: {e}")

    return "00:00:00:00:00:00"


def get_system_info() -> dict:
    """Tizim haqida ma'lumot"""
    return {
        "cpu_count": psutil.cpu_count(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "memory_percent": psutil.virtual_memory().percent,
    }
