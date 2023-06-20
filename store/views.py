from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .models import Product
from category.models import Category
from cart.models import CartItem
from cart.views import _cart_id

# Create your views here.
def store(request, category_slug=None):
    category = None
    products = None
    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True).order_by('-created_date')
        paginator = Paginator(products, 3)
        page_number = request.GET.get("page")
        page_product = paginator.get_page(page_number)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('-created_date')
        paginator = Paginator(products, 3)
        page_number = request.GET.get("page")
        page_product = paginator.get_page(page_number)
        product_count = products.count()
    context = {
        "products": page_product,
        "product_count": product_count,
        
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug ,slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id =_cart_id(request), product=single_product ).exists()
    except Exception as e:
        raise e

    context= {
        'single_product': single_product,
        'in_cart': in_cart,
    }

    return render(request, 'store/product_detail.html', context)

def search(request):

    if request.method == "GET":
        keyword = request.GET['keyword']
        if len(keyword) > 0:
            products = Product.objects.filter(Q(description__icontains=keyword) | Q(name__icontains=keyword)).order_by("-created_date")
            product_count = products.count()
        else:
            return redirect("store")

    context = {
        'products': products,
        "product_count": product_count,
        'keyword': keyword
    }

    return render(request, 'store/store.html', context)