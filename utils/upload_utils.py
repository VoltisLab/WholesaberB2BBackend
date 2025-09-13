import os
import tempfile
import boto3
import uuid
import logging
from accounts.models import User
from django.conf import settings
from typing import List
from PIL import Image

logger = logging.getLogger(__name__)


KEY_PREFIX = "wms"

class UploadUtil:

    @staticmethod
    def upload_file(files: list, user: User, upload_type: str) -> List[dict]:
        try:
            # S3 connection
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_SERVER_PUBLIC_KEY,
                aws_secret_access_key=settings.AWS_SERVER_SECRET_KEY,
            )
            # Define folder for user-specific uploads
            folder = user.username if user.username else uuid.uuid4().hex[:6]
            # Initialize response array
            response = []

            for file in files:
                # Create unique identifier for the file
                file_uuid = uuid.uuid4().hex[:6]
                extension = "png" if upload_type == settings.OUTFEATZ else "jpeg"
                file_key = f"{KEY_PREFIX}/{upload_type.lower()}/{folder}/{file_uuid}.{extension}"

                # Convert and upload the main file to S3
                with Image.open(file) as img:
                    # For OUTFEATZ, remove the background
                    if upload_type == settings.OUTFEATZ:
                        processed_img = UploadUtil.remove_background(img)
                    else:
                        # For other upload types, convert to RGB as before
                        processed_img = UploadUtil.convert_to_rgb(img)

                    # converted_img = (
                    #     UploadUtil.convert_to_rgb(img)
                    #     if upload_type != settings.OUTFEATZ
                    #     else img
                    # )  # Convert to RGB mode if not OutFeatz

                    # Save the processed image to a temporary file
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=f".{extension}"
                    ) as temp_file:
                        if upload_type == settings.OUTFEATZ:
                            # PNG format for transparent background
                            processed_img.save(temp_file, format="PNG")
                        else:
                            processed_img.save(temp_file, format="JPEG")

                        # converted_img.save(temp_file, format="JPEG")
                        temp_file.flush()
                        # Upload the processed file to S3
                        with open(temp_file.name, "rb") as file_obj:
                            s3.upload_fileobj(
                                file_obj,
                                settings.BUCKET,
                                file_key,
                                ExtraArgs={"ACL": "public-read"},
                            )
                        temp_file.close()
                        os.remove(temp_file.name)

                # Check if the upload_type matches PROFILE_PICTURE or PRODUCT
                thumbnail_key = None
                if upload_type in [
                    settings.PROFILE_PICTURE,
                    settings.PRODUCT,
                    settings.OUTFEATZ,
                ]:
                    # Set thumbnail size based on upload_type
                    thumbnail_size = (
                        (150, 150)
                        if upload_type == settings.PROFILE_PICTURE
                        else (450, 450)
                    )
                    thumbnail_key = f"{KEY_PREFIX}/{upload_type.lower()}/{folder}/{file_uuid}_thumbnail.{extension}"

                    # Process and create the thumbnail
                    with Image.open(file) as img:
                        if upload_type == settings.OUTFEATZ:
                            processed_img = UploadUtil.remove_background(img)
                        else:
                            processed_img = UploadUtil.convert_to_rgb(img)
                        # converted_img = (
                        #     UploadUtil.convert_to_rgb(img)
                        #     if upload_type != settings.OUTFEATZ
                        #     else img
                        # )  # Convert to RGB mode if not OutFeatz

                        # Create thumbnail
                        processed_img.thumbnail(thumbnail_size)

                        # Save the thumbnail to a temporary file
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=".jpeg"
                        ) as thumbnail_temp:
                            if upload_type == settings.OUTFEATZ:
                                processed_img.save(thumbnail_temp, format="PNG")
                            else:
                                processed_img.save(thumbnail_temp, format="JPEG")

                            # converted_img.save(thumbnail_temp, format="JPEG")
                            thumbnail_temp.flush()
                            # Upload the thumbnail to S3
                            with open(thumbnail_temp.name, "rb") as thumbnail_file:
                                s3.upload_fileobj(
                                    thumbnail_file,
                                    settings.BUCKET,
                                    thumbnail_key,
                                    ExtraArgs={"ACL": "public-read"},
                                )
                            thumbnail_temp.close()
                            os.remove(thumbnail_temp.name)

                # Append the response with the file key and optionally the thumbnail key
                response.append(
                    {
                        "image": file_key,
                        "thumbnail": thumbnail_key,
                        "success": True,
                        "message": "File uploaded successfully",
                        "extension": extension,
                    }
                )

            return response
        except Exception as err:
            logger.error(f"Exception: {err}")
            return [
                {"success": False, "message": str(err), "file_url": "", "extension": ""}
            ]

    @staticmethod
    def delete_file(file_urls: List[str], file_type: str) -> bool:
        try:
            # Initialize the S3 client
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_SERVER_PUBLIC_KEY,
                aws_secret_access_key=settings.AWS_SERVER_SECRET_KEY,
                # region_name=settings.REGION_NAME, # Uncomment if you need a specific region
            )

            # Prepare list of objects to delete
            keys = []

            for url in file_urls:
                # Extract the key by removing the base URL part
                if url.startswith(settings.UPLOAD_BASE_URL):
                    key = url.split(settings.UPLOAD_BASE_URL)[1]
                else:
                    key = url

                keys.append({"Key": key})

                # If the file type supports thumbnails, delete the thumbnail as well
                if file_type in [settings.PROFILE_PICTURE, settings.PRODUCT]:
                    base_name, extension = os.path.splitext(key)
                    thumbnail_key = f"{base_name}_thumbnail{extension}"
                    keys.append({"Key": thumbnail_key})

            # Perform the deletion of objects from S3
            s3.delete_objects(Bucket=settings.BUCKET, Delete={"Objects": keys})
            logger.info(f"Keys to delete: {keys}")

            return True

        except Exception as err:
            # Log the exception for debugging
            logger.error(f"Exception occurred while deleting files: {err}")
            return False

    @staticmethod
    def convert_to_rgb(img: Image.Image) -> Image.Image:
        """
        Convert an image to RGB mode, handling transparency appropriately.

        Args:
            img: PIL Image object to convert

        Returns:
            PIL Image object in RGB mode
        """
        if img.mode in ("RGBA", "LA") or (
            img.mode == "P" and "transparency" in img.info
        ):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
            return background
        elif img.mode != "RGB":
            return img.convert("RGB")
        return img

    @staticmethod
    def remove_background(input_image):
        """
        Removes the background from an image and returns the processed image.

        Args:
            input_image (PIL.Image.Image): The input image.

        Returns:
            PIL.Image.Image: The image with the background removed.
        """
        try:
            # Remove the background
            output_image = remove(input_image)
            return output_image
        except Exception as e:
            logger.error(f"Error removing background: {e}")
            return None
