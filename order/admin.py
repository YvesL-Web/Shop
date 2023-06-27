from django.contrib import admin

from .models import Order, Payment, OrderProduct
# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields =['payment','user','product','quantity','product_price','ordered']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','full_name','email','order_total','is_ordered']   
    list_filter = ['is_ordered']
    search_fields = ['order_number',"first_name",'last_name',"email","phone"]
    list_per_page = 10
    inlines = [OrderProductInline]


admin.site.register(Payment)
admin.site.register(OrderProduct)
