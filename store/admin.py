from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Product, Review, CartItem, Order, OrderItem, Category


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff', 'is_superuser')
    readonly_fields = ('uuid',)

    fieldsets = UserAdmin.fieldsets + (
        ('Extra info', {'fields': ('uuid', 'user_type')}),
    )


admin.site.register(Product)
admin.site.register(Review)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Category)