from django.db.models import Q


def get_exclusion_queries(user_field: str = "user"):
    """
    Returns exclusion conditions for a specified user-related field.

    Args:
        user_field (str): The name of the user-related field to apply the conditions to
                          (e.g., 'user', 'owner', 'reviewer', 'post_owner').

    Returns:
        Q: A Q object representing the combined exclusion conditions.
    """
    return (
        Q(**{f"{user_field}__is_active": False})
        | Q(**{f"{user_field}__deleted": True})
        | Q(**{f"{user_field}__is_banned": True})
    )
