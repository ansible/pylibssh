# `pep517_backend` in-tree build backend

The `pep517_backend.hooks` importable exposes callables declared by PEP 517
and PEP 660 and is integrated into `pyproject.toml`'s
`[build-system].build-backend` through `[build-system].backend-path`.

# Design considerations

`__init__.py` is to remain empty, leaving `hooks.py` the only entrypoint
exposing the callables. The logic is contained in private modules. This is
to prevent import-time side effects.

# Upstream RPM package spec

This exists for smoke testing builds and is dynamically configured for
targeting different operating system. It's also used by the [Packit] CI
integration.

[Packit]: https://packit.dev
