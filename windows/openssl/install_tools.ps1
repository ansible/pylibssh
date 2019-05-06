param (
   [Parameter(Mandatory=$true)][string]$InstallURI
)

Function Install-SDK-MSI{
  [cmdletbinding()]
  param (
    [Parameter(mandatory=$true)][string]$MSIName
  )

  Write-Output "Installing MSI $MSIName from SDK"
  $msifile = (Get-ChildItem C:\install\sdk\setup\${MSIName}\*.msi)[0].FullName
  Write-Output "Using $msifile"
  Start-Process msiexec.exe -Wait -ArgumentList "/i ${msifile} /q /l*v c:\install_logs\${MSIName}.log"
}

New-Item -ItemType directory -Path c:\install
New-Item -ItemType directory -Path c:\install_logs

Write-Output "Downloading ISO from $InstallURI"
Write-Output "This might take a while..."
(New-Object System.Net.WebClient).DownloadFile($InstallURI, "c:\install\sdk.iso")

Write-Output "Unpacking ISO contents"
Start-Process "${Env:ProgramFiles}\7-Zip\7z.exe" -ArgumentList "x -o`"c:\install\sdk`" -y `"c:\install\sdk.iso`"" -Wait -WindowStyle Hidden -PassThru

Install-SDK-MSI -MsiName "winsdk"
Install-SDK-MSI -MsiName "winsdkbuild"
Install-SDK-MSI -MsiName "winsdkinterop"
Install-SDK-MSI -MsiName "winsdktools"
Install-SDK-MSI -MsiName "winsdkwin32tools"
Install-SDK-MSI -MsiName "vc_stdx86"
Install-SDK-MSI -MsiName "vc_stdamd64"
Install-SDK-MSI -MsiName "winsdknetfxtools"

Remove-Item c:\install -Recurse
Remove-Item c:\install_logs -Recurse
