# Tech E-Commerce API

Built with the Django REST Framework, it integrates seamlessly with the Next.js front-end application and offers a complete set of essential features. These encompass endpoints for managing application resources, authentication and authorization mechanisms, integration with a PostgreSQL database powered by Supabase, throttling, caching and other functionalities to ensure a secure and seamless e-commerce experience.

## Key Features

- **Authentication:** Utilize JWT (JSON Web Tokens) for secure user authentication.
- **Authorization:** Employ permission classes provided by Django Rest Framework (DRF) for fine-grained authorization control.
- **User Management:** Implement a robust account system, combining the built-in user model with a custom customer model. The API enforces a daily limit of creating a maximum of 50 accounts.
- **Data Validation:** Ensure data integrity by validating all incoming user data before processing.
- **Caching:** Accelerate data retrieval by caching GET requests for optimized performance.
- **Throttling:** Enhance security by incorporating throttling mechanisms that recognize the X-Forwarded-For header from the Front-End app.
- **Public Resources:** Allow unauthenticated users to access and view public resources such as brands, categories, products, and reviews, as well as create new accounts.
- **Product Search:** Enable unauthenticated users to perform product searches.
- **Account Management:** Empower authenticated users to update their account information or delete their accounts.
- **Shopping Cart and Favorites:** Authenticated users can create, delete, or manage products in their shopping carts or favorites lists, with a maximum limit of 10 cart items and 25 favorites per user.
- **Product Purchases:** Authenticated users can initiate product purchases, creating orders that store order items, including quantity, total price, and more. Each user can have a maximum of 3 active orders and buy up to 10 products per order. The API enforces a daily limit of creating a maximum of 100 orders.
- **Product Reviews:** Authenticated users can write reviews for their purchased products, with the ability to update or delete them. These reviews are hidden by default until approved. Users can also like, dislike, or report product reviews. The API has a daily limit of creating a maximum of 100 reviews.
- **Coupons:** Authenticated users can use coupons to apply discounts to their purchases.
- **Purchase History:** Authenticated users can easily access their purchase history, providing a convenient platform to review their purchased products, delve into order details, and report any issues related to delivery or product quality.

## API Endpoints

Here are the key API endpoints available:

### Products

- **List Products:** `GET /products/` - Retrieve a list of all products.
- **Retrieve Product:** `GET /products/<int:product_id>` - Retrieve details of a specific product.

### Brands

- **List Brands:** `GET /brands/` - Retrieve a list of all brands.

### Categories

- **List Categories:** `GET /categories/` - Retrieve a list of all product categories.

### Search

- **Search Products:** `GET /search/<str:search>` - Search for products based on a query string.

### Customer

- **Retrieve Customer:** `GET /customer/` - Retrieve customer information.
- **Create Customer:** `POST /customer/create/` - Create a new customer account.
- **Update Customer:** `PATCH /customer/update/` - Update customer account information.
- **Delete Customer:** `DELETE /customer/delete/` - Delete customer account.
- **List Customer Interactions:** `GET /customer/interactions/` - List customer interactions.

### Cart

- **List Cart Items:** `GET /cart/` - Retrieve a list of items in the shopping cart.
- **Create Cart Item:** `POST /cart/create/<int:product_id>` - Add a product to the shopping cart.
- **Delete Cart Item:** `DELETE /cart/delete/<int:product_id>` - Remove a product from the shopping cart.
- **Move Cart Item:** `PATCH /cart/move/<int:product_id>` - Move a product from the shopping cart to favorites.

### Favorites

- **List Favorite Items:** `GET /favorites/` - Retrieve a list of favorite items.
- **Create Favorite Item:** `POST /favorites/create/<int:product_id>` - Add a product to the favorites list.
- **Delete Favorite Items:** `DELETE /favorites/delete/<intlist:product_ids>` - Remove multiple products from favorites.
- **Move Favorite Item:** `PATCH /favorites/move/<int:product_id>` - Move a product from favorites to the shopping cart.

### Purchase

- **Create Purchase (Order):** `POST /purchase/` - Initiate a product purchase by creating an order.
- **Update Purchase (Order):** `PATCH /purchase/<int:order_id>/update/` - Update order details.
- **Delete Purchase (Order):** `DELETE /purchase/<int:order_id>/delete/` - Delete an order.

### Purchase History

- **List Purchase History:** `GET /purchase/history/` - Retrieve a list of past and active purchases.
- **Retrieve Purchase History Item:** `GET /purchase/history/<int:order_item_id>` - Retrieve details of a specific purchased product.

### Reviews

- **Like Review:** `PATCH /reviews/<int:review_id>/like/` - Like a product review.
- **Dislike Review:** `PATCH /reviews/<int:review_id>/dislike/` - Dislike a product review.
- **Report Review:** `PATCH /reviews/<int:review_id>/report/` - Report a product review.
- **List Product Reviews:** `GET /reviews/product/<int:product_id>` - Retrieve a list of reviews for a specific product.
- **Create Product Review:** `POST /reviews/product/<int:product_id>/create/` - Create a new product review.
- **Update Product Review:** `PATCH /reviews/product/<int:product_id>/update/` - Update a product review.
- **Delete Product Review:** `DELETE /reviews/product/<int:product_id>/delete/` - Delete a product review.

### Coupons

- **List Coupons:** `GET /coupons/` - Retrieve a list of available coupons.

These endpoints provide various functionalities for managing products, customers, orders, reviews, and more within the API.

## Testing

The application leverages the `APITestCase` class provided by Django Rest Framework (DRF), mirroring the structure of the pre-existing `TestCase` class in Django. For every existing view, there exists a dedicated test case meticulously designed to emulate genuine API interactions by employing mock data.

## Authentication

To implement authentication, I utilized JSON Web Tokens (JWT) through the `djangorestframework-simplejwt` package. You can locate the routes associated with simple JWT in the `/project/urls.py` file.

## Authorization

To establish authorization, I harnessed the power of DRF's permission classes. By default, the `AllowAny` permission class is employed for views where the `permission_classes` property is not explicitly specified. For all other views, the choice between the `IsAuthenticated` class and the `get_permissions` method is made, dynamically determining whether to use `AllowAny` or `IsAuthenticated` based on specific criteria.

## Throttle

To control the rate of incoming requests, the API employs the `AnonRateThrottle` and `UserRateThrottle` classes provided by DRF. These throttles enforce limits on both anonymous and authenticated requests per day:

- The anonymous rate limit is currently set to: `3600/day`.
- The authenticated rate limit is currently set to: `7200/day`.

## License

This project is licensed under the [MIT License](https://github.com/GoTierGod/react-calculator/blob/main/LICENSE.md).
