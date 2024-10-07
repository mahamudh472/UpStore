from django.shortcuts import render
from store.models import Product, Category, Cart
from django.http import HttpResponse
# Create your views here.
def home(request):
    porducts = Product.objects.all()
    context = {
        'products': porducts
    
    }
    return render(request,'index.html', context)


def about(request):
    return render(request,'main/about.html')

def contact(request):
    return render(request,'main/contact.html')

def handler404(self, *args, **kwargs):
    return render(self, '404.html')