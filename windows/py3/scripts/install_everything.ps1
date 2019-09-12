& C:/scripts/vs.bat
if ($LastExitCode -ne 0) { exit 1; };

Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

choco install --no-progress -y 7zip
# We need to check exit code after every exe invocation because powershell has no
# facility for doing this since Windows exit codes are inconsistent
if ($LastExitCode -ne 0) { exit 1; }

choco install --no-progress -y git --params="/NoAutoCrlf"
if ($LastExitCode -ne 0) { exit 1; }

& C:/scripts/install_python.ps1 3.6.8 Python36 $env:CPU_ARCH
if ($LastExitCode -ne 0) { exit 1; }

& C:/scripts/install_python.ps1 3.7.4 Python37 $env:CPU_ARCH
if ($LastExitCode -ne 0) { exit 1; };
