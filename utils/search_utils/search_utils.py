from datetime import timedelta
from django.db.models import Count, Avg, Max, Min, F
from django.db.models.functions import ExtractDay, TruncDate, ExtractHour
from django.utils import timezone
from accounts.models import SearchHistory, User


class SearchUtils:

    @staticmethod
    def get_top_searches_by_frequency(days=30, limit=10, user=None):
        """
        Get top searches by frequency within specified time period

        Args:
            days (int): Number of days to look back
            limit (int): Number of results to return
            user (User): Optional user to filter searches for specific user

        Returns:
            QuerySet: Top searches with frequency stats
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Base query
        query = SearchHistory.objects.filter(
            timestamp__gte=start_date, timestamp__lte=end_date, deleted=False
        )

        # Add user filter if specified
        if user:
            query = query.filter(user=user)

        # Aggregate search statistics
        top_searches = (
            query.values("query")
            .annotate(
                total_searches=Count("id"),
                unique_users=Count("user", distinct=True),
                avg_frequency=Avg("search_frequency"),
                last_searched=Max("last_searched"),
                days_active=ExtractDay(Max("timestamp") - Min("timestamp")) + 1,
            )
            .annotate(searches_per_day=F("total_searches") / F("days_active"))
            .order_by("-searches_per_day")[:limit]
        )

        return top_searches

    @staticmethod
    def calculate_frequency(user, query, days=30):
        """
        Calculate search frequency: searches per day over the last specified days
        Returns searches per day multiplied by 100 to store as an integer
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get daily search counts for this query
        daily_searches = (
            SearchHistory.objects.filter(
                user=user,
                query=query,
                timestamp__gte=start_date,
                timestamp__lte=end_date,
            )
            .annotate(date=TruncDate("timestamp"))
            .values("date")
            .annotate(daily_count=Count("id"))
            .count()
        )

        # Calculate searches per day (multiplied by 100 to store as integer)
        # If no days have searches, default to 100 (1 search per day)
        if daily_searches == 0:
            return 100

        frequency = (daily_searches / days) * 100
        return int(frequency)

    @staticmethod
    def save_search_query(user: User, query: str, search_type: str):
        try:
            search_history, created = SearchHistory.objects.get_or_create(
                user=user,
                query=query,
                defaults={
                    "search_type": search_type,
                    "search_count": 1,
                    "last_searched": timezone.now(),
                    "search_frequency": SearchUtils.calculate_frequency(user, query),
                },
            )

            if not created:
                search_history.search_count += 1
                search_history.search_type = search_type
                search_history.last_searched = timezone.now()
                # Update frequency based on recent search history
                search_history.search_frequency = SearchUtils.calculate_frequency(
                    user, query
                )
                search_history.save()

            return search_history

        except Exception as e:
            print(f"An error occurred while saving the search. {e}")
            return None

    @staticmethod
    def get_user_search_patterns(user, days=30):
        """
        Get search patterns for a specific user

        Args:
            user (User): User to analyze
            days (int): Number of days to analyze

        Returns:
            dict: User search pattern statistics
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        searches = SearchHistory.objects.filter(
            user=user, timestamp__gte=start_date, deleted=False
        )

        patterns = {
            "total_searches": searches.count(),
            "unique_queries": searches.values("query").distinct().count(),
            "top_queries": searches.values("query")
            .annotate(count=Count("id"), avg_frequency=Avg("search_frequency"))
            .order_by("-count")[:5],
            "search_times": searches.annotate(hour=ExtractHour("timestamp"))
            .values("hour")
            .annotate(count=Count("id"))
            .order_by("hour"),
            "most_recent": searches.order_by("-timestamp").values("query", "timestamp")[
                :5
            ],
        }

        return patterns
