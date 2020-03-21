FROM mcr.microsoft.com/windows/servercore:1809

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

COPY scripts C:/scripts/

ARG CPU_ARCH

# Windows docker images are substantially larger with multiple layers, which is
# insane, but here we are so let's do it all in one step.
RUN C:/scripts/install_everything.ps1
