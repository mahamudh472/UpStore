from django.shortcuts import render, redirect
from store.models import *
# Create your views here.
def home(request):
    return render(request, 'store/home.html')

def products(request):
    return render(request, 'store/products.html')

def customers(request):
    return render(request, 'store/customers.html')

def cart(request):
    items = Cart.objects.filter(user=request.user)
    total = 0
    for item in items:
        total += item.quantity * item.product.price

    context = {
        'items': items,
        'total': total
    }
    return render(request, 'store/cart.html', context)

def checkout(request):
    return render(request, 'store/checkout.html')

def productDetails(request, id):
    product = Product.objects.get(id=id)
    context = {
        'product': product
    }

    return render(request, 'store/product-details.html', context)

def addToCart(request):
    if request.method == "POST":
        product_name = request.POST['product_name']
        quantity = request.POST['quantity']
        product = Product.objects.get(name=product_name)
        print(product)
        cart = Cart.objects.update_or_create(
            user=request.user,
            name=product.name,
            product = product,
            quantity=quantity
        )
       
        return redirect('store:cart')

def removeFromCart(request, id):
    product = Product.objects.get(id=id)

    Cart.objects.get(name=product.name).delete()
    return redirect('store:cart')