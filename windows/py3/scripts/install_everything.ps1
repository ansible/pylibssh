& C:/scripts/vs.bat
if ($LastExitCode -ne 0) { exit 1; };

& C:/scripts/install_python.ps1 3.6.8 Python36 $env:CPU_ARCH
if ($LastExitCode -ne 0) { exit 1; }

& C:/scripts/install_python.ps1 3.7.4 Python37 $env:CPU_ARCH
if ($LastExitCode -ne 0) { exit 1; };

& C:/scripts/install_python.ps1 3.8.0 Python38 $env:CPU_ARCH
if ($LastExitCode -ne 0) { exit 1; };
