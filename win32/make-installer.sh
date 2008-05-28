#!/bin/bash
# Build an installer with makensis

NSI_SCRIPT="tsnet4.nsi"

# procuce nsi script from nsi.in
sed s/\$\{VERSION\}/`./print-version.py`/ <"$NSI_SCRIPT.in" >"$NSI_SCRIPT"

PYTHON="1"

for i in $@; do

if [ "$i" == "--help" ] || [ "$i" == "-h" ]; then
  echo -e "Usage: $0 [OPTIONS ...]\n"
  echo -e "\t-h,--help\t\tShow this help screen."
  echo -e "\t--without-python\tDo not include Python and other libraries."
  echo -e "\t--force-python\t\tForce downloading Python and other libraries."
exit 1
fi

if [ "$i" == "--without-python" ]; then
  PYTHON="0"
fi

if [ "$i" == "--force-python" ]; then
  PYTHON="1"
  FORCEPY="1"
fi

done

if [ "$PYTHON" == "1" ]; then

  # Autodownload python and dependiences
  PYTHON="python-2.5.2.msi"
  PYGAME="pygame-1.8.0.win32-py2.5.msi"
  WXPYTHON="wxPython2.8-win32-unicode-2.8.7.1-py25.exe"

  if test -s "$PYTHON"; then
    if [ "$FORCEPY" == "1" ]; then echo $FORCEPY; PYTHON_DL="1"; fi
  else
    PYTHON_DL="1"
  fi

  if test -s "$PYGAME"; then
    if [ "$FORCEPY" == "1" ]; then PYGAME_DL="1"; fi
  else
    PYGAME_DL="1"
  fi

  if test -s "$WXPYTHON"; then
    if [ "$FORCEPY" == "1" ]; then WXPYTHON_DL="1"; fi
  else
    WXPYTHON_DL="1"
  fi

  # download!
  if [ "$PYTHON_DL" == "1" ]; then
    rm -f $PYTHON
    wget -c "http://www.python.org/ftp/python/2.5.2/$PYTHON"
  fi

  if [ "$PYGAME_DL" == "1" ]; then
    rm -f $PYGAME
    wget -c "http://www.pygame.org/ftp/$PYGAME"
  fi

  if [ "$WXPYTHON_DL" == "1" ]; then
    rm -f $WXPYTHON
    wget -c "http://downloads.sourceforge.net/wxpython/$WXPYTHON"
  fi


  ARG="-DPYTHON"

fi

# prepare compiled python files
_OLD="$PWD"
cd ..
py_compilefiles -f *.py
cd netframework
py_compilefiles -f *.py
cd ${_OLD}

makensis $ARG $NSI_SCRIPT
