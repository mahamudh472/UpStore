from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


class CartManager(models.Manager):
    """Custom manager for Cart model"""
    
    def get_or_create_cart(self, user=None, session_key=None):
        """Get or create cart for user or session"""
        if user and user.is_authenticated:
            cart, created = self.get_or_create(
                user=user,
                is_active=True,
                defaults={'session_key': session_key}
            )
        else:
            cart, created = self.get_or_create(
                session_key=session_key,
                is_active=True,
                defaults={'user': None}
            )
        return cart, created

    def merge_carts(self, user_cart, session_cart):
        """Merge session cart into user cart when user logs in"""
        for session_item in session_cart.cart_items.all():
            user_item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=session_item.product,
                defaults={'quantity': session_item.quantity}
            )
            if not created:
                user_item.quantity += session_item.quantity
                user_item.save()
        
        # Delete session cart after merging
        session_cart.delete()


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField()
    stock = models.IntegerField(default=0)
    image_url = models.ImageField(upload_to='images/', null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product'
        verbose_name = 'product'
        verbose_name_plural = 'products'
    
    def __str__(self):
        return self.name
    
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum([review.rating for review in reviews]) / len(reviews)
        return 0
    
    def review_count(self):
        return self.reviews.count()
    
    def get_related_products(self, limit=4):
        return Product.objects.filter(category=self.category).exclude(id=self.id)[:limit]

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    image_url = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self) -> str:
        return self.name

class Cart(models.Model):
    """
    Cart model to store user's cart session information
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)  # For anonymous users
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    objects = CartManager()

    class Meta:
        db_table = 'cart'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Anonymous Cart {self.session_key}"

    def get_total_price(self):
        """Calculate total price of all items in cart"""
        return sum(item.get_total_price() for item in self.cart_items.all())

    def get_total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.cart_items.all())

    def get_unique_items_count(self):
        """Get count of unique products in cart"""
        return self.cart_items.count()

    def clear_cart(self):
        """Remove all items from cart"""
        self.cart_items.all().delete()

    def add_item(self, product, quantity=1):
        """Add item to cart or update quantity if exists"""
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item

    def remove_item(self, product):
        """Remove item from cart completely"""
        try:
            cart_item = CartItem.objects.get(cart=self, product=product)
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False

    def update_item_quantity(self, product, quantity):
        """Update specific item quantity"""
        try:
            cart_item = CartItem.objects.get(cart=self, product=product)
            cart_item.update_quantity(quantity)
            return True
        except CartItem.DoesNotExist:
            return False


class CartItem(models.Model):
    """
    Individual items in a cart
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_item'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')  # One product per cart
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def subtotal(self):
        """Calculate total price for this cart item"""
        return self.product.price * self.quantity

    def add_quantity(self, quantity=1):
        """Add to existing quantity"""
        self.quantity += quantity
        self.save()

    def remove_quantity(self, quantity=1):
        """Remove from existing quantity"""
        if self.quantity > quantity:
            self.quantity -= quantity
            self.save()
        else:
            self.delete()

    def update_quantity(self, quantity):
        """Update quantity to specific value"""
        if quantity <= 0:
            self.delete()
        else:
            self.quantity = quantity
            self.save()


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'product')  # One review per user per product
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.product.name} ({self.rating} stars)'


class CartUtility:
    """
    Utility class for cart operations
    """
    
    @staticmethod
    def get_cart_for_request(request):
        """Get cart for current request (handles both authenticated and anonymous users)"""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create_cart(
                user=request.user,
                session_key=request.session.session_key
            )
        else:
            # Ensure session exists
            if not request.session.session_key:
                request.session.create()
            
            cart, created = Cart.objects.get_or_create_cart(
                session_key=request.session.session_key
            )
        
        return cart

    @staticmethod
    def merge_session_cart_to_user(request):
        """Merge anonymous cart to user cart when user logs in"""
        if request.user.is_authenticated and request.session.session_key:
            try:
                # Get session cart
                session_cart = Cart.objects.get(
                    session_key=request.session.session_key,
                    user=None,
                    is_active=True
                )
                
                # Get or create user cart
                user_cart, created = Cart.objects.get_or_create_cart(
                    user=request.user
                )
                
                # Merge carts
                Cart.objects.merge_carts(user_cart, session_cart)
                
            except Cart.DoesNotExist:
                pass  # No session cart to merge

    @staticmethod
    def add_to_cart(request, product, quantity=1):
        """Add product to cart"""
        cart = CartUtility.get_cart_for_request(request)
        cart_item = cart.add_item(product, quantity)
        return cart_item

    @staticmethod
    def remove_from_cart(request, product):
        """Remove product from cart"""
        cart = CartUtility.get_cart_for_request(request)
        return cart.remove_item(product)

    @staticmethod
    def update_cart_item(request, product, quantity):
        """Update cart item quantity"""
        cart = CartUtility.get_cart_for_request(request)
        return cart.update_item_quantity(product, quantity)

    @staticmethod
    def get_cart_summary(request):
        """Get cart summary information"""
        cart = CartUtility.get_cart_for_request(request)
        return {
            'cart': cart,
            'items': cart.cart_items.all(),
            'total_price': cart.get_total_price(),
            'total_items': cart.get_total_items(),
            'unique_items_count': cart.get_unique_items_count(),
        }


@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    """
    Signal handler to merge anonymous cart with user cart when user logs in
    """
    try:
        CartUtility.merge_session_cart_to_user(request)
    except Exception:
        pass  # Silently handle any errors during cart merging