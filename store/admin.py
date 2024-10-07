from django.contrib import admin
from .models import Product, Category, Cart
# Register your models here.
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource

# admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)