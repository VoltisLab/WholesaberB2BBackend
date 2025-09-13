import hashlib
from functools import wraps
from typing import Optional
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache

from graphql.error import GraphQLError

def is_admin(func):
    @wraps(func)
    def wrapper(self, info, *args, **kwargs):
        user = info.context.user

        # Check if the user is authenticated
        if isinstance(user, AnonymousUser):
            raise GraphQLError("Authentication credentials were not provided.")

        # Check if the user is an admin (is_staff or is_superuser)
        if not (user.is_staff or user.is_superuser):
            raise GraphQLError("You do not have permission to perform this action.")

        return func(self, info, *args, **kwargs)

    return wrapper


def user_verified_required(func):
    @wraps(func)
    def wrapper(self, info, **kwargs):
        user = info.context.user

        if not getattr(user, "status", None) or not user.status.verified:
            raise GraphQLError("Verification is required to perform this action.")
        return func(self, info, **kwargs)

    return wrapper


def cache_resolver(timeout=300):
    """
    Cache decorator for GraphQL resolvers that considers user-specific data.

    Args:
        timeout (int): Cache timeout in seconds (default: 300 seconds / 5 minutes)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, info, **kwargs):
            # Generate a cache key based on function name, user, and kwargs

            username = kwargs.get("username", None)
            user_identifier = username if username else str(info.context.user.username)

            cache_parts = [
                func.__name__,
                user_identifier,
            ]

            cache_key = hashlib.md5("_".join(cache_parts).encode()).hexdigest()

            # Get cached result
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # If not cached, execute the resolver
            result = func(self, info, **kwargs)

            # Cache the result
            cache.set(cache_key, result, timeout)

            return result

        return wrapper

    return decorator


def cache_sizes(timeout=3600):  # Cache for 1 hour
    def decorator(func):
        @wraps(func)
        def wrapper(self, info, **kwargs):
            path = kwargs.get("path")
            path = path.split(" > ")[:2]
            path = "_".join(path)
            cache_key = f"sizes:{path}"
            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # If not in cache, run the function to get resut from database
            result = func(self, info, **kwargs)

            # Store in cache
            cache.set(cache_key, list(result), timeout)

            return result

        return wrapper

    return decorator


def cache_categories(timeout=3600):  # Cache for 1 hour
    def decorator(func):
        @wraps(func)
        def wrapper(self, info, **kwargs):
            parent_id = kwargs.get("parent_id", None)
            cache_key = f"categories_{parent_id}" if parent_id else "categories"
            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # If not in cache, run the function to get resut from database
            result = func(self, info, **kwargs)

            # Store in cache
            cache.set(cache_key, list(result), timeout)

            return result

        return wrapper

    return decorator


class CacheManager:
    """
    A utility class to handle cache key generation and invalidation.
    """

    @staticmethod
    def generate_cache_key(function_name, username):
        """
        Generate a cache key based on the function name, user, and additional arguments.

        Args:
            function_name (str): The name of the function/resolver.
            user: The user object whose data is being cached.
            kwargs: Additional arguments to include in the cache key.

        Returns:
            str: The generated cache key.
        """
        cache_parts = [
            function_name,
            username,
        ]
        return hashlib.md5("_".join(cache_parts).encode()).hexdigest()

    @staticmethod
    def invalidate_cache(function_name: str, username: Optional[str] = None):
        """
            Invalidate the cached result by deleting the cache entry for the given key.

        Args:
            function_name (str): The name of the function/resolver.
            username (Optional[str]): The username whose cache entry should be invalidated.

        Returns:
            None
        """
        if function_name.startswith("resolve_"):
            cache_key = CacheManager.generate_cache_key(function_name, username)
        else:
            cache_key = function_name

        if cache_key:
            cache.delete(cache_key)

    @staticmethod
    def invalidate_all_category_caches():
        """
        Invalidates all category-related caches
        """
        # Clear main categories cache
        cache.delete("categories")

        # Clear parent category caches
        for key in cache.keys("categories_*"):
            cache.delete(key)

    @staticmethod
    def invalidate_all_size_caches():
        """
        Invalidates all image size-related caches.
        """
        # Find and delete all cache keys that start with 'sizes:'
        for key in cache.keys("sizes:*"):
            cache.delete(key)
