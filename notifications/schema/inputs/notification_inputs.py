import graphene


class NotificationsPreferenceInputType(graphene.InputObjectType):
    likes = graphene.Boolean()
    new_followers = graphene.Boolean()
    profile_view = graphene.Boolean()
    messages = graphene.Boolean()
