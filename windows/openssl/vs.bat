curl -fSLo vs_BuildTools.exe https://aka.ms/vs/16/release/vs_buildtools.exe
if %errorlevel% neq 0 exit /b %errorlevel%
setx /M DOTNET_SKIP_FIRST_TIME_EXPERIENCE 1
start /w vs_BuildTools.exe --quiet --norestart --nocache --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended
if %errorlevel% neq 0 exit /b %errorlevel%
del vs_BuildTools.exe
powershell Remove-Item -Force -Recurse "%TEMP%\*"
rmdir /S /Q "%ProgramData%\Package Cache"
