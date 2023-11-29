"""Cross-interpreter compatibility shims."""

try:
    # Python 3.11+
    from tomllib import loads as load_toml_from_string  # noqa: WPS433
except ImportError:
    # before Python 3.11
    from tomli import loads as load_toml_from_string  # noqa: WPS433, WPS440


__all__ = ('load_toml_from_string',)  # noqa: WPS410
