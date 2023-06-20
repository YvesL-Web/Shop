from django.contrib import admin

from .models import Product, Variation
# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "category","stock", "is_available","modified_date","created_date"]
    prepopulated_fields = {"slug": ["name"]}

@admin.register(Variation)
class AdminVariation(admin.ModelAdmin):
    list_display = ['product','variation_cat','variation_value','is_active']
    list_editable=['is_active']
    list_filter=['is_active','product']