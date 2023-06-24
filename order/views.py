from django.http import HttpResponse
from django.shortcuts import render, redirect

import datetime

from cart.models import CartItem
from .forms import OrderForm
from .models import Order

# Create your views here.
def payment(request):
    return render(request, "order/payment.html")

def place_order(request):
    current_user = request.user
    #  if the cart is empty, the redirect to the shop
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("store")

    tax= 0
    total = 0
    quantity = 0
    grand_total = 0

    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = tax + total

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone_number = form.cleaned_data['phone_number']
            data.address = form.cleaned_data['address']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.country = form.cleaned_data['country']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META['REMOTE_ADDR']
            data.save()
            # generate order number
            yr =int(datetime.date.today().strftime('%Y'))
            dt =int(datetime.date.today().strftime('%d'))
            mt =int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%d%m%Y")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total
            }
            return render(request,'order/payment.html',context)
        else:
            form = OrderForm()
            return redirect ('checkout')
        
            

