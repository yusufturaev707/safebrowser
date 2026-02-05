# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SafeBrowser is a Python/PyQt6 proctoring application for secure online examinations. It provides face verification, screen monitoring, keyboard blocking, and webcam recording during tests.

## Commands

```bash
# Setup virtual environment
python -m venv env
.\env\Scripts\activate  # Windows
source env/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Architecture

### Entry Point
- `main.py` - Application entry point, creates `SafeBrowserApp` which initializes PyQt6 and launches `MainWindow`

### Core Modules

**config/** - Configuration management
- `config.py` - Singleton `Config` class reading from `config.ini`. Access via `from config import config`

**core/** - Face recognition core
- `face_analyzer.py` - InsightFace wrapper (`FaceAnalyzer` class) for face detection and embedding comparison

**services/** - External communication
- `api_client.py` - REST API client for server communication (test loading, PINFL verification, warnings)

**workers/** - Background QThread workers
- `face_detector.py` - Real-time face detection from camera
- `face_recognition.py` - Face verification workers (`CPUOptimizedFaceIdWorker`, `FaceIdStaffWorker`, `Camera1Worker`)
- `internet_checker.py` - Periodic internet connectivity check
- `monitor_checker.py` - Multi-monitor detection
- `screen_recorder.py` - Screen recording during tests
- `camera_checker.py` - Camera availability verification
- `loader.py` - App and test loading workers

**ui/** - User interface (PyQt6)
- `main_window.py` - Main window with all page logic and worker coordination
- `base_ui.py` - Pure Python UI layout (replaces Qt Designer .ui files)
- `styles.py` - Material Design 3 stylesheet definitions
- `components/pages/` - Individual page widgets (`PageMain`, `PagePinfl`, `PageFace`, `PageNote`, `PageTest`, `PageNoInternet`, `PageHome`)
- `dialogs/` - Modal dialogs (`ExitDialog`, `InfoModal`, `MonitorWarningModal`, `FaceWarningModal`, `ToastManager`)

**utils/** - Utilities
- `system.py` - Cross-platform helpers (OS detection, camera backend selection, path utilities)
- `graphics.py` - UI graphics helpers (pixmap creation)
- `helpers.py` - General utilities

### Application Flow

1. Test selection (page_main) → 2. Staff face verification if enabled (page_home) → 3. PINFL input (page_pinfl) → 4. Candidate face verification (page_face) → 5. Test rules/notes (page_note) → 6. WebView test (page_test)

### Key Patterns

- **Workers pattern**: All background tasks use QThread-based workers that emit signals to communicate with the main UI
- **Page navigation**: `QStackedWidget` manages pages, navigation via `_next_page_by_name('page_name')`
- **Configuration**: Settings from `config/config.ini` accessed via singleton `config` object
- **Face verification**: InsightFace-based embedding comparison with configurable similarity threshold

## Cross-Platform Notes

- Windows: Full keyboard blocking support via `keyboard` module
- Linux: Keyboard blocking requires root privileges
- macOS: Limited keyboard blocking, requires Accessibility permissions
- Camera backends: Auto-selected per platform (DSHOW/V4L2/AVFoundation)

## Language

Code comments and UI text are in Uzbek. Variable/function names are in English.
