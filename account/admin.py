from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Account

# Register your models here.

@admin.register(Account)
class AdminAccount(BaseUserAdmin):
    list_display = ["email","first_name", "last_name",'phone_number',"username","is_active",'date_joined','last_login']
    list_filter = ["is_admin"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["first_name","last_name",'phone_number']}),
        ("Time",{"fields":['date_joined','last_login']}),
        ("Permissions", {"fields": ["is_admin",'is_staff','is_super_admin','is_active']}),
    ]
    readonly_fields =["date_joined","last_login"]
    search_fields = ["email","username"]
    ordering = ["-date_joined"]
    filter_horizontal = []
