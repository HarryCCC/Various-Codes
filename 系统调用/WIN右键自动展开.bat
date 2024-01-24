@echo off
echo 以管理员身份运行此脚本以继续...
echo.

chcp 65001

:: 检查脚本是否以管理员身份运行
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

if '%errorlevel%' NEQ '0' (
    echo 请以管理员身份运行此脚本.
    echo.
    echo 正在退出...
    goto end
)

:: 添加注册表项
reg.exe add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /f /ve

:: 重启资源管理器
taskkill /f /im explorer.exe
start explorer.exe

:end
echo 操作完成.
pause
