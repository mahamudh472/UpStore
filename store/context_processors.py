from store.models import Category, CartUtility


def custom_data(request):
    """
    Context processor to provide cart information to all templates
    """
    try:
        cart_summary = CartUtility.get_cart_summary(request)
        return {
            'cart_count': cart_summary['unique_items_count'],  # Keep old name for compatibility
            'cart_total_items': cart_summary['total_items'],
            'cart_unique_items': cart_summary['unique_items_count'],
            'cart_total_price': cart_summary['total_price'],
        }
    except Exception:
        # In case of any error, return empty cart data
        return {
            'cart_count': 0,
            'cart_total_items': 0,
            'cart_unique_items': 0,
            'cart_total_price': 0,
        }