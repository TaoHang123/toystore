from django.contrib import admin
from .models import Vendors, Customers, Products, Orders, OrderItems, Addresses
admin.site.register(Vendors)
admin.site.register(Customers)
admin.site.register(Products)
admin.site.register(Orders)
admin.site.register(OrderItems)
admin.site.register(Addresses)

# Register your models here.
