"""Connect using a custom SSH config file.

Use this when you have a dedicated config file (e.g. for Host aliases,
ProxyCommand, or per-host options) and want the session to use it
instead of the default ~/.ssh/config and /etc/ssh/ssh_config.
"""

from pylibsshext.errors import LibsshSessionException
from pylibsshext.session import Session


ssh = Session()

# Host alias or hostname that appears in your custom config
HOST = 'myalias'
USER = 'myuser'
CONFIG_FILE = '/path/to/my/ssh_config'

try:
    ssh.connect(
        host=HOST,
        user=USER,
        config_file=CONFIG_FILE,
    )
except LibsshSessionException as exc:
    print(f'Failed to connect: {exc!s}')

if ssh.is_connected:
    print('Connected.')
    ssh.close()
