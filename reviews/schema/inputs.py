import graphene


class ReviewInput(graphene.InputObjectType):
    product_id = graphene.ID(required=True)
    rating = graphene.Int(required=True)
    title = graphene.String()
    comment = graphene.String()
    images = graphene.List(graphene.String)


class ReviewResponseInput(graphene.InputObjectType):
    review_id = graphene.ID(required=True)
    response = graphene.String(required=True)


class ReviewHelpfulInput(graphene.InputObjectType):
    review_id = graphene.ID(required=True)
    is_helpful = graphene.Boolean(required=True)
