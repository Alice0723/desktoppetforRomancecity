@echo off
chcp 65001 >nul
echo ============================================
echo   火辣辣 桌宠 - 打包脚本
echo ============================================
echo.

REM 使用标准 Python 环境（非 conda）避免 DLL 问题
set PYTHON=C:\Users\dophi\AppData\Roaming\uv\python\cpython-3.14.3-windows-x86_64-none\python.exe

if not exist "%PYTHON%" (
    echo [错误] 找不到 Python: %PYTHON%
    echo 请先通过 uv 安装 Python: uv python install 3.14
    pause
    exit /b 1
)

echo [1/5] 检查依赖...
%PYTHON% -m pip install pyinstaller pynput pywin32 PyQt5 --break-system-packages --quiet
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)

echo [2/5] 验证 pynput 安装...
%PYTHON% -c "from pynput import keyboard, mouse; print('pynput OK')"
if errorlevel 1 (
    echo [错误] pynput 安装异常
    pause
    exit /b 1
)

echo [3/5] 清理旧的打包文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec

echo [4/5] 开始打包（单文件模式）...
echo.
echo 注意：打包过程可能需要 1-3 分钟，请耐心等待...
echo.

%PYTHON% -m PyInstaller ^
    --noconsole ^
    --onefile ^
    --name "HuolalaPet" ^
    --add-data "assets;assets" ^
    --hidden-import=pynput ^
    --hidden-import=pynput.keyboard ^
    --hidden-import=pynput.keyboard._win32 ^
    --hidden-import=pynput.mouse ^
    --hidden-import=pynput.mouse._win32 ^
    --hidden-import=pynput._util ^
    --hidden-import=pynput._util.win32 ^
    --hidden-import=win32api ^
    --hidden-import=win32con ^
    --hidden-import=win32event ^
    --hidden-import=win32file ^
    --hidden-import=win32gui ^
    --hidden-import=win32process ^
    --hidden-import=pywintypes ^
    --hidden-import=pythoncom ^
    --collect-submodules pynput ^
    main.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！尝试使用文件夹模式...
    echo.
    
    REM 回退：使用文件夹模式
    if exist "build" rmdir /s /q build
    if exist "dist" rmdir /s /q dist
    if exist "*.spec" del /q *.spec
    
    %PYTHON% -m PyInstaller ^
        --noconsole ^
        --onedir ^
        --name "HuolalaPet" ^
        --add-data "assets;assets" ^
        --hidden-import=pynput ^
        --hidden-import=pynput.keyboard ^
        --hidden-import=pynput.keyboard._win32 ^
        --hidden-import=pynput.mouse ^
        --hidden-import=pynput.mouse._win32 ^
        --hidden-import=pynput._util ^
        --hidden-import=pynput._util.win32 ^
        --hidden-import=win32api ^
        --hidden-import=win32con ^
        --hidden-import=win32gui ^
        --hidden-import=pywintypes ^
        --hidden-import=pythoncom ^
        --collect-submodules pynput ^
        main.py
    
    if errorlevel 1 (
        echo [错误] 打包失败！
        pause
        exit /b 1
    )
)

echo.
echo [5/5] 完成！
echo.

if exist "dist\HuolalaPet.exe" (
    echo ============================================
    echo   打包完成！
    echo   单文件版本: dist\HuolalaPet.exe
    echo ============================================
    echo.
    echo 提示：
    echo   - 双击 exe 即可运行
    echo   - 数据会保存在 exe 同目录
    echo   - 首次启动可能较慢（约 3-5 秒）
) else if exist "dist\HuolalaPet\HuolalaPet.exe" (
    echo ============================================
    echo   打包完成！（文件夹模式）
    echo   位置: dist\HuolalaPet\
    echo ============================================
    echo.
    echo 提示：
    echo   - 将整个文件夹复制给朋友
    echo   - 双击 HuolalaPet.exe 运行
) else (
    echo [错误] 未找到生成的 exe 文件
)

echo.
pause
