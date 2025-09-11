from django.core.management.base import BaseCommand
from django.db import connection


from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Drops specific tables in the products app."

    def handle(self, *args, **kwargs):
        tables_to_drop = [
            "products_size",
            "products_category",
        ]

        with connection.cursor() as cursor:
            for table_name in tables_to_drop:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully dropped table {table_name}")
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error dropping table {table_name}: {str(e)}")
                    )
