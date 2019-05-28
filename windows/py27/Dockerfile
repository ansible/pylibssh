FROM mcr.microsoft.com/windows/servercore:1809

COPY --from=pyca/openssl-windows-artifact:win32-2010 "C:/openssl-win32-2010" C:/OpenSSL-Win32-2010
COPY --from=pyca/openssl-windows-artifact:win64-2010 "C:/openssl-win64-2010" C:/OpenSSL-Win64-2010

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Install Compiler
RUN Invoke-WebRequest -Uri https://download.microsoft.com/download/7/9/6/796EF2E4-801B-4FC4-AB28-B59FBF6D907B/VCForPython27.msi -OutFile VCForPython27.msi; \
    Write-Host 'Installing VC For Python 2.7...'; \
    Start-Process msiexec -Wait \
        -ArgumentList @('/i', 'VCForPython27.msi', '/qn', 'ALLUSERS=1'); \
    Remove-Item VCForPython27.msi -Force;

# Install chocolatey
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

RUN choco install -y git --params="/NoAutoCrlf"

COPY *.ps1 C:/scripts/

ARG CPU_ARCH

RUN C:/scripts/install_python.ps1 $env:CPU_ARCH

ENV PYTHONIOENCODING=utf8
