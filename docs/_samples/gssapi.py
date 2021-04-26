from pylibsshext.errors import LibsshSessionException
from pylibsshext.session import Session


ssh = Session()

HOST = 'CHANGEME'
USER = 'CHANGEME'
TIMEOUT = 30
PORT = 22
try:
    ssh.connect(
        host=HOST,
        user=USER,
        timeout=TIMEOUT,
        port=PORT,
        # These parameters are not necessary, but can narrow down which token
        # should be used to connect, similar to specifying a ssh private key
        # gssapi_client_identity="client_principal_name",
        # gssapi_server_identity="server_principal_hostname",
    )
except LibsshSessionException as ssh_exc:
    print(f'Failed to connect over SSH: {ssh_exc!s}')

print(f'{ssh.is_connected=}')

if ssh.is_connected:
    chan_shell = ssh.invoke_shell()
    try:
        chan_shell.sendall(b'ls\n')
        data_b = chan_shell.read_bulk_response(timeout=2, retry=10)
        print(data_b.decode())
    finally:
        chan_shell.close()

    ssh.close()
