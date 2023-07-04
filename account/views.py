from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

import requests

# email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from .models import Account, UserProfile
from .forms import RegistrationForm, UserProfileForm, UserForm
from cart.views import _cart_id
from cart.models import Cart, CartItem
from order.models import Order, OrderProduct

# Create your views here.
def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            print(first_name)
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password = password,
            )
            user.phone_number = phone_number
            user.save() 

            # User Account activation
            current_site = get_current_site(request)
            mail_subject = 'Activation account.'
            message = render_to_string('account/account_verification_email.html',{
                'user':user,
                'domain': current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), # encoding user pk
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request,'Account successfully created.Please check your email, we have sent you an email to activate your account.') 
            return redirect('/account/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'account/register.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(email=email, password=password)   
        if user is not None: 
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    product_variation = []
                    # getting product variations by cart id
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                    # getting the cart items for a specific user 
                    cart_item = CartItem.objects.filter(user=user)
                    existing_variations_list=[]
                    id=[]
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        existing_variations_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    # product_variation = [1,2,3,4,6,...]
                    # existing_variations_list = [1,2,3,5..]
                    # find common product variation
                    for pr_variation in product_variation:
                        if pr_variation in existing_variations_list:
                            index = existing_variations_list.index(pr_variation)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass

            login(request, user)
            messages.success(request, "You are logged in!")
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                # print("query->:",query)
                # for example : next=/cart/checkout/
                params = dict(x.split('=') for x in query.split("&"))
                # print("params=",params)   //for example {'next': '/account/logout/'}
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
               return redirect("dashboard")
        else:
            messages.error(request, "email or password is incorrect")
            return redirect("login")  
    return render(request, 'account/login.html')

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, "You are now logged out!")
    return redirect('login')

def email_activation(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been successfully activated.")
        return redirect('login')
    else:
        messages.error(request,'Invalid activation link.')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.filter(user_id=request.user.id, is_ordered=True).order_by("-created_at")
    orders_count = orders.count()
    context = {
        'orders_count':orders_count,
    }
    return render(request, 'account/dashboard.html', context)

def forgot_password(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email):
            user= Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Password'
            message = render_to_string('account/reset_password_email.html',{
                'user':user,
                'domain': current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), # encoding user pk
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('login')
        else:
            messages.error(request, "Account does not exist.")
            return redirect('forgot_password')
    return render(request, 'account/forgot_password.html')

def reset_password_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password.")
        return  redirect('reset_password')
    else:
        messages.error(request, "This link has already expired!")
        return redirect('login')
    
def reset_password(request):
    if request.session.get('uid') == None:
        return redirect('home')
    
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password successfully reset.")
            return redirect('login')
        else:
            messages.error(request,'Password does not match!')
            return redirect('reset_password')

    return render(request, 'account/reset_password_page.html')

@login_required(login_url='login')
def my_order(request):
    orders = Order.objects.filter(user= request.user, is_ordered=True).order_by("-created_at")
    context={
        "orders":orders,
    }
    return render(request, 'account/my_order.html', context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile ,user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("edit_profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
            
    return render(request,"account/edit_profile.html", context)

@login_required(login_url='login')
def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_new_password = request.POST['confirm_new_password']

        user = Account.objects.get(username__exact= request.user.username)

        if new_password == confirm_new_password:
            correct_current_password = user.check_password(current_password)
            if correct_current_password:
                user.set_password(new_password)
                user.save()
                # logout(request) if you to logout the user after chnaging the password.
                messages.success(request,'Your password has been successfully changed.')
                return redirect('change_password')
            else:
                messages.error(request,"Invalide Current Password ")
                return redirect('change_password')
        else:
            messages.error(request,"Password does not match.")
            return redirect('change_password')
    return render(request, "account/change_password.html")

@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number = order_id)
    sub_total = 0
    for i in order_detail:
        sub_total += i.product_price * i.quantity

    context = {
        "order_detail":order_detail,
        "order": order,
        "sub_total": sub_total
    }
    return render(request, "account/order_detail.html", context)