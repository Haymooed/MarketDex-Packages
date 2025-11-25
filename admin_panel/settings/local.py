try:
    from .base import *  # type: ignore
except ImportError:  # pragma: no cover - placeholder for packaged settings
    INSTALLED_APPS = []

INSTALLED_APPS += ["adventcalendars"]
