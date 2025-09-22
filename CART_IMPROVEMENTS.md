# Cart Functionality Improvements

## Overview
The cart functionality has been completely restructured to follow e-commerce best practices and provide a better user experience.

## Problems with Previous Implementation

1. **OneToOneField Limitation**: Used `OneToOneField` between Cart and Product, meaning users could only have one cart item per product
2. **Redundant Data**: Stored product name redundantly in the cart model
3. **No Session Support**: No support for anonymous users (session-based carts)
4. **Poor Structure**: Lacked proper cart session management
5. **Missing Features**: No cart merging, item management, or proper total calculations

## New Cart Structure

### Models

#### 1. Cart Model
- **Purpose**: Represents a shopping cart session
- **Features**:
  - Supports both authenticated users and anonymous sessions
  - Tracks creation and update timestamps
  - Has active/inactive status
  - Provides methods for total calculations and cart management

#### 2. CartItem Model
- **Purpose**: Individual items within a cart
- **Features**:
  - Links cart to products with quantities
  - Unique constraint ensures one product per cart
  - Provides item-level calculations and quantity management
  - Tracks creation and update timestamps

#### 3. CartManager
- **Purpose**: Custom manager for advanced cart operations
- **Features**:
  - `get_or_create_cart()`: Handles cart creation for users/sessions
  - `merge_carts()`: Merges session cart into user cart

#### 4. CartUtility Class
- **Purpose**: High-level cart operations
- **Features**:
  - Request-aware cart management
  - Session to user cart merging
  - CRUD operations for cart items
  - Cart summary generation

## Key Features

### 1. Session-Based Carts for Anonymous Users
- Anonymous users can add items to cart using session keys
- Cart persists across pages until session expires
- Seamless experience for non-authenticated users

### 2. Cart Merging on Login
- When anonymous user logs in, their session cart merges with user cart
- Duplicate products have quantities combined
- Implemented via Django signals for automatic handling

### 3. Stock Validation
- Checks product stock before adding/updating items
- Prevents overselling and provides user feedback

### 4. Improved Cart Operations
- **Add to Cart**: Supports both product ID and name lookup
- **Update Quantity**: AJAX-enabled quantity updates
- **Remove Items**: Complete item removal from cart
- **Clear Cart**: Remove all items at once

### 5. Enhanced Admin Interface
- Detailed cart and cart item admin views
- Inline editing of cart items
- Total calculations displayed in admin
- Filtering and searching capabilities

### 6. AJAX Support
- All cart operations support AJAX requests
- Returns JSON responses with cart statistics
- Graceful fallback to page redirects for non-AJAX requests

### 7. Context Processor Integration
- Cart information available in all templates
- Backward compatibility with existing template variables
- Real-time cart counts and totals

## API Endpoints

### Existing (Updated)
- `POST /store/add-to-cart/` - Add product to cart
- `POST /store/buy-now/` - Add to cart and redirect to checkout
- `GET /store/remove-from-cart/<id>/` - Remove product from cart

### New Endpoints
- `POST /store/update-cart-item/` - Update cart item quantity
- `POST /store/clear-cart/` - Clear all cart items

## Database Changes

### Migration Details
- Removed: `name`, `product` (OneToOneField), `quantity` from Cart model
- Added: `session_key`, `is_active`, `created_at`, `updated_at` to Cart model
- Modified: `user` field now allows null values
- Created: New `CartItem` model with foreign keys to Cart and Product

## Usage Examples

### Adding to Cart (Python)
```python
from store.models import CartUtility, Product

# Add product to cart
product = Product.objects.get(id=1)
cart_item = CartUtility.add_to_cart(request, product, quantity=2)

# Get cart summary
summary = CartUtility.get_cart_summary(request)
print(f"Total items: {summary['total_items']}")
print(f"Total price: ${summary['total_price']}")
```

### AJAX Cart Operations (JavaScript)
```javascript
// Add to cart
$.post('/store/add-to-cart/', {
    'product_id': 1,
    'quantity': 2
}).done(function(data) {
    if (data.success) {
        $('#cart-count').text(data.cart_count);
        $('#cart-total').text('$' + data.cart_total);
    }
});

// Update cart item
$.post('/store/update-cart-item/', {
    'product_id': 1,
    'quantity': 3
}).done(function(data) {
    if (data.success) {
        location.reload(); // Refresh to show updated cart
    }
});
```

## Benefits

1. **Scalability**: Proper separation of cart and cart items
2. **User Experience**: Works for both anonymous and authenticated users
3. **Flexibility**: Easy to extend with features like wishlist, saved carts
4. **Performance**: Efficient queries and optimized database structure
5. **Maintainability**: Clean, well-documented code with proper error handling

## Backward Compatibility

The new implementation maintains backward compatibility with existing templates and JavaScript code by:
- Keeping the same URL patterns
- Preserving `cart_count` in context processor
- Maintaining similar JSON response structure for AJAX calls

## Future Enhancements

1. **Cart Expiration**: Automatic cleanup of old, inactive carts
2. **Saved Carts**: Allow users to save carts for later
3. **Cart Sharing**: Share cart via URL or email
4. **Bulk Operations**: Add multiple products at once
5. **Price History**: Track price changes for cart items
6. **Inventory Alerts**: Notify when cart items go out of stock
