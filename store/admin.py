from django.contrib import admin
from .models import *
 
class OrderAdmin(admin.ModelAdmin):
    list_filter = ['customer','complete','date_ordered', ]
    list_display = ['id', 'customer', 'complete','date_ordered', 'get_cart_total', 'get_cart_items', ]
    class Meta:
        model = Order
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Improve)
