@echo off
echo ========================================
echo   PixCI CLI Builder
echo ========================================
echo.

echo [1/2] Installing dependencies...
uv pip install pyinstaller pillow typer rich

echo.
echo [2/2] Building pixci-cli.exe...
uv run build_exe.py --mode cli

echo.
echo ========================================
echo   Build Complete!
echo ========================================
echo.
echo File location: dist\pixci-cli.exe
echo.
echo You can now copy pixci-cli.exe anywhere and run it!
echo.
pause
