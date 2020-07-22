from pylibsshext.includes.libssh cimport libssh_version


LIBSSH_VERSION = libssh_version.decode("ascii")
