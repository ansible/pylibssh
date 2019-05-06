FROM mcr.microsoft.com/windows/servercore:ltsc2019

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

RUN Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

RUN choco install -y 7zip nasm activeperl winrar
RUN choco install --ignore-package-exit-codes -y dotnetfx
RUN choco install --ignore-package-exit-codes -y visualstudio2017buildtools
RUN choco install --ignore-package-exit-codes -y visualstudio2017-workload-vctools

COPY *.ps1 /scripts/
COPY *.bat /scripts/

RUN powershell -Command /scripts/install_tools.ps1 -InstallURI http://download.microsoft.com/download/F/1/0/F10113F5-B750-4969-A255-274341AC6BCE/GRMSDK_EN_DVD.iso

RUN [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; wget 'https://www.openssl.org/source/openssl-1.1.1-latest.tar.gz' -OutFile 'openssl-latest.tar.gz'

RUN & 'C:\scripts\setup.bat'

ARG BUILDARCH
ARG VSVERSION

RUN & 'C:\scripts\build_openssl.bat' %BUILDARCH% %VSVERSION%
