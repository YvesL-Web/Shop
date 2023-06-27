from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

import datetime
import json

from cart.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product

# Create your views here.
@csrf_protect
def payment(request):
    body= json.loads(request.body)
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = body['orderID'])
    #  store the transaction details inside the payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment 
    order.is_ordered = True
    order.save()

    # Move the cart items to order table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # clear cart
    CartItem.objects.filter(user=request.user).delete()

    # send email to customer
    mail_subject = 'Thank you for your order.'
    message = render_to_string('order/order_email.html',{
        'user': request.user,
        'order': order
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number' : order.order_number,
        'transID': payment.payment_id,
    }

    return JsonResponse(data)

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
    tax =(5 * total)/100
    tax = float("{:.2f}".format(tax))
    grand_total = tax + float(total)

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
        
def order_complete(request):
    order_number = request.GET['order_number']
    transID = request.GET['payment_id']
    sub_total = 0
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transID)

        for i in ordered_products:
            sub_total += i.product_price * i.quantity

        context = {
            'order': order,
            'ordered_products':ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'status': payment.status,
            'sub_total':sub_total,
        }
        return render(request, 'order/order_complete.html', context) 
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

