from django.core.management.base import BaseCommand
from accounts.models import User
from notifications.models import NotificationPreference
from django.core.management.color import color_style
from django.db.models import OuterRef, Exists

style = color_style()


class Command(BaseCommand):
    help = "Create or update notification preferences for all users"

    def handle(self, *args, **options):
        batch_size = 1000
        users = User.objects.annotate(
            has_preferences=Exists(
                NotificationPreference.objects.filter(user=OuterRef("pk"))
            )
        )

        total_users = users.count()
        created_count = 0
        updated_count = 0

        # Get all field names except 'id' and 'user'
        fields_to_update = [
            field.name
            for field in NotificationPreference._meta.fields
            if field.name not in ["id", "user"]
        ]

        for i in range(0, total_users, batch_size):
            batch_users = users[i : i + batch_size]

            to_create = []
            to_update = []

            for user in batch_users:
                if user.has_preferences:
                    pref = user.notification_preferences
                    # Update all fields with default values
                    for field in fields_to_update:
                        setattr(pref, field, getattr(NotificationPreference(), field))
                    to_update.append(pref)
                    updated_count += 1
                else:
                    to_create.append(NotificationPreference(user=user))
                    created_count += 1

            NotificationPreference.objects.bulk_create(to_create)
            if to_update:
                NotificationPreference.objects.bulk_update(
                    to_update, fields=fields_to_update
                )

            self.stdout.write(
                style.SUCCESS(
                    f"Processed {min(i + batch_size, total_users)} out of {total_users} users"
                )
            )

        self.stdout.write(
            style.SUCCESS(f"Created {created_count} new notification preferences")
        )
        self.stdout.write(
            style.SUCCESS(f"Updated {updated_count} existing notification preferences")
        )
        self.stdout.write(style.SUCCESS("All notification preferences processed"))
