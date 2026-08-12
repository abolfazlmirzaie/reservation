from rest_framework.pagination import PageNumberPagination


class SalonPageNumberPagination(PageNumberPagination):
    page_size = 5
