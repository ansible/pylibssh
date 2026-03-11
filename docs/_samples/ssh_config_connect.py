"""Connect using a custom SSH config file.

Use this when you have a dedicated config file (e.g. for ``Host`` aliases,
``ProxyCommand``, or per-host options) and want the session to use it
instead of the default ~/.ssh/config and /etc/ssh/ssh_config.

You can either pass ``config_file`` to ``Session.connect()`` (recommended),
or call ``Session.parse_config(path)`` before ``connect()`` to load a
specific config file. When using ``parse_config()``, set ``host`` first
so that ``Host`` blocks in the config match correctly.
"""

from pylibsshext.errors import (
    LibsshConfigParseException,
    LibsshSessionException,
)
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
except LibsshConfigParseException as ssh_config_load_error:
    print(f'Failed to load the SSH config: {ssh_config_load_error!s}')
except LibsshSessionException as ssh_session_connection_error:
    print(f'Failed to connect: {ssh_session_connection_error!s}')

# Alternative: call parse_config() explicitly (e.g. with a pathlib.Path)
# ssh = Session(host=HOST)
# ssh.parse_config(Path(CONFIG_FILE))  # or str/bytes
# ssh.connect(user=USER)

if ssh.is_connected:
    print('Connected.')
    ssh.close()
