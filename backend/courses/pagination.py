"""Custom pagination class for standardized result sets."""

import rest_framework.pagination as pagination


class StandardResultsSetPagination(pagination.PageNumberPagination):
    """Standard pagination settings for API views.

    Attributes:
        page_size (int): The default number of items per page.
        page_size_query_param (str): Query parameter to override page size.
        max_page_size (int): The maximum number of items allowed per page.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
