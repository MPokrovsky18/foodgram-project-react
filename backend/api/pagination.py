from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """
    Custom pagination class for Django Rest Framework.

    Allowing clients to specify
    the number of items per page using the 'limit' query parameter.
    """

    page_size_query_param = 'limit'
