from django.contrib import admin

from .models import Customer, Restaurant, Item, Cart, CartItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'mobile', 'is_admin', 'is_active')
    list_filter = ('is_admin', 'is_active')
    search_fields = ('username', 'email')
    readonly_fields = ('password', 'last_login', 'date_joined')


admin.site.register(Restaurant)
admin.site.register(Item)
admin.site.register(Cart)
admin.site.register(CartItem)
