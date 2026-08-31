#pragma once
#include <stdint.h>
#include <libssh/libssh.h>
#include <libssh/sftp.h>

#if LIBSSH_VERSION_INT >= SSH_VERSION_INT(0, 11, 0)

#define HAVE_SFTP_AIO 1

#else

#define HAVE_SFTP_AIO 0

/*
 * 1. STUB THE TYPES
 * Cython just needs to know these are pointer-sized.
 * Mapping them to void* keeps the C compiler perfectly happy.
 */
struct sftp_limits_struct {
    uint64_t max_packet_length;   /** maximum number of bytes in a single sftp packet */
    uint64_t max_read_length;     /** maximum length in a SSH_FXP_READ packet */
    uint64_t max_write_length;    /** maximum length in a SSH_FXP_WRITE packet */
    uint64_t max_open_handles;    /** maximum number of active handles allowed by server */
};
typedef struct sftp_limits_struct* sftp_limits_t;

struct sftp_aio_struct {
    int _unused;
};
typedef struct sftp_aio_struct* sftp_aio;

/*
 * 2. STUB THE LIMITS FUNCTIONS
 * (Cast arguments to void to suppress unused variable warnings)
 */
static inline sftp_limits_t sftp_limits(sftp_session sftp) {
    (void)sftp;
    return NULL;
}

static inline void sftp_limits_free(sftp_limits_t limits) {
    (void)limits;
}

/*
 * 3. STUB THE AIO FUNCTIONS
 */
static inline ssize_t sftp_aio_begin_read(sftp_file file, size_t len, sftp_aio *aio) {
    (void)file; (void)len; (void)aio;
    return SSH_ERROR;
}

static inline ssize_t sftp_aio_wait_read(sftp_aio *aio, void *buf, size_t buf_size) {
    (void)aio; (void)buf; (void)buf_size;
    return SSH_ERROR;
}

static inline ssize_t sftp_aio_begin_write(sftp_file file, const void *buf, size_t len, sftp_aio *aio) {
    (void)file; (void)buf; (void)len; (void)aio;
    return SSH_ERROR;
}

static inline ssize_t sftp_aio_wait_write(sftp_aio *aio) {
    (void)aio;
    return SSH_ERROR;
}

static inline void sftp_aio_free(sftp_aio aio) {
    (void)aio;
}

#endif
