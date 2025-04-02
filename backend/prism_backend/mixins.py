"""mixins for prism_backend"""

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class CachedViewMixin:
    """Mixin to cache the response of a view for 15 minutes.

    This is useful for views that do not change often and can benefit from caching.
    """
    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)