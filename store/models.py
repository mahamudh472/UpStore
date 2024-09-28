from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
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

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    image_url = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self) -> str:
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.OneToOneField(Product, on_delete=models.CASCADE, default=None, null=True, blank=True)
    name = models.CharField(max_length=255)
    quantity = models.IntegerField()

    def __unicode__(self):
        return self.name
    def subtotal(self):
        return self.product.price * self.quantity