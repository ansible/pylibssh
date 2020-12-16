from pylibsshext.errors import LibsshSessionException
from pylibsshext.session import Session


ssh = Session()

HOST = 'CHANGEME'
USER = 'CHANGEME'
PASSWORD = 'CHANGEME'
TIMEOUT = 30
PORT = 22
try:
    ssh.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        timeout=TIMEOUT,
        port=PORT,
    )
except LibsshSessionException as ssh_exc:
    print(f'Failed to connect to {HOST}:{PORT} over SSH: {ssh_exc!s}')

print(f'{ssh.is_connected=}')

ssh_channel = ssh.new_channel()
cmd_resp = ssh_channel.write(b'ls')
print(f'stdout:\n{cmd_resp.stdout}\n')
print(f'stderr:\n{cmd_resp.stderr}\n')
print(f'return code: {cmd_resp.returncode}\n')
ssh_channel.close()

chan_shell = ssh.invoke_shell()
chan_shell.sendall(b'ls')
data = chan_shell.read_bulk_response(timeout=2, retry=10)
chan_shell.close()
print(data)

ssh.close()
