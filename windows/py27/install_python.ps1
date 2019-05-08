$CPU_ARCH = $args[0]

if ($CPU_ARCH -eq "x86_64") {
    $PYTHON_INSTALLER_PATH = "2.7.16/python-2.7.16.amd64.msi"
} else {
    $PYTHON_INSTALLER_PATH = "2.7.16/python-2.7.16.msi"
}

$url = ('https://www.python.org/ftp/python/{0}' -f $PYTHON_INSTALLER_PATH);
Write-Host ('Downloading {0} ...' -f $url)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $url -OutFile 'python.msi'
Write-Host 'Installing ...';
Start-Process msiexec -Wait -ArgumentList @('/i', 'python.msi', '/quiet', '/qn', 'TARGETDIR=C:\Python27', 'ALLUSERS=1', 'ADDLOCAL=DefaultFeature,Extensions,Tools');
Write-Host 'Verifying install ...'
Write-Host 'C:\Python27\python --version'
C:\Python27\python --version
Write-Host 'Removing ...'
Remove-Item python.msi -Force;
Write-Host 'Complete.'


Write-Host ('Installing pip')
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'
C:\Python27\python get-pip.py --disable-pip-version-check --no-cache-dir
Remove-Item get-pip.py -Force
Write-Host 'Verifying pip install ...'
C:\Python27\Scripts\pip --version
Write-Host 'Complete.'

C:\Python27\Scripts\pip install --no-cache-dir tox
