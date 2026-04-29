from django.contrib import admin
from .models import Game, Category, Publisher, Cart, CartItem, Order, OrderItem

admin.site.site_header = "Игротека — Администрирование"
admin.site.site_title = "Панель управления Игротекой"
admin.site.index_title = "Добро пожаловать в админ-панель магазина настольных игр"

# Базовый класс для всех ModelAdmin, подключающий кастомный CSS
class CustomAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('shop/css/admin-override.css',)
        }

# Регистрация моделей с кастомным CSS
@admin.register(Game)
class GameAdmin(CustomAdmin):
    list_display = ('name', 'price', 'category', 'publisher', 'stock')
    list_filter = ('category', 'publisher')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(CustomAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Publisher)
class PublisherAdmin(CustomAdmin):
    list_display = ('name', 'country', 'founded_year')

@admin.register(Cart)
class CartAdmin(CustomAdmin):
    list_display = ('user', 'created_at', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(CustomAdmin):
    list_display = ('cart', 'game', 'quantity')

@admin.register(Order)
class OrderAdmin(CustomAdmin):
    list_display = ('id', 'user', 'created_at', 'status', 'total')

@admin.register(OrderItem)
class OrderItemAdmin(CustomAdmin):
    list_display = ('order', 'game', 'quantity', 'price')