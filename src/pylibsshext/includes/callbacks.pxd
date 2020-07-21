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

from pylibsshext.includes.libssh cimport ssh_channel, ssh_session


cdef extern from "libssh/callbacks.h":

    void ssh_callbacks_init(void *)

    ctypedef int (*ssh_channel_data_callback) (ssh_session session,
                                               ssh_channel channel,
                                               void *data,
                                               uint32_t len,
                                               int is_stderr,
                                               void *userdata)
    ctypedef void (*ssh_channel_eof_callback) (ssh_session session,
                                               ssh_channel channel,
                                               void *userdata)

    ctypedef void (*ssh_channel_close_callback) (ssh_session session,
                                                 ssh_channel channel,
                                                 void *userdata)

    ctypedef void (*ssh_channel_signal_callback) (ssh_session session,
                                                  ssh_channel channel,
                                                  const char *signal,
                                                  void *userdata)

    ctypedef void (*ssh_channel_exit_status_callback) (ssh_session session,
                                                       ssh_channel channel,
                                                       int exit_status,
                                                       void *userdata)

    ctypedef void (*ssh_channel_exit_signal_callback) (ssh_session session,
                                                       ssh_channel channel,
                                                       const char *signal,
                                                       int core,
                                                       const char *errmsg,
                                                       const char *lang,
                                                       void *userdata)

    ctypedef int (*ssh_channel_pty_request_callback) (ssh_session session,
                                                      ssh_channel channel,
                                                      const char *term,
                                                      int width, int height,
                                                      int pxwidth, int pwheight,
                                                      void *userdata)

    ctypedef int (*ssh_channel_shell_request_callback) (ssh_session session,
                                                        ssh_channel channel,
                                                        void *userdata)

    ctypedef void (*ssh_channel_auth_agent_req_callback) (ssh_session session,
                                                          ssh_channel channel,
                                                          void *userdata)

    ctypedef void (*ssh_channel_x11_req_callback) (ssh_session session,
                                                   ssh_channel channel,
                                                   int single_connection,
                                                   const char *auth_protocol,
                                                   const char *auth_cookie,
                                                   uint32_t screen_number,
                                                   void *userdata)

    ctypedef int (*ssh_channel_pty_window_change_callback) (ssh_session session,
                                                            ssh_channel channel,
                                                            int width, int height,
                                                            int pxwidth, int pwheight,
                                                            void *userdata)

    ctypedef int (*ssh_channel_exec_request_callback) (ssh_session session,
                                                       ssh_channel channel,
                                                       const char *command,
                                                       void *userdata)

    ctypedef int (*ssh_channel_env_request_callback) (ssh_session session,
                                                      ssh_channel channel,
                                                      const char *env_name,
                                                      const char *env_value,
                                                      void *userdata)

    ctypedef int (*ssh_channel_subsystem_request_callback) (ssh_session session,
                                                            ssh_channel channel,
                                                            const char *subsystem,
                                                            void *userdata)

    ctypedef int (*ssh_channel_write_wontblock_callback) (ssh_session session,
                                                          ssh_channel channel,
                                                          size_t bytes,
                                                          void *userdata)

    struct ssh_channel_callbacks_struct:
        size_t size
        void *userdata
        ssh_channel_data_callback channel_data_function
        ssh_channel_eof_callback channel_eof_function
        ssh_channel_close_callback channel_close_function
        ssh_channel_signal_callback channel_signal_function
        ssh_channel_exit_status_callback channel_exit_status_function
        ssh_channel_exit_signal_callback channel_exit_signal_function
        ssh_channel_pty_request_callback channel_pty_request_function
        ssh_channel_shell_request_callback channel_shell_request_function
        ssh_channel_auth_agent_req_callback channel_auth_agent_req_function
        ssh_channel_x11_req_callback channel_x11_req_function
        ssh_channel_pty_window_change_callback channel_pty_window_change_function
        ssh_channel_exec_request_callback channel_exec_request_function
        ssh_channel_env_request_callback channel_env_request_function
        ssh_channel_subsystem_request_callback channel_subsystem_request_function
        ssh_channel_write_wontblock_callback channel_write_wontblock_function
    ctypedef ssh_channel_callbacks_struct * ssh_channel_callbacks

    int ssh_set_channel_callbacks(ssh_channel channel, ssh_channel_callbacks cb)
