SET FINALDIR="openssl-win64-2015"

call "C:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=x64
SET PATH=%PATH%;C:\Program Files\NASM

perl Configure no-comp no-shared VC-WIN64A
nmake
if %errorlevel% neq 0 exit /b %errorlevel%

mkdir C:\build\%FINALDIR%
mkdir C:\build\%FINALDIR%\lib
move libcrypto.lib C:\build\%FINALDIR%\lib\
move libssl.lib C:\build\%FINALDIR%\lib\
move include C:\build\%FINALDIR%\include
