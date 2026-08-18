from django.contrib import admin
from .models import (
    Drug,
    Order,
    OrderItem,
    Sale,
    SaleItem
)

# Kusajili models zote kwenye Django Admin Panel
admin.site.register(Drug)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Sale)
admin.site.register(SaleItem)