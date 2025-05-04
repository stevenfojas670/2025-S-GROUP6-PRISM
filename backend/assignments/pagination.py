"""Custom pagination class for standardized result sets."""

import rest_framework.pagination as pagination
from rest_framework.response import Response


class StandardResultsSetPagination(pagination.PageNumberPagination):
    """Standard pagination settings for API views.

    Attributes:
        page_size (int): The default number of items per page.
        page_size_query_param (str): Query parameter to override page size.
        max_page_size (int): The maximum number of items allowed per page.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 200

    def get_paginated_response(self, data):
        """
        Return a paginated API response with custom pagination structure.

        Args:
            data (list): The paginated list of results for the current page.

        Returns:
            Response: A DRF Response object containing pagination metadata
                    and the current page's results.
        """
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "current_page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "results": data,
            }
        )
