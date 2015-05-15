; Script generated by the HM NIS Edit Script Wizard.

; Trick for aborting if parameters are wrong
!ifndef TSNET4_VERSION
Abort
!endif

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "TressetteNetwork4"
!define PRODUCT_VERSION "${TSNET4_VERSION}"
!define PRODUCT_PUBLISHER "GtkDC Team"
!define PRODUCT_WEB_SITE "http://home.gna.org/tsnet4"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PRODUCT_STARTMENU_REGVAL "NSIS:StartMenuDir"
!define PRODUCT_URI_HANDLER "tsnet4"
!define PYTHON_PATH_KEY "Software\Python\PythonCore\2.5\InstallPath"
Var PYTHON_EXE


; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "..\COPYING"
; Components page
!insertmacro MUI_PAGE_COMPONENTS
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Start menu page
var ICONS_GROUP
!define MUI_STARTMENUPAGE_NODISABLE
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "TressetteNetwork4"
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "${PRODUCT_STARTMENU_REGVAL}"
!insertmacro MUI_PAGE_STARTMENU Application $ICONS_GROUP
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
;!define MUI_FINISHPAGE_NOAUTOCLOSE
;!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "Italian"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
!ifdef PYTHON
OutFile "tsnet4-${PRODUCT_VERSION}.exe"
!else
OutFile "tsnet4-${PRODUCT_VERSION}-no-python.exe"
!endif
InstallDir "$PROGRAMFILES\TressetteNetwork4"
ShowInstDetails show
ShowUnInstDetails show

Section "TressetteNetwork4" SEC01
  SectionIn RO
  SetOutPath "$INSTDIR"
  SetOverwrite try
  File "..\graphics.pyc"
  File "..\launcher.pyc"
  File "..\main.pyc"
  File "..\miscgui.pyc"
  File "..\objects.pyc"
  File "..\player.pyc"
  File "..\protocol.pyc"
  File "..\server.pyc"
  File "..\__init__.pyc"
  File "..\client.pyc"
  File "..\deck.pyc"

  SetOutPath "$INSTDIR\netframework"
  File "..\netframework\connection.pyc"
  File "..\netframework\interfaces.pyc"
  File "..\netframework\loop.pyc"
  File "..\netframework\miscnet.pyc"
  File "..\netframework\__init__.pyc"

  SetOutPath "$INSTDIR\data"
  File "..\data\logo.png"
  File "..\data\tsnet4.png"

  SetOutPath "$INSTDIR"

; Shortcuts
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  CreateDirectory "$SMPROGRAMS\$ICONS_GROUP"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\TressetteNetwork4.lnk" "$INSTDIR\launcher.pyc"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Avvia server.lnk" "$INSTDIR\main.pyc" "standalone"

  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section "Carte piacentine" SEC02
  SectionIn RO
  SetOutPath "$INSTDIR\data\cards"
  File "..\data\cards\piacentine1.jpg"
  File "..\data\cards\piacentine10.jpg"
  File "..\data\cards\piacentine11.jpg"
  File "..\data\cards\piacentine12.jpg"
  File "..\data\cards\piacentine13.jpg"
  File "..\data\cards\piacentine14.jpg"
  File "..\data\cards\piacentine15.jpg"
  File "..\data\cards\piacentine16.jpg"
  File "..\data\cards\piacentine17.jpg"
  File "..\data\cards\piacentine18.jpg"
  File "..\data\cards\piacentine19.jpg"
  File "..\data\cards\piacentine2.jpg"
  File "..\data\cards\piacentine20.jpg"
  File "..\data\cards\piacentine21.jpg"
  File "..\data\cards\piacentine22.jpg"
  File "..\data\cards\piacentine23.jpg"
  File "..\data\cards\piacentine24.jpg"
  File "..\data\cards\piacentine25.jpg"
  File "..\data\cards\piacentine26.jpg"
  File "..\data\cards\piacentine27.jpg"
  File "..\data\cards\piacentine28.jpg"
  File "..\data\cards\piacentine29.jpg"
  File "..\data\cards\piacentine3.jpg"
  File "..\data\cards\piacentine30.jpg"
  File "..\data\cards\piacentine31.jpg"
  File "..\data\cards\piacentine32.jpg"
  File "..\data\cards\piacentine33.jpg"
  File "..\data\cards\piacentine34.jpg"
  File "..\data\cards\piacentine35.jpg"
  File "..\data\cards\piacentine36.jpg"
  File "..\data\cards\piacentine37.jpg"
  File "..\data\cards\piacentine38.jpg"
  File "..\data\cards\piacentine39.jpg"
  File "..\data\cards\piacentine4.jpg"
  File "..\data\cards\piacentine40.jpg"
  File "..\data\cards\piacentine41.jpg"
  File "..\data\cards\piacentine5.jpg"
  File "..\data\cards\piacentine6.jpg"
  File "..\data\cards\piacentine7.jpg"
  File "..\data\cards\piacentine8.jpg"
  File "..\data\cards\piacentine9.jpg"
SectionEnd

!ifdef PYTHON
Section "Python 2.5" SEC03
  SetOutPath "$TEMP"
  SetOverwrite on
  File /oname=python.msi "python-2.5*.msi"

  ExecWait '"msiexec" /i "$TEMP\python.msi" /norestart /quiet'
  Delete "$TEMP\python.msi"
SectionEnd

Section "Pygame 1.8" SEC04
  SetOutPath "$TEMP"
  SetOverwrite on
  File /oname=pygame.msi "pygame-1.8*.msi"

  ExecWait '"msiexec" /i "$TEMP\pygame.msi" /norestart /quiet'
  Delete "$TEMP\pygame.msi"
SectionEnd

Section "wxPython 2.8" SEC05
  SetOutPath "$TEMP"
  SetOverwrite on
  File /oname=wxpython.exe "wxPython2.8*.exe"

  ExecWait '"$TEMP\wxpython.exe" /verysilent /norestart /suppressmsgboxes'
  Delete "$TEMP\wxpython.exe"
SectionEnd
!endif

Section "Registra URL ${PRODUCT_URI_HANDLER}://" SEC06
  DetailPrint "Registro il gestore per gli URI ${PRODUCT_URI_HANDLER}://"
  DeleteRegKey HKCR "${PRODUCT_URI_HANDLER}"
  WriteRegStr HKCR "${PRODUCT_URI_HANDLER}" "" "URL:${PRODUCT_URI_HANDLER}"
  WriteRegStr HKCR "${PRODUCT_URI_HANDLER}" "URL Protocol" ""
  WriteRegStr HKCR "${PRODUCT_URI_HANDLER}\DefaultIcon" "" "$PYTHON_EXE\python.exe"
  WriteRegStr HKCR "${PRODUCT_URI_HANDLER}\shell" "" ""
  WriteRegStr HKCR "${PRODUCT_URI_HANDLER}\shell\Open" "" ""
  WriteRegStr HKCR "${PRODUCT_URI_HANDLER}\shell\Open\command" "" "$PYTHON_EXE\python.exe $INSTDIR\main.pyc server=%1"
SectionEnd

Section "Icona sul Desktop" SEC07
  SetOutPath $INSTDIR
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  CreateShortCut "$DESKTOP\TressetteNetwork4.lnk" "$INSTDIR\launcher.pyc"
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section -AdditionalIcons
  SetOutPath $INSTDIR
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Progetto TSNet4.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Disinstalla.lnk" "$INSTDIR\uninst.exe"
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

Function .onInit
  ReadRegStr $PYTHON_EXE HKLM ${PYTHON_PATH_KEY} ""
  StrCmp $PYTHON_EXE "" notPython contPy

  ReadRegStr $PYTHON_EXE HKCU ${PYTHON_PATH_KEY} ""
  StrCmp $PYTHON_EXE "" notPython

contPy:
!ifdef PYTHON
  SectionGetFlags ${SEC03} $1
  IntOp $1 $1 - ${SF_SELECTED}
  SectionSetFlags ${SEC03} $1

!endif
notPython:
!ifdef PYTHON
  IfFileExists "$PYTHON_EXE\Lib\site-packages\pygame*" 0 notPygame

  SectionGetFlags ${SEC04} $1
  IntOp $1 $1 - ${SF_SELECTED}
  SectionSetFlags ${SEC04} $1

notPygame:
  IfFileExists "$PYTHON_EXE\Lib\site-packages\wx.pth" 0 notWx

  SectionGetFlags ${SEC05} $1
  IntOp $1 $1 - ${SF_SELECTED}
  SectionSetFlags ${SEC05} $1

notWx:
!endif
FunctionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "Installa il gioco e i relativi dati."
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "Installa il set di carte piacentine."
!ifdef PYTHON
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC03} "Installa Python 2.5 per Windows."
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC04} "Installa la libreria Pygame - necessaria per il gioco."
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC05} "Installa la libreria wxPython - necessaria per l'interfaccia grafica."
!endif
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC06} "Installa il gestore per gli URL ${PRODUCT_URI_HANDLER}://."
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC07} "Crea un collegamento a TressetteNetwork4 sul desktop."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Sei sicuro di voler completamente rimuovere $(^Name) e tutti i suoi componenti?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  !insertmacro MUI_STARTMENU_GETFOLDER "Application" $ICONS_GROUP
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\deck.pyc"
  Delete "$INSTDIR\client.pyc"
  Delete "$INSTDIR\__init__.pyc"
  Delete "$INSTDIR\netframework\__init__.pyc"
  Delete "$INSTDIR\netframework\miscnet.pyc"
  Delete "$INSTDIR\netframework\loop.pyc"
  Delete "$INSTDIR\netframework\interfaces.pyc"
  Delete "$INSTDIR\netframework\connection.pyc"
  Delete "$INSTDIR\data\cards\piacentine9.jpg"
  Delete "$INSTDIR\data\cards\piacentine8.jpg"
  Delete "$INSTDIR\data\cards\piacentine7.jpg"
  Delete "$INSTDIR\data\cards\piacentine6.jpg"
  Delete "$INSTDIR\data\cards\piacentine5.jpg"
  Delete "$INSTDIR\data\cards\piacentine41.jpg"
  Delete "$INSTDIR\data\cards\piacentine40.jpg"
  Delete "$INSTDIR\data\cards\piacentine4.jpg"
  Delete "$INSTDIR\data\cards\piacentine39.jpg"
  Delete "$INSTDIR\data\cards\piacentine38.jpg"
  Delete "$INSTDIR\data\cards\piacentine37.jpg"
  Delete "$INSTDIR\data\cards\piacentine36.jpg"
  Delete "$INSTDIR\data\cards\piacentine35.jpg"
  Delete "$INSTDIR\data\cards\piacentine34.jpg"
  Delete "$INSTDIR\data\cards\piacentine33.jpg"
  Delete "$INSTDIR\data\cards\piacentine32.jpg"
  Delete "$INSTDIR\data\cards\piacentine31.jpg"
  Delete "$INSTDIR\data\cards\piacentine30.jpg"
  Delete "$INSTDIR\data\cards\piacentine3.jpg"
  Delete "$INSTDIR\data\cards\piacentine29.jpg"
  Delete "$INSTDIR\data\cards\piacentine28.jpg"
  Delete "$INSTDIR\data\cards\piacentine27.jpg"
  Delete "$INSTDIR\data\cards\piacentine26.jpg"
  Delete "$INSTDIR\data\cards\piacentine25.jpg"
  Delete "$INSTDIR\data\cards\piacentine24.jpg"
  Delete "$INSTDIR\data\cards\piacentine23.jpg"
  Delete "$INSTDIR\data\cards\piacentine22.jpg"
  Delete "$INSTDIR\data\cards\piacentine21.jpg"
  Delete "$INSTDIR\data\cards\piacentine20.jpg"
  Delete "$INSTDIR\data\cards\piacentine2.jpg"
  Delete "$INSTDIR\data\cards\piacentine19.jpg"
  Delete "$INSTDIR\data\cards\piacentine18.jpg"
  Delete "$INSTDIR\data\cards\piacentine17.jpg"
  Delete "$INSTDIR\data\cards\piacentine16.jpg"
  Delete "$INSTDIR\data\cards\piacentine15.jpg"
  Delete "$INSTDIR\data\cards\piacentine14.jpg"
  Delete "$INSTDIR\data\cards\piacentine13.jpg"
  Delete "$INSTDIR\data\cards\piacentine12.jpg"
  Delete "$INSTDIR\data\cards\piacentine11.jpg"
  Delete "$INSTDIR\data\cards\piacentine10.jpg"
  Delete "$INSTDIR\data\cards\piacentine1.jpg"
  Delete "$INSTDIR\data\logo.png"
  Delete "$INSTDIR\data\tsnet4.png"
  Delete "$INSTDIR\server.pyc"
  Delete "$INSTDIR\protocol.pyc"
  Delete "$INSTDIR\player.pyc"
  Delete "$INSTDIR\objects.pyc"
  Delete "$INSTDIR\miscgui.pyc"
  Delete "$INSTDIR\main.pyc"
  Delete "$INSTDIR\launcher.pyc"
  Delete "$INSTDIR\graphics.pyc"

  Delete "$SMPROGRAMS\$ICONS_GROUP\Disinstalla.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\Progetto TSNet4.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\TressetteNetwork4.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\Avvia server.lnk"
  Delete "$DESKTOP\TressetteNetwork4.lnk"

  RMDir "$SMPROGRAMS\$ICONS_GROUP"
  RMDir "$INSTDIR\netframework"
  RMDir "$INSTDIR\data\cards"
  RMDir "$INSTDIR\data"
  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"

  DetailPrint "Cancello la registrazione del gestore degli URI ${PRODUCT_URI_HANDLER}://"
  DeleteRegKey HKCR ${PRODUCT_URI_HANDLER}

;  SetAutoClose true
SectionEnd