from store.models import Category, Cart
def custom_data(request):
    if request.user.is_authenticated:
        count = Cart.objects.filter(user=request.user).count()
        return {
            'cart_count': count,
        }
    else:
        return {}