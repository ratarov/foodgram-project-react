from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """
    Standard paginator with page size query parameter switched on.
    """
    page_size_query_param = 'limit'
    page_size = 6
