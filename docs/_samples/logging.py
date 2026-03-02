import logging

from pylibsshext.errors import LibsshSessionException
from pylibsshext.logging import ANSIBLE_PYLIBSSH_TRACE
from pylibsshext.session import Session


HOST = 'CHANGEME'
USER = 'CHANGEME'
PASSWORD = 'CHANGEME'
PORT = 22

# Initializes the new TRACE log level in python logging system
ssh = Session()

error_handler = logging.StreamHandler()
error_handler.setLevel(logging.ERROR)

debug_handler = logging.FileHandler('ansible-libssh-errors.log')
debug_handler.setLevel(ANSIBLE_PYLIBSSH_TRACE)

logging.getLogger('ansible-pylibssh').addHandler(error_handler)
logging.getLogger('ansible-pylibssh').addHandler(debug_handler)

# Set log level on session to filter log messages libssh emits internally
# and sends over into the Python land (when performance matters)
ssh.set_log_level(ANSIBLE_PYLIBSSH_TRACE)

try:
    ssh.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        port=PORT,
    )
except LibsshSessionException as ssh_exc:
    # NOTE: `connect()` above will emit its own detailed logs from `libssh`
    print(f'Failed to connect to {HOST}:{PORT} over SSH: {ssh_exc!s}')
