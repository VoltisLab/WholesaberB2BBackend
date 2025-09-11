import os
import boto3
from django.conf import settings
from products.models import Product
from django.core.management.base import BaseCommand
import tempfile
from PIL import Image
from django.db import transaction


class Command(BaseCommand):
    help = "Update thumbnails for all products in batches"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=20,
            help="Number of products to process in each batch",
        )
        parser.add_argument(
            "--start-id", type=int, help="Start processing from this product ID"
        )

    def __init__(self):
        super().__init__()
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_SERVER_PUBLIC_KEY,
            aws_secret_access_key=settings.AWS_SERVER_SECRET_KEY,
            region_name=settings.AWS_SERVER_REGION_NAME,
        )
        self.tmp_dir = "tmp"
        os.makedirs(self.tmp_dir, exist_ok=True)

    def handle(self, *args, **kwargs):
        batch_size = kwargs["batch_size"]
        start_id = kwargs.get("start_id")

        try:
            query = Product.objects.order_by("id")
            if start_id:
                query = query.filter(id__gte=start_id)

            total_products = query.count()
            processed = 0

            while processed < total_products:
                with transaction.atomic():
                    batch = query[processed : processed + batch_size]
                    self.process_batch(batch)
                    processed += batch_size
                    self.stdout.write(
                        f"Processed {min(processed, total_products)}/{total_products} products"
                    )

                self.cleanup_tmp_dir()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
        finally:
            self.cleanup_tmp_dir()

    def process_batch(self, products):
        for product in products:
            if not product.images_url:
                self.stdout.write(
                    self.style.ERROR(f"No images found for product {product.id}")
                )
                continue
            thumbnails = [image["thumbnail"] for image in product.images_url]
            for thumbnail in thumbnails:
                try:
                    s3_key = self.get_s3_key(thumbnail)
                    if not s3_key:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Invalid S3 key for thumbnail {thumbnail}"
                            )
                        )
                        continue

                    # original_key = s3_key.replace("_thumbnail", "")
                    local_file_path = self.download_from_s3(s3_key)

                    if local_file_path:
                        self.delete_from_s3(s3_key)
                        thumbnail_key = self.process_and_upload_thumbnail(
                            local_file_path, product.seller.username
                        )

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Updated thumbnail for product {product.id}"
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error processing product {product.id}: {str(e)}"
                        )
                    )

    def cleanup_tmp_dir(self):
        if os.path.exists(self.tmp_dir):
            for file in os.listdir(self.tmp_dir):
                try:
                    os.remove(os.path.join(self.tmp_dir, file))
                except OSError:
                    pass

    def delete_from_s3(self, s3_key):
        """Delete a file from S3."""

        # Delete the file from S3
        self.s3.delete_object(Bucket=settings.BUCKET, Key=s3_key)

        return True

    def get_s3_key(self, url):
        # target_substring = "d1q0jm5ujs3rwb"
        target_substring = "d2j4biyfasje1u"
        base_url = "https://d2j4biyfasje1u.cloudfront.net/"

        # Ensure the URL contains the exact substring and starts with the base URL
        if target_substring in url and url.startswith(base_url):
            return url[len(base_url) :]

        return None

    def get_file_uuid(self, file_path):
        filename = os.path.basename(file_path)
        file_uuid = os.path.splitext(filename)[0]

        return file_uuid

    def process_and_upload_thumbnail(self, file_path, username):
        # Determine the thumbnail size based on the upload type
        thumbnail_size = (450, 450)
        file_uuid = self.get_file_uuid(file_path)

        # Construct the thumbnail S3 key
        thumbnail_key = f"product/{username}/{file_uuid}_thumbnail.jpeg"

        # Process and create the thumbnail
        with Image.open(file_path) as img:
            img.thumbnail(thumbnail_size)

            # Save the thumbnail to a temporary file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".jpeg"
            ) as thumbnail_temp:
                img.save(thumbnail_temp, format="JPEG")
                thumbnail_temp.flush()

                # Upload the thumbnail to S3
                with open(thumbnail_temp.name, "rb") as thumbnail_file:
                    s3.upload_fileobj(
                        thumbnail_file,
                        settings.BUCKET,
                        thumbnail_key,
                        ExtraArgs={"ACL": "public-read"},
                    )

                # Remove the temporary thumbnail file after upload
                thumbnail_temp.close()
                os.remove(thumbnail_temp.name)
                os.remove(file_path)

        return thumbnail_key

    def download_from_s3(self, s3_key):
        """Download a file from S3 and save it locally."""
        local_file_path = os.path.join("tmp", os.path.basename(s3_key))

        # Download the file from S3 to the local backup directory
        self.s3.download_file(settings.BUCKET, s3_key, local_file_path)

        return local_file_path
