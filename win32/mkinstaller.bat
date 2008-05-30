@echo off
Rem Prepare the files for creating the installer

set NSI_SCRIPT=tsnet4.nsi
set PYTHON=python-2.5.2.msi
set PYGAME=pygame-1.8.0.win32-py2.5.msi
set WXPYTHON=wxPython2.8-win32-unicode-2.8.7.1-py25.exe

set PYTHON_URL=http://www.python.org/ftp/python/2.5.2/%PYTHON%
set PYGAME_URL=http://www.pygame.org/ftp/%PYGAME%
set WXPYTHON_URL=http://downloads.sourceforge.net/wxpython/%WXPYTHON%

REM Detect version
echo Checking version...
start /B /WAIT print-version.py tmp-version

for /F ""; %%v in (tmp-version) do SET TSNET4_VERSION=%%v
del tmp-version

echo Installer for version %TSNET4_VERSION%
set NSIS_ARGS=

if /I not "%1"=="/python" goto :compile

REM Check python packages
echo Checking dependencies...

if exist %PYTHON% goto cont1
echo.
echo Download Python from:
echo %PYTHON_URL%

:cont1
if exist %PYGAME% goto cont2
echo.
echo Download Pygame from:
echo %PYGAME_URL%

:cont2
if exist %WXPYTHON% goto cont3
echo.
echo Download wxPython from:
echo %WXPYTHON_URL%

:cont3
set NSIS_ARGS=/DPYTHON

:compile
REM compile python files -> pyc
start /B /WAIT compile.py

:finish
set NSIS_ARGS=%NSIS_ARGS% /DTSNET4_VERSION=%TSNET4_VERSION% %NSI_SCRIPT%

echo.
echo Run NSIS with these arguments:
echo.
echo makensis %NSIS_ARGS%
echo.

pause
