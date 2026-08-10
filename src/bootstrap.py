"""Backward-compatible application entry point.

New code should import ``create_application`` or ``ApplicationContainer`` from
``src.core.container``. Existing pages can continue to call ``Bootstrap()``.
"""

from src.core.container import ApplicationContainer, create_application


class Bootstrap(ApplicationContainer):
    pass


__all__ = ["ApplicationContainer", "Bootstrap", "create_application"]
