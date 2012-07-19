import os
import platform

from cx_Freeze import setup, Executable


includes = ['scipy.signal', 'scipy.sparse.csgraph._validation']
if platform.system() == 'Windows':
    includes.append('serial.win32')
    
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'tcl', 'Tkconstants', 'Tkinter']
packages = []
include_files = [os.path.relpath(os.path.join(root, f))
                 for folder in ('res', 'effects')
                 for root, dirs, files in os.walk(folder)
                 for f in files]

if platform.system() == 'Windows':
    target_name = 'flux.exe'
    base = 'Win32GUI'
else:
    target_name = 'flux'
    base = None
target = Executable(
    script='main.py',
    base=base,
    targetName=target_name,
    icon=os.path.join('res', 'logo', 'logo.ico')
    )


setup(
    version = '1.0',
    description = '',
    author = '',
    name = 'Flux',
    options = {'build_exe': {'includes': includes,
                             'excludes': excludes,
                             'packages': packages,
                             'include_files':include_files
                             }
               },
    executables = [target]
    )

