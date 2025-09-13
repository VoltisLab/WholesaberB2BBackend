import graphene
from graphql import GraphQLError
from django.db import transaction

from reviews.models import Review, ReviewHelpful, ReviewResponse, ProductRating, VendorRating
from reviews.schema.types import ReviewType, ReviewHelpfulType, ReviewResponseType
from reviews.schema.inputs import ReviewInput, ReviewResponseInput, ReviewHelpfulInput
from products.models import Product


class CreateReviewMutation(graphene.Mutation):
    """Create a product review"""
    
    class Arguments:
        review_data = ReviewInput(required=True)
    
    review = graphene.Field(ReviewType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, review_data):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            product = Product.objects.get(id=review_data.product_id)
            
            # Check if user already reviewed this product
            existing_review = Review.objects.filter(
                user=user,
                product=product
            ).first()
            
            if existing_review:
                raise GraphQLError("You have already reviewed this product")
            
            # Validate rating
            if not (1 <= review_data.rating <= 5):
                raise GraphQLError("Rating must be between 1 and 5")
            
            with transaction.atomic():
                # Create review
                review = Review.objects.create(
                    product=product,
                    user=user,
                    rating=review_data.rating,
                    title=review_data.title,
                    comment=review_data.comment,
                    images=review_data.images or [],
                )
                
                # Update product rating
                product_rating, created = ProductRating.objects.get_or_create(
                    product=product
                )
                product_rating.update_rating()
                
                # Update vendor rating
                vendor_rating, created = VendorRating.objects.get_or_create(
                    vendor=product.seller
                )
                vendor_rating.update_rating()
                
                return CreateReviewMutation(
                    review=review,
                    success=True,
                    message="Review created successfully"
                )
                
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
        except Exception as e:
            raise GraphQLError(f"Failed to create review: {str(e)}")


class UpdateReviewMutation(graphene.Mutation):
    """Update a product review"""
    
    class Arguments:
        review_id = graphene.ID(required=True)
        review_data = ReviewInput(required=True)
    
    review = graphene.Field(ReviewType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, review_id, review_data):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            review = Review.objects.get(id=review_id, user=user)
            
            # Validate rating
            if not (1 <= review_data.rating <= 5):
                raise GraphQLError("Rating must be between 1 and 5")
            
            with transaction.atomic():
                # Update review
                review.rating = review_data.rating
                review.title = review_data.title
                review.comment = review_data.comment
                review.images = review_data.images or []
                review.save()
                
                # Update product rating
                product_rating, created = ProductRating.objects.get_or_create(
                    product=review.product
                )
                product_rating.update_rating()
                
                # Update vendor rating
                vendor_rating, created = VendorRating.objects.get_or_create(
                    vendor=review.product.seller
                )
                vendor_rating.update_rating()
                
                return UpdateReviewMutation(
                    review=review,
                    success=True,
                    message="Review updated successfully"
                )
                
        except Review.DoesNotExist:
            raise GraphQLError("Review not found")
        except Exception as e:
            raise GraphQLError(f"Failed to update review: {str(e)}")


class DeleteReviewMutation(graphene.Mutation):
    """Delete a product review"""
    
    class Arguments:
        review_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, review_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            review = Review.objects.get(id=review_id, user=user)
            product = review.product
            
            with transaction.atomic():
                review.delete()
                
                # Update product rating
                product_rating, created = ProductRating.objects.get_or_create(
                    product=product
                )
                product_rating.update_rating()
                
                # Update vendor rating
                vendor_rating, created = VendorRating.objects.get_or_create(
                    vendor=product.seller
                )
                vendor_rating.update_rating()
                
                return DeleteReviewMutation(
                    success=True,
                    message="Review deleted successfully"
                )
                
        except Review.DoesNotExist:
            raise GraphQLError("Review not found")
        except Exception as e:
            raise GraphQLError(f"Failed to delete review: {str(e)}")


class CreateReviewResponseMutation(graphene.Mutation):
    """Create a vendor response to a review"""
    
    class Arguments:
        response_data = ReviewResponseInput(required=True)
    
    review_response = graphene.Field(ReviewResponseType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, response_data):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            review = Review.objects.get(id=response_data.review_id)
            
            # Check if user is the vendor of the product
            if review.product.seller != user:
                raise GraphQLError("You can only respond to reviews of your products")
            
            # Check if response already exists
            if hasattr(review, 'response'):
                raise GraphQLError("Response already exists for this review")
            
            review_response = ReviewResponse.objects.create(
                review=review,
                vendor=user,
                response=response_data.response
            )
            
            return CreateReviewResponseMutation(
                review_response=review_response,
                success=True,
                message="Response created successfully"
            )
            
        except Review.DoesNotExist:
            raise GraphQLError("Review not found")
        except Exception as e:
            raise GraphQLError(f"Failed to create response: {str(e)}")


class MarkReviewHelpfulMutation(graphene.Mutation):
    """Mark a review as helpful or not helpful"""
    
    class Arguments:
        helpful_data = ReviewHelpfulInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, helpful_data):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        
        try:
            review = Review.objects.get(id=helpful_data.review_id)
            
            if helpful_data.is_helpful:
                # Add helpful vote
                helpful, created = ReviewHelpful.objects.get_or_create(
                    review=review,
                    user=user
                )
                if created:
                    review.is_helpful += 1
                    review.save()
                    message = "Review marked as helpful"
                else:
                    message = "You have already marked this review as helpful"
            else:
                # Remove helpful vote
                try:
                    helpful = ReviewHelpful.objects.get(review=review, user=user)
                    helpful.delete()
                    review.is_helpful = max(0, review.is_helpful - 1)
                    review.save()
                    message = "Helpful vote removed"
                except ReviewHelpful.DoesNotExist:
                    message = "No helpful vote to remove"
            
            return MarkReviewHelpfulMutation(
                success=True,
                message=message
            )
            
        except Review.DoesNotExist:
            raise GraphQLError("Review not found")
        except Exception as e:
            raise GraphQLError(f"Failed to mark review helpful: {str(e)}")


class ReviewMutations(graphene.ObjectType):
    create_review = CreateReviewMutation.Field()
    update_review = UpdateReviewMutation.Field()
    delete_review = DeleteReviewMutation.Field()
    create_review_response = CreateReviewResponseMutation.Field()
    mark_review_helpful = MarkReviewHelpfulMutation.Field()
