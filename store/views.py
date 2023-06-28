from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages

from category.models import Category
from cart.models import CartItem
from cart.views import _cart_id
from .forms import ReviewForm
from .models import Product, ReviewRating
from order.models import OrderProduct

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

    if request.user.is_authenticated:
        try:
            order_product = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            order_product = None
    else:
        order_product = None
    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id = single_product.id, status=True)

    context= {
        'single_product': single_product,
        'in_cart': in_cart,
        'order_product':order_product,
        'reviews': reviews
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

def submit_review(request, product_id):
    current_url = request.META.get('HTTP_REFERER') 
    print(current_url)
    if request.method == "POST":
        try:
            review = ReviewRating.objects.get(user__id = request.user.id, product__id = product_id)
            form = ReviewForm(request.POST, instance=review) # check if is already a review, if it's the case update it else create a new one 
            form.save()
            messages.success(request, "Your review as been update.")
            return redirect(current_url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, "Thank you for your review.")
                return redirect(current_url)
            else:
                form = ReviewForm()
                return redirect(current_url)
