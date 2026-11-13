# Cython and libssh

Conventions specific to ansible-pylibssh's Cython extension
modules and the libssh C API they wrap. This file isn't shared with
other projects -- see [HOUSE_STYLE.md](HOUSE_STYLE.md) for the
general style rules.

## Keep encoded-bytes objects alive when backing a `char*`

Assigning an intermediate result straight into a `char*`/`const
char*` (e.g. `cdef char* c_buf = value.encode("utf-8")`) is a
segfault waiting to happen: the encoded `bytes` object has no
Python reference keeping it alive, so it can be garbage-collected
while the pointer is still in use, leaving `c_buf` dangling.
Assign the encoded bytes to a named Python variable first and
keep that variable alive for as long as the pointer is used. When
you do this, add a code comment explaining why, citing Cython's
own docs on the gotcha:
https://cython.rtfd.io/en/latest/src/tutorial/strings.html#encoding-text-to-bytes
(PR #875).

## Cython still shims the removed Python 2 `unicode` name

Even under `language_level = 3`, Cython keeps `unicode` available
as a shim for `str`
(https://cython.rtfd.io/en/latest/src/tutorial/strings.html#python-string-types-in-cython-code),
which reads as confusing coming from plain Python 3, where
`unicode` doesn't exist. Don't be surprised to see it in Cython
code or docs, but don't introduce new uses of it -- prefer `str`.

A related open TODO, not yet acted on: unifying the
`language_level` compiler directive to a single explicit value
across the codebase, rather than leaving it implicit/inconsistent
(PR #875).

## The extension modules hold the GIL while in libssh

The Cython modules call into libssh without releasing the GIL, so
a blocking call -- connecting, authenticating, waiting on a
channel -- stalls every other Python thread in the process.
Anything that has to keep running meanwhile, like a server or
relay test double, needs a separate process.

## `str | bytes`-style type hints aren't enforced at runtime here

Union type annotations on Cython-extension methods (e.g. `data:
str | bytes`) aren't actually enforced at runtime by
CPython/Cython -- they have the same effect as a docstring, not
real validation. Don't treat a Union annotation as a substitute
for actual input-coercion/validation logic (PR #870/#874
discussion).

## No automated formatter for `.pyx` -- wrap long lines by hand

Unlike `.py` files (formatted by `ruff format`), there's
currently no formatter tool that works on Cython source. Long-line
wrapping in `.pyx` files is done by hand, following ordinary
Python-style continuation conventions -- not C-style formatting
habits (PR #869).

## Libssh functions safely handle NULL pointers, but initialize them early

Functions in the libssh C API (e.g. `sftp_aio_free()`,
`sftp_limits_free()`, `sftp_free()`) are designed to be safe no-ops
when passed `NULL`. Do not add redundant `if ptr is not NULL:` guards
prior to calling these cleanup functions, and do not flag unguarded
calls to them as missing null-checks.

However, note that `sftp_close()` is an exception in older libssh versions
(such as libssh < 0.10.0 / 0.9.x, shipped e.g. in Ubuntu 22.04 LTS), where
passing `NULL` dereferences `file->sftp` without a null check and crashes
with SIGSEGV. Therefore, calls to `sftp_close()` must always be guarded
against `NULL` handles (e.g. `if self._fd is NULL: return`).

However, `NULL`-safety in C functions only works if the pointer is
actually `NULL`, not uninitialized garbage memory. Always initialize raw C
pointer attributes (e.g. `self._fd = NULL`) at the very beginning of
`__cinit__` before any checks that could raise an exception, because Cython
still invokes `__dealloc__` when `__cinit__` raises early.
