@echo off
setlocal
title Fexiva - Local Network Server
cd /d "%~dp0"
if not exist index.html (
  echo ERROR: index.html not found. Keep this launcher in the website root.
  pause
  exit /b 1
)
where npx.cmd >nul 2>&1
if errorlevel 1 (
  echo ERROR: Install Node.js LTS from https://nodejs.org/ and try again.
  pause
  exit /b 1
)
echo.
echo Fexiva - Local Network Server
echo Local URL: http://localhost:8080
echo Network IPv4 addresses:
ipconfig | findstr /i "IPv4"
echo From another device on the same trusted network, open http://YOUR-IP:8080
echo Keep this window open. Press Ctrl+C to stop the server.
echo First launch may need internet to download http-server.
echo.
call npx --yes http-server@14.1.1 . -a 0.0.0.0 -p 8080 -c-1
if errorlevel 1 echo Server exited with an error. Check the output above.
pause
