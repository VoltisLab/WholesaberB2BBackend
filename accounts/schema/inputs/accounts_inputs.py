import graphene


class ProfilePictureInputType(graphene.InputObjectType):
    profile_picture_url = graphene.String()
    thumbnail_url = graphene.String()
