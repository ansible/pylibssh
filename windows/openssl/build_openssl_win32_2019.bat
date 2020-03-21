call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=x86
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\VC\Auxiliary\Build\vcvarsall.bat" x86
SET PATH=%PATH%;C:\Program Files\NASM

perl Configure no-comp no-shared VC-WIN32
nmake
if %errorlevel% neq 0 exit /b %errorlevel%

mkdir ..\build
mkdir ..\build\lib
move libcrypto.lib ..\build\lib\
move libssl.lib ..\build\lib\
move include ..\build\include
