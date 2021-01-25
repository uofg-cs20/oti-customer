from rest_framework import pagination

class LimitSkipPagination(pagination.LimitOffsetPagination):
    offset_query_param = "skip"
    max_limit = 50
