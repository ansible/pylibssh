FROM mcr.microsoft.com/windows/servercore:1809 as openssl-builder

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

RUN Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

RUN choco install -y 7zip nasm activeperl winrar
COPY *.ps1 /scripts/
COPY *.bat /scripts/

RUN & 'C:/scripts/vs.bat'

RUN powershell -Command /scripts/install_tools.ps1 -InstallURI http://download.microsoft.com/download/F/1/0/F10113F5-B750-4969-A255-274341AC6BCE/GRMSDK_EN_DVD.iso

RUN [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; wget 'https://www.openssl.org/source/openssl-1.1.1-latest.tar.gz' -OutFile 'openssl-latest.tar.gz'

RUN & 'C:\scripts\setup.bat'

ARG BUILDARCH
ARG VSVERSION

RUN & 'C:\scripts\build_openssl.bat' %BUILDARCH% %VSVERSION%

FROM mcr.microsoft.com/windows/nanoserver:1809

# We need these because ARGs from the previous stage don't carry over
ARG BUILDARCHVSVERSION

COPY --from=openssl-builder "C:/build/openssl-${BUILDARCHVSVERSION}" "C:/openssl-${BUILDARCHVSVERSION}"
