from rest_framework.pagination import LimitOffsetPagination as DRFLimitOffsetPagination
from rest_framework.response import Response


class LimitOffsetPagination(DRFLimitOffsetPagination):
    def __init__(self, *args, **kwargs):
        super(LimitOffsetPagination, self).__init__(*args, **kwargs)

    def get_paginated_response(self, data):
        return Response(data)
