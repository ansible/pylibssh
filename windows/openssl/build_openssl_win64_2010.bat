SET FINALDIR="openssl-win64-2010"

call "C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.cmd" /x64 /release
SET PATH=%PATH%;C:\Program Files\NASM;C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1\Bin
SET INCLUDE=C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\INCLUDE;C:\Program Files\Microsoft SDKs\Windows\v7.1\INCLUDE;C:\Program Files\Microsoft SDKs\Windows\v7.1\INCLUDE\gl;C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1\Include
SET LIB=%LIB%;C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1\Lib\x64

perl Configure no-comp no-shared VC-WIN64A
nmake

mkdir C:\build\%FINALDIR%
mkdir C:\build\%FINALDIR%\lib
move libcrypto.lib C:\build\%FINALDIR%\lib\
move libssl.lib C:\build\%FINALDIR%\lib\
move include C:\build\%FINALDIR%\include
