FROM mcr.microsoft.com/windows/servercore:1809

COPY --from=pyca/openssl-windows-artifact:win32-2010 "C:/openssl-win32-2010" C:/OpenSSL-Win32-2010
COPY --from=pyca/openssl-windows-artifact:win64-2010 "C:/openssl-win64-2010" C:/OpenSSL-Win64-2010

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

RUN Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

RUN choco install -y 7zip
RUN choco install git -y --params="/NoAutoCrlf"

COPY *.ps1 C:/scripts/

RUN /scripts/install_compiler.ps1 -InstallURI http://download.microsoft.com/download/F/1/0/F10113F5-B750-4969-A255-274341AC6BCE/GRMSDK_EN_DVD.iso

ARG CPU_ARCH

RUN C:/scripts/install_python.ps1 3.4.4 Python34 $env:CPU_ARCH
