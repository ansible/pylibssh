FROM mcr.microsoft.com/windows/servercore:1809

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

RUN Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

RUN choco install --ignore-package-exit-codes -y visualcpp-build-tools --version 14.0.25420.1

COPY *.ps1 C:/scripts/

ARG CPU_ARCH

RUN C:/scripts/install_python.ps1 3.5.4 Python35 $env:CPU_ARCH
