from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from store.models import *
from rest_framework import viewsets
from .serializer import ProductSerializer


# Create your views here.
def home(request):
    return render(request, 'store/home.html')

def products(request):
    return render(request, 'store/products.html')

def customers(request):
    return render(request, 'store/customers.html')

def cart(request):
    """Display cart items for the current user/session"""
    cart_summary = CartUtility.get_cart_summary(request)
    
    context = {
        'cart': cart_summary['cart'],
        'items': cart_summary['items'],
        'total': cart_summary['total_price'],
        'total_items': cart_summary['total_items'],
        'unique_items_count': cart_summary['unique_items_count'],
    }
    return render(request, 'store/cart.html', context)

def checkout(request):
    return render(request, 'store/checkout.html')

def productDetails(request, id):
    product = Product.objects.get(id=id)
    reviews = product.reviews.all()[:5]  # Get latest 5 reviews
    related_products = product.get_related_products()
    
    # Check if user has already reviewed this product
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(user=request.user, product=product)
        except Review.DoesNotExist:
            pass
    
    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'user_review': user_review,
    }

    return render(request, 'store/product-details.html', context)

def addToCart(request):
    """Add product to cart (works for both authenticated and anonymous users)"""
    if request.method == "POST":
        try:
            product_name = request.POST.get('product_name')
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            
            # Get product by name or ID
            if product_id:
                product = Product.objects.get(id=product_id)
            elif product_name:
                product = Product.objects.get(name=product_name)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Product identifier not provided!'
                })
            
            # Check stock availability
            if product.stock < quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Only {product.stock} items available in stock!'
                })
            
            # Add to cart using utility
            cart_item = CartUtility.add_to_cart(request, product, quantity)
            
            # Get updated cart summary
            cart_summary = CartUtility.get_cart_summary(request)
            
            return JsonResponse({
                'success': True,
                'message': 'Product added to cart successfully!',
                'cart_count': cart_summary['unique_items_count'],
                'total_items': cart_summary['total_items'],
                'cart_total': float(cart_summary['total_price'])
            })
            
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error adding product to cart: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method!'
    })

@login_required
def buyNow(request):
    """Add product to cart and redirect to checkout"""
    if request.method == "POST":
        try:
            product_name = request.POST.get('product_name')
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            
            # Get product by name or ID
            if product_id:
                product = Product.objects.get(id=product_id)
            elif product_name:
                product = Product.objects.get(name=product_name)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Product identifier not provided!'
                })
            
            # Check stock availability
            if product.stock < quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Only {product.stock} items available in stock!'
                })
            
            # Add to cart using utility
            CartUtility.add_to_cart(request, product, quantity)
            
            return JsonResponse({
                'success': True,
                'redirect': True,
                'redirect_url': '/store/checkout/'
            })
            
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error processing your request: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method!'
    })

@login_required
def addReview(request):
    if request.method == "POST":
        try:
            product_id = request.POST.get('product_id')
            rating = int(request.POST.get('rating'))
            comment = request.POST.get('comment', '')
            
            product = Product.objects.get(id=product_id)
            
            # Update or create review
            review, created = Review.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={
                    'rating': rating,
                    'comment': comment
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Review added successfully!' if created else 'Review updated successfully!'
            })
            
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error adding review!'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method!'
    })

def removeFromCart(request, id):
    """Remove product from cart"""
    try:
        product = Product.objects.get(id=id)
        success = CartUtility.remove_from_cart(request, product)
        
        if success:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # AJAX request
                cart_summary = CartUtility.get_cart_summary(request)
                return JsonResponse({
                    'success': True,
                    'message': 'Product removed from cart!',
                    'cart_count': cart_summary['unique_items_count'],
                    'total_items': cart_summary['total_items'],
                    'cart_total': float(cart_summary['total_price'])
                })
            else:
                # Regular request
                return redirect('store:cart')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Product not found in cart!'
                })
            else:
                return redirect('store:cart')
                
    except Product.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Product not found!'
            })
        else:
            return redirect('store:cart')


def updateCartItem(request):
    """Update cart item quantity via AJAX"""
    if request.method == "POST":
        try:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            
            product = Product.objects.get(id=product_id)
            
            # Check stock availability
            if product.stock < quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Only {product.stock} items available in stock!'
                })
            
            success = CartUtility.update_cart_item(request, product, quantity)
            
            if success:
                cart_summary = CartUtility.get_cart_summary(request)
                return JsonResponse({
                    'success': True,
                    'message': 'Cart updated successfully!',
                    'cart_count': cart_summary['unique_items_count'],
                    'total_items': cart_summary['total_items'],
                    'cart_total': float(cart_summary['total_price'])
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Product not found in cart!'
                })
                
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found!'
            })
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid quantity!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating cart: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method!'
    })


def clearCart(request):
    """Clear all items from cart"""
    try:
        cart = CartUtility.get_cart_for_request(request)
        cart.clear_cart()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Cart cleared successfully!'
            })
        else:
            return redirect('store:cart')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error clearing cart: {str(e)}'
            })
        else:
            return redirect('store:cart')

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

