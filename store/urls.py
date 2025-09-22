from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'product', views.ProductViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('customers/', views.customers, name='customers'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.cart, name='cart'),
    path('product-details/<int:id>', views.productDetails, name='product-details'),
    path('add-to-cart/', views.addToCart, name='add-to-cart'),
    path('buy-now/', views.buyNow, name='buy-now'),
    path('add-review/', views.addReview, name='add-review'),
    path('remove-from-cart/<int:id>', views.removeFromCart, name='remove-from-cart'),
    path('update-cart-item/', views.updateCartItem, name='update-cart-item'),
    path('clear-cart/', views.clearCart, name='clear-cart'),
]
urlpatterns += router.urls