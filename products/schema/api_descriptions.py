USER_PRODUCT_GROUPING = """
    Retrieves a grouped list of products based on the specified `group_by` parameter.

    This method allows the user to retrieve products grouped by various categories or brands. 
    The available grouping options are:

    - **CATEGORY**: Groups products by their category (e.g., Men, Women, Kids).
    - **BRAND**: Groups products by their brand (e.g., Nike, Adidas). If the brand is `None`, the `custom_brand` field is used.
    - **TOP_BRAND**: Retrieves the top 10 brands based on the number of products a user has in each brand.

    Parameters:
    - `user_id`: The ID of the user whose products are being grouped.
    - `group_by`: The criteria to group the products. Possible values are:
        - `ProductGroupingEnum.CATEGORY`: Group by product category.
        - `ProductGroupingEnum.BRAND`: Group by brand name.
        - `ProductGroupingEnum.TOP_BRAND`: Retrieve the top 10 brands by product count.

    Returns:
    - A list of `CategoryGroupType` objects, each containing the name of the group and the count of products in that group.
    """

ALL_PRODUCTS = """
    This method is responsible for retrieving a paginated list of products based on optional filtering and search criteria. 
    The results can be filtered by various product attributes such as name, category, brand, price, condition, and more.

    Parameters:
    - `page_count`: The number of products to return per page (optional).
    - `page_number`: The page number for pagination (optional).
    - `filters`: A dictionary of optional filters that can be applied to the product search. 
      Possible keys in the `filters` dictionary include:
      - `name`: Filter products by name.
      - `brand`: Filter products by brand ID.
      - `category`: Filter products by a specific category ID.
      - "parent_category" (enum): Filters products based on the slug of parent category, 
            finding all child categories that match [MEN, WOMEN, BOYS, GIRLS, TODDLERS] prefix.
      - `custom_brand`: Filter products by custom brand.
      - `price`: Filter products by price (less than or equal to the provided price).
      - `condition`: Filter products by condition (e.g., "new", "used").
      - `size`: Filter products by size.
      - `style`: Filter products by style.
      - `status`: Filter products by status (e.g., "available", "out of stock").
      - `discount_price`: Filter products with a discount price.
      - `hashtags`: Filter products that contain specific hashtags.
    - `search`: A string to search for in the product name.

    Returns:
    - A paginated list of products matching the filters and search criteria.
    - `pagination_result`: A tuple containing:
      - `result`: A list of products for the current page.
      - `total_pages`: Total number of pages based on the current `page_count`.
      - `total_items`: Total number of products matching the filters and search criteria.

    This method also handles pagination of the results to ensure efficient retrieval of large datasets.
    """
USER_PRODUCTS = """
    This method retrieves a paginated list of products associated with a specific user (either the logged-in user or a user identified by username).
    The products can be filtered by a search term (name) and are excluded if marked as deleted.

    Parameters:
    - `page_count`: The number of products to return per page (optional).
    - `page_number`: The page number for pagination (optional).
    - `username`: The username of the seller to filter products by. If not provided, it will use the logged-in user.
    - `search`: A string to search for in the product name (optional).

    Returns:
    - A paginated list of products for the specified user.

    This method also handles pagination of the results to ensure efficient retrieval of large datasets. 
    The method will return a list of products that match the filters and pagination settings.
    """
PRODUCT = """
    This method retrieves a specific product by its ID for the logged-in user. It ensures that only products that are not deleted are returned. 
    If the product exists and the user is authorized, it will increment the product's views if the logged-in user hasn't viewed it before.

    Parameters:
    - `id`: The ID of the product to retrieve.

    Returns:
    - The `Product` object corresponding to the given ID if it exists and is not deleted, otherwise raises an error.
    """

RECOMMENDED_SELLERS = """
    The seller recommendation system works by evaluating different metrics related
    to the seller's performance over the last 30 days. Here's how it works:

    1.  Total Sales: It looks at how much the seller has sold in the last 30 days, focusing only on orders that were delivered.

    2.  Total Shop Value: It adds up the prices of all the seller's active products that are currently for sale.

    3.  Product Views: It counts how many times the seller’s products were viewed by customers in the last 30 days.

    4.  Active Listings: It counts how many products the seller currently has available for sale.

    5.  Seller Score: It combines all these metrics (sales, shop value, and views) into one score. 
        The total sales are given the most weight (50%), the shop value is given a smaller weight (30%),
        and product views are given the least weight (20%).
"""

OFFER_OVERVIEW = """
    This class encapsulates the business logic related to 
    offers and ensures consistency in actions such as accepting, rejecting, and countering offers.

    Functionality Overview:
    -----------------------
    - **Accept Offer**: Handles the logic for accepting an offer made by a buyer. This changes 
      the status of the offer to "ACCEPTED", sets an expiry time, and notifies the relevant 
      parties of the acceptance.

    - **Reject Offer**: Allows either the buyer or seller to reject an offer, changing the 
      status to "REJECTED", and notifying the opposite party about the rejection.

    - **Counter Offer**: Enables both buyers and sellers to counter an existing offer. The 
      counter action cancels the current offer and creates a new child offer linked to the 
      original (root) offer, allowing for a back-and-forth negotiation process.

    - **Offer History Management**: When an offer is accepted, rejected, or countered, the 
      entire chain of offers (parent and children) related to the original offer is retrieved 
      and included in the response to provide a full context of the negotiation.

    - **Notification System**: Automatically triggers notifications to the relevant users 
      (seller or buyer) when an offer is accepted, rejected, or countered, ensuring that 
      both parties stay informed about the status of their offers.

    Key Rules:
    -------------------
    - An offer is created by the buyer with a status of "PENDING".
    - The seller can then accept, reject, or counter the offer.
    - If countered, the current offer is cancelled, and a new offer is created as a child of 
      the original offer, forming a hierarchical negotiation structure.
    - Both buyer and seller can continue to counter offers until either party accepts or rejects.
    - No modifications can be made to an offer with a "CANCELLED" status.
    - The entire chain of offers (root and children) is retrieved to maintain a record of 
      the negotiation process.
    """
