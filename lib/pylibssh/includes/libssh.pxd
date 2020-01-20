#
# This file is part of the pylibssh library
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, see file LICENSE.rst in this
# repository.
#

from libc.stdint cimport uint32_t

cdef extern from "libssh/libssh.h" nogil:

    cdef struct ssh_session_struct:
        pass
    ctypedef ssh_session_struct* ssh_session

    cdef struct ssh_key_struct:
        pass
    ctypedef ssh_key_struct* ssh_key

    cdef struct ssh_channel_struct:
        pass
    ctypedef ssh_channel_struct* ssh_channel

    cdef enum ssh_known_hosts_e:
        SSH_KNOWN_HOSTS_ERROR,
        SSH_KNOWN_HOSTS_NOT_FOUND,
        SSH_KNOWN_HOSTS_UNKNOWN,
        SSH_KNOWN_HOSTS_OK,
        SSH_KNOWN_HOSTS_CHANGED,
        SSH_KNOWN_HOSTS_OTHER

    cdef enum ssh_auth_e:
        SSH_AUTH_SUCCESS,
        SSH_AUTH_DENIED,
        SSH_AUTH_PARTIAL,
        SSH_AUTH_INFO,
        SSH_AUTH_AGAIN,
        SSH_AUTH_ERROR

    cdef enum ssh_publickey_hash_type:
        SSH_PUBLICKEY_HASH_SHA1,
        SSH_PUBLICKEY_HASH_MD5,
        SSH_PUBLICKEY_HASH_SHA256

    cdef enum ssh_options_e:
          SSH_OPTIONS_HOST,
          SSH_OPTIONS_PORT,
          SSH_OPTIONS_PORT_STR,
          SSH_OPTIONS_FD,
          SSH_OPTIONS_USER,
          SSH_OPTIONS_SSH_DIR,
          SSH_OPTIONS_IDENTITY,
          SSH_OPTIONS_ADD_IDENTITY,
          SSH_OPTIONS_KNOWNHOSTS,
          SSH_OPTIONS_TIMEOUT,
          SSH_OPTIONS_TIMEOUT_USEC,
          SSH_OPTIONS_SSH1,
          SSH_OPTIONS_SSH2,
          SSH_OPTIONS_LOG_VERBOSITY,
          SSH_OPTIONS_LOG_VERBOSITY_STR,
          SSH_OPTIONS_CIPHERS_C_S,
          SSH_OPTIONS_CIPHERS_S_C,
          SSH_OPTIONS_COMPRESSION_C_S,
          SSH_OPTIONS_COMPRESSION_S_C,
          SSH_OPTIONS_PROXYCOMMAND,
          SSH_OPTIONS_BINDADDR,
          SSH_OPTIONS_STRICTHOSTKEYCHECK,
          SSH_OPTIONS_COMPRESSION,
          SSH_OPTIONS_COMPRESSION_LEVEL,
          SSH_OPTIONS_KEY_EXCHANGE,
          SSH_OPTIONS_HOSTKEYS,
          SSH_OPTIONS_GSSAPI_SERVER_IDENTITY,
          SSH_OPTIONS_GSSAPI_CLIENT_IDENTITY,
          SSH_OPTIONS_GSSAPI_DELEGATE_CREDENTIALS,
          SSH_OPTIONS_HMAC_C_S,
          SSH_OPTIONS_HMAC_S_C,
          SSH_OPTIONS_PASSWORD_AUTH,
          SSH_OPTIONS_PUBKEY_AUTH,
          SSH_OPTIONS_KBDINT_AUTH,
          SSH_OPTIONS_GSSAPI_AUTH,
          SSH_OPTIONS_GLOBAL_KNOWNHOSTS,
          SSH_OPTIONS_NODELAY,
          SSH_OPTIONS_PUBLICKEY_ACCEPTED_TYPES,
          SSH_OPTIONS_PROCESS_CONFIG,
          SSH_OPTIONS_REKEY_DATA,
          SSH_OPTIONS_REKEY_TIME

    cdef int SSH_OK
    cdef int SSH_ERROR
    cdef int SSH_AGAIN
    cdef int SSH_EOF

    cdef int SSH_LOG_NONE
    cdef int SSH_LOG_WARN
    cdef int SSH_LOG_INFO
    cdef int SSH_LOG_DEBUG
    cdef int SSH_LOG_TRACE

    const char *ssh_get_error(void *)
    void ssh_string_free_char(char *)

    ssh_session ssh_new()
    void ssh_free(ssh_session session)

    int ssh_connect(ssh_session session)
    int ssh_is_connected(ssh_session session)
    void ssh_disconnect(ssh_session session)
    ssh_known_hosts_e ssh_session_is_known_server(ssh_session)

    int ssh_options_get(ssh_session session, ssh_options_e type, char **value)
    int ssh_options_get_port(ssh_session session, unsigned int * port_target)
    int ssh_options_set(ssh_session session, ssh_options_e type, const void *value)

    int ssh_get_server_publickey(ssh_session session, ssh_key *key)
    void ssh_key_free(ssh_key)

    int ssh_get_publickey_hash(const ssh_key key, ssh_publickey_hash_type type, unsigned char **hash, size_t *hlen)
    char *ssh_get_hexa(const unsigned char *what, size_t len)

    int ssh_userauth_publickey_auto(ssh_session session, const char *username, const char *passphrase)
    int ssh_userauth_password(ssh_session session, const char *username, const char *password)

    ssh_channel ssh_channel_new(ssh_session session)
    void ssh_channel_free(ssh_channel channel)
    int ssh_channel_open_session(ssh_channel channel)
    int ssh_channel_request_pty(ssh_channel channel)
    int ssh_channel_request_pty_size(ssh_channel channel, const char *term, int cols, int rows)
    int ssh_channel_request_shell(ssh_channel channel)
    int ssh_channel_is_open(ssh_channel channel)
    int ssh_channel_write(ssh_channel channel, const void *data, uint32_t len)
    int ssh_channel_poll(ssh_channel channel, int is_stderr)
    int ssh_channel_read(ssh_channel channel, void *dest, uint32_t count, int is_stderr)
    int ssh_channel_read_nonblocking(ssh_channel channel, void *dest, uint32_t count, int is_stderr)
    int ssh_channel_poll_timeout(ssh_channel channel, int timeout, int is_stderr)
    int ssh_channel_close(ssh_channel channel)
    int ssh_channel_request_exec(ssh_channel channel, const char *cmd)
    int ssh_channel_get_exit_status(ssh_channel channel)
    int ssh_channel_send_eof(ssh_channel channel)

    int ssh_set_log_level(int level)

cdef extern from "sys/stat.h" nogil:
    cdef int S_IRWXU
