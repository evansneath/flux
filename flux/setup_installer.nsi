;NSIS Modern User Interface

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"
  
;--------------------------------
;Defines

!define VERSION_MAJOR 1
!define VERSION_MINOR 0
!define VERSION_POSTFIX_FULL ""
!ifdef WIN64
  !define VERSION_SYS_POSTFIX_FULL " for Windows x64"
  !define VERSION_SYS_POSTFIX "-x64"
!else
  !define VERSION_SYS_POSTFIX_FULL ""
  !define VERSION_SYS_POSTFIX ""
!endif
!define NAME_FULL "Flux ${VERSION_MAJOR}.${VERSION_MINOR}${VERSION_POSTFIX_FULL}${VERSION_SYS_POSTFIX_FULL}"
!define VERSION_POSTFIX ""

;--------------------------------
;General

  ;Name and file
  Name Flux
  OutFile "..\Flux${VERSION_MAJOR}${VERSION_MINOR}${VERSION_POSTFIX}${VERSION_SYS_POSTFIX}.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\Flux"
  
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\Flux" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel user

;--------------------------------
;Variables

  Var StartMenuFolder

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  ;!insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  
  ;Start Menu Folder Page Configuration
  !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU" 
  !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\Flux" 
  !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
  
  !insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
  
  !insertmacro MUI_PAGE_INSTFILES
  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section

  SetOutPath "$INSTDIR"
  
  File *.pyd
  File *.dll
  File flux.exe
  File library.zip
  
  SetOutPath $INSTDIR\res
  File res\stylesheet.qss
  
  SetOutPath $INSTDIR\res\icons
  File res\icons\*.png
  
  SetOutPath $INSTDIR\res\logo
  File res\logo\logo_small.png
  File res\logo\logo.png
  File res\logo\logo.ico
  
  SetOutPath $INSTDIR\effects
  File effects\__init__.pyc
  File effects\_base.pyc
  File effects\compressor.pyc
  File effects\decimation.pyc
  File effects\delay.pyc
  File effects\filter.pyc
  File effects\fuzzbox.pyc
  File effects\gain.pyc
  File effects\noise_gate.pyc
  File effects\overdrive.pyc
  File effects\pitchshift.pyc
  File effects\reverb.pyc
  File effects\tremolo.pyc
  
  SetOutPath $INSTDIR
  
  
  ;Store installation folder
  WriteRegStr HKCU "Software\Flux" "" $INSTDIR
  
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    
    ;Create shortcuts
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Flux.lnk" "$INSTDIR\flux.exe"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  
  !insertmacro MUI_STARTMENU_WRITE_END

SectionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"
  Delete $INSTDIR\Uninstall.exe

  Delete $INSTDIR\*.pyd
  Delete /REBOOTOK $INSTDIR\*.dll
  Delete $INSTDIR\flux.exe
  Delete $INSTDIR\library.zip
  
  Delete $INSTDIR\res\stylesheet.qss
  
  Delete $INSTDIR\res\icons\*.png
  RMDir $INSTDIR\res\icons
  
  Delete $INSTDIR\res\logo\logo_small.png
  Delete $INSTDIR\res\logo\logo.png
  Delete $INSTDIR\res\logo\logo.ico
  RMDir $INSTDIR\res\logo
  
  RMDir $INSTDIR\res
  
  Delete $INSTDIR\effects\__init__.pyc
  Delete $INSTDIR\effects\_base.pyc
  Delete $INSTDIR\effects\compressor.pyc
  Delete $INSTDIR\effects\decimation.pyc
  Delete $INSTDIR\effects\delay.pyc
  Delete $INSTDIR\effects\filter.pyc
  Delete $INSTDIR\effects\fuzzbox.pyc
  Delete $INSTDIR\effects\gain.pyc
  Delete $INSTDIR\effects\noise_gate.pyc
  Delete $INSTDIR\effects\overdrive.pyc
  Delete $INSTDIR\effects\pitchshift.pyc
  Delete $INSTDIR\effects\reverb.pyc
  Delete $INSTDIR\effects\tremolo.pyc
  RMDir  $INSTDIR\effects

  RMDir $INSTDIR
  
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
    
  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Flux.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"
  
  DeleteRegKey HKCU "Software\Flux"

SectionEnd
