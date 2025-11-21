from rest_framework.pagination import LimitOffsetPagination


class StandardLimitOffsetPagination(LimitOffsetPagination):
    # Limit: The number of items to show per page (scroll).
    default_limit = 3
    
    # limit_query_param: The parameter the frontend sends in the URL to specify the number of items.
    limit_query_param = 'limit'
    
    # offset_query_param: The parameter the frontend sends to specify the starting point (number of items to skip).
    offset_query_param = 'offset'
    
    # max_limit: The maximum number of items the frontend can request (to prevent abuse).
    max_limit = 10