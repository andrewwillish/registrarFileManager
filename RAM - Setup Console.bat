::Get active directory
SET mypath=%~dp0

::Set path
set path=%mypath:~0,-1%\Python26\pythonw

::Call Production Software
start %mypath:~0,-1%\Python26\python.exe %mypath:~0,-1%\ramSetupConsole.pyc