"""
Test settings for prism_backend project.

This settings file is used when running tests. It imports all of the base
settings from the main settings module, but then overrides certain settings
such as caching and the database for a faster, isolated test environment.
"""

from .settings import *  # noqa: F401, F403

# Use the DummyCache backend to disable caching in tests.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
