FROM mcr.microsoft.com/windows/servercore:1809

COPY --from=pyca/openssl-windows-artifact:win32-2015 "C:/openssl-win32-2015" C:/OpenSSL-Win32-2015
COPY --from=pyca/openssl-windows-artifact:win64-2015 "C:/openssl-win64-2015" C:/OpenSSL-Win64-2015

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

COPY *.ps1 C:/scripts/
ARG CPU_ARCH

# Windows docker images are substantially larger with multiple layers, which is
# insane, but here we are so let's do it all in one step.
RUN C:/scripts/install_everything.ps1
