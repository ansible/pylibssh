Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

choco install --no-progress -y 7zip
# We need to check exit code after every exe invocation because powershell has no
# facility for doing this since Windows exit codes are inconsistent
if ($LastExitCode -ne 0) { exit 1; }

choco install --no-progress -y git --params="/NoAutoCrlf"
if ($LastExitCode -ne 0) { exit 1; }

choco install --ignore-package-exit-codes --no-progress -y dotnetfx
if ($LastExitCode -ne 0) { exit 1; }

choco install --ignore-package-exit-codes --no-progress -y visualstudio2017buildtools
if ($LastExitCode -ne 0) { exit 1; }

choco install --ignore-package-exit-codes --no-progress -y visualstudio2017-workload-vctools --package-parameters "'--add Microsoft.VisualStudio.Component.Windows10SDK.17763 --no-includeRecommended'"
if ($LastExitCode -ne 0) { exit 1; }

& C:/scripts/install_python.ps1 3.6.8 Python36 $env:CPU_ARCH
if ($LastExitCode -ne 0) { exit 1; }

& C:/scripts/install_python.ps1 3.7.3 Python37 $env:CPU_ARCH
if ($LastExitCode -ne 0) { exit 1; };
