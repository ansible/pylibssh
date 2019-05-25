$PYTHON_VERSION = $args[0]
$PYTHON_DIR = $args[1]
$CPU_ARCH = $args[2]

if ($CPU_ARCH -eq "x86_64") {
    $PYTHON_ARCH = ".amd64"
} else {
    $PYTHON_ARCH = ""
}

$url = ('https://www.python.org/ftp/python/{0}/python-{1}{2}.msi' -f $PYTHON_VERSION, $PYTHON_VERSION, $PYTHON_ARCH)
Write-Host ('Downloading {0} ...' -f $url)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $url -OutFile 'python.msi'
Write-Host 'Installing ...'
Start-Process msiexec -Wait -ArgumentList @('/i', 'python.msi', '/quiet', '/qn', 'TARGETDIR=C:\Python34', 'ALLUSERS=1', 'ADDLOCAL=DefaultFeature,Extensions,Tools');
Write-Host 'Verifying install ...'
Write-Host "C:\$PYTHON_DIR\python --version"
& "C:\$PYTHON_DIR\python" --version
Write-Host 'Removing ...'
Remove-Item python.msi -Force
Write-Host 'Complete.'


Write-Host ('Installing pip...')

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'
& "C:\$PYTHON_DIR\python" get-pip.py --disable-pip-version-check --no-cache-dir
Remove-Item get-pip.py -Force
Write-Host 'Verifying pip install ...'
& "C:\$PYTHON_DIR\Scripts\pip" --version
Write-Host 'Complete.'

& "C:\$PYTHON_DIR\Scripts\pip" install --no-cache-dir tox
