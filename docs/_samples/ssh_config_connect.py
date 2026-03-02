"""Connect using a custom SSH config file.

Use this when you have a dedicated config file (e.g. for ``Host`` aliases,
``ProxyCommand``, or per-host options) and want the session to use it
instead of the default ~/.ssh/config and /etc/ssh/ssh_config.

You can either pass ``config_file`` to ``Session.connect()`` (recommended),
or call ``Session.parse_config(path)`` before ``connect()`` to load a
specific config file. When using ``parse_config()``, set ``host`` first
so that ``Host`` blocks in the config match correctly.
"""

from pylibsshext.errors import LibsshConfigParseException, LibsshSessionException
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
except LibsshConfigParseException as exc:
    print(f'Failed to parse SSH config: {exc!s}')
except LibsshSessionException as exc:
    print(f'Failed to connect: {exc!s}')

if ssh.is_connected:
    print('Connected.')
    ssh.close()
