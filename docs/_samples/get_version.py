from pylibsshext import (
    __full_version__,  # string with both ansible-pylibssh and libssh versions
)
from pylibsshext import (
    __libssh_version__,  # linked libssh lib version as a string
)
from pylibsshext import __version__  # ansible-pylibssh version as a string
from pylibsshext import __version_info__  # ansible-pylibssh version as a tuple


print(f'{__full_version__=}')
print(f'{__libssh_version__=}')
print(f'{__version__=}')
print(f'{__version_info__=}')
