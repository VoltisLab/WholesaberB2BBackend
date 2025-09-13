import base64
from io import BytesIO
import graphene
import tempfile
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from non_modular_schema.enums.non_modular_enums import FileTypeEnum

from utils.non_modular_utils.errors import ErrorException, StandardError
from utils.upload_utils import UploadUtil
from PIL import Image


class UploadPictures(graphene.Mutation):
    class Arguments:
        filetype = FileTypeEnum(required=True)
        files = graphene.List(Upload, required=True)

    base_url = graphene.String()
    data = graphene.List(graphene.JSONString)
    success = graphene.Boolean()

    # @login_required
    def mutate(self, info, **kwargs):
        filetype = kwargs.get("filetype")
        files = kwargs.get("files")
        user = info.context.user

        # Debug print statements
        print(f"Debug: filetype = {filetype}")
        print(f"Debug: files = {files}")
        print(f"Debug: user = {user}")

        # Validate filetype
        valid_filetypes = [
            settings.PROFILE_PICTURE,
            settings.PRODUCT,
            settings.BANNER,
            settings.OUTFEATZ,
            settings.RESOURCES,
            settings.VIDEO,
        ]

        if filetype.value not in valid_filetypes:
            raise GraphQLError(f"Invalid filetype '{filetype}'")

        temp_files = []
        for file in files:
            temp = tempfile.NamedTemporaryFile(
                delete=False
            )  # This ensure file is not deleted after closing
            temp.write(file.read())
            temp.flush()  # Write any unwritten data
            temp_files.append(temp.name)

        upload_response = UploadUtil.upload_file(temp_files, user, filetype.value)

        return UploadPictures(
            base_url=settings.UPLOAD_BASE_URL,
            data=upload_response,
            success=upload_response[0]["success"],
        )

class DeleteMediaFiles(graphene.Mutation):
    class Arguments:
        file_urls = graphene.List(graphene.String)
        filetype = FileTypeEnum(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, **kwargs):
        file_urls = kwargs.get("file_urls")
        filetype = kwargs.get("filetype")

        response = UploadUtil.delete_file(file_urls, filetype)

        return DeleteMediaFiles(success=response)


class Mutation(graphene.ObjectType):
    upload = UploadPictures.Field()
    delete_media_files = DeleteMediaFiles.Field()
    # remove_background = RemoveBackgroundMutation.Field()
    # contact_message = ContactMessageMutation.Field()
