from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Profile,
    Category,
    ModeratorCategory,
    Product,
    Comment,
    Order,
    OrderItem,
    Cart,
    CartItem,
    Notification,
)

# Rejestracja modeli w panelu administracyjnym
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(ModeratorCategory)
admin.site.register(Product)
admin.site.register(Comment)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Notification)