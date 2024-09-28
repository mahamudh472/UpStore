from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('customers/', views.customers, name='customers'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.cart, name='cart'),
    path('product-details/<int:id>', views.productDetails, name='product-details'),
    path('add-to-cart/', views.addToCart, name='add-to-cart'),
    path('remove-from-cart/<int:id>', views.removeFromCart, name='remove-from-cart'),
]
