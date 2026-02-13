@echo off
echo ============================================
echo  SafeBrowser EXE Build
echo ============================================
echo.

:: Virtual environment aktivatsiya
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist "env\Scripts\activate.bat" (
    call env\Scripts\activate.bat
) else (
    echo [XATO] Virtual environment topilmadi!
    echo .venv yoki env papkasi mavjud emasligini tekshiring.
    pause
    exit /b 1
)

:: PyInstaller mavjudligini tekshirish
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller o'rnatilmoqda...
    pip install pyinstaller
)

echo.
echo [INFO] Build boshlanmoqda...
echo.

pyinstaller safebrowser.spec --noconfirm --clean

if errorlevel 1 (
    echo.
    echo [XATO] Build muvaffaqiyatsiz tugadi!
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Build muvaffaqiyatli tugadi!
echo  Natija: dist\SafeBrowser\SafeBrowser.exe
echo ============================================
pause
