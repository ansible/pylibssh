SET BUILDARCH=%1
SET VSVERSION=%2
echo %BUILDARCH%
echo %VSVERSION%

cd openssl-1*

if "%VSVERSION%" == "2010" (
    if "%BUILDARCH%" == "win32" (
        CALL C:\scripts\build_openssl_win32_2010.bat
    ) else (
        CALL C:\scripts\build_openssl_win64_2010.bat
    )
) else (
    if "%BUILDARCH%" == "win32" (
        CALL C:\scripts\build_openssl_win32_2015.bat
    ) else (
        CALL C:\scripts\build_openssl_win64_2015.bat
    )
)
if %errorlevel% neq 0 exit /b %errorlevel%
