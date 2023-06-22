from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

# email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from .models import Account
from .forms import RegistrationForm

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
            login(request,user)
            messages.success(request, "You are logged in!")
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
    return render(request, 'account/dashboard.html')

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