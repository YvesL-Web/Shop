from django.contrib import admin
import admin_thumbnails
from .models import Product, Variation, ReviewRating, ProductGallery

# Register your models here.
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "category","stock", "is_available","modified_date","created_date"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [ProductGalleryInline]

@admin.register(Variation)
class AdminVariation(admin.ModelAdmin):
    list_display = ['product','variation_cat','variation_value','is_active']
    list_editable=['is_active']
    list_filter=['is_active','product']

admin.site.register(ProductGallery)
admin.site.register(ReviewRating)
