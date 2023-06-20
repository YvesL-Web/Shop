from .models import Cart, CartItem
from .views import _cart_id

def cart_items_counter(request):
    item_count= 0
    if "admin" in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            cart_items = CartItem.objects.all().filter(cart = cart[:1])
            for item in cart_items:
                item_count += item.quantity
        except Cart.DoesNotExist:
            item_count = 0
    context={
        "item_count": item_count
    }

    return context