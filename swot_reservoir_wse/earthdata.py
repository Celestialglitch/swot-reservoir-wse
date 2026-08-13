import earthaccess


_initialized = False


def initialize_earthdata():
    """
    Initialize NASA Earthdata authentication once per process.
    """

    global _initialized

    if _initialized:
        return

    try:
        auth = earthaccess.login(
            strategy="netrc",
        )

    except Exception as exc:
        raise RuntimeError(
            "Failed to initialize NASA Earthdata.\n"
            "Please verify your Earthdata credentials.\n"
            "Run:\n\n"
            "    swot-reservoir-wse auth --earthdata-only\n"
        ) from exc

    if not auth.authenticated:
        raise RuntimeError(
            "NASA Earthdata authentication failed.\n"
            "Run:\n\n"
            "    swot-reservoir-wse auth --earthdata-only\n"
        )

    _initialized = True