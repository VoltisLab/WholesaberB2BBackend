from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class DatabaseUtil:
    @classmethod
    def get_default_page_count(cls) -> dict:
        return {
            "page_count": 50,
            "page_number": 1,
        }

    @staticmethod
    def paginate_query(query_set, page_count=None, page_number=None):
        """
        Paginate a queryset based on the provided page count and page number.

        Args:
            query_set (QuerySet): The queryset to paginate.
            page_count (int, optional): The number of items per page.
            page_number (int, optional): The page number to retrieve.

        Returns:
            tuple: (paginated_queryset, total_pages, total_items)
        """
        if page_count is None or page_number is None:
            defaults = DatabaseUtil.get_default_page_count()
            page_count = page_count or defaults["page_count"]
            page_number = page_number or defaults["page_number"]

        paginator = Paginator(query_set, page_count)
        total_items = paginator.count

        try:
            paginated_queryset = paginator.page(page_number)
        except PageNotAnInteger:
            paginated_queryset = paginator.page(1)
        except EmptyPage:
            paginated_queryset = paginator.page(paginator.num_pages)

        return paginated_queryset, paginator.num_pages, total_items
