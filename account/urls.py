from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('register/', views.register_view, name="register"),
    
    path('activate/<uidb64>/<token>/', views.email_activation, name='email_activation'),
    path('forgot_password/', views.forgot_password, name="forgot_password"),
    path('reset_password_email/<uidb64>/<token>/', views.reset_password_email, name='reset_password_email'),
    path('reset_password/', views.reset_password, name='reset_password'),

    path('my_order/', views.my_order, name='my_order'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
]
