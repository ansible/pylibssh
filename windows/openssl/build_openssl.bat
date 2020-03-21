SET BUILDARCH=%1
SET VSVERSION=%2

cd openssl-1*

if "%VSVERSION%" == "2010" (
    if "%BUILDARCH%" == "win32" (
        CALL ..\windows\openssl\build_openssl_win32_2010.bat
    ) else (
        CALL ..\windows\openssl\build_openssl_win64_2010.bat
    )
) else (
    if "%BUILDARCH%" == "win32" (
        CALL ..\windows\openssl\build_openssl_win32_2019.bat
    ) else (
        CALL ..\windows\openssl\build_openssl_win64_2019.bat
    )
)
if %errorlevel% neq 0 exit /b %errorlevel%
