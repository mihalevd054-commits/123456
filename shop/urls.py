from django.urls import path
from django.contrib.auth.views import LoginView
from . import views
from .forms import CustomLoginForm   # импортируем форму входа
from . import views

urlpatterns = [
    path('', views.GameListView.as_view(), name='home'),
    path('games/add/', views.GameCreateView.as_view(), name='game_create'),
    path('games/<slug:slug>/', views.GameDetailView.as_view(), name='game_detail'),
    path('games/<slug:slug>/edit/', views.GameUpdateView.as_view(), name='game_update'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/<slug:category_slug>/', views.GameListView.as_view(), name='category_games'),
    path('publishers/', views.PublisherListView.as_view(), name='publisher_list'),
    path('publishers/<int:pk>/', views.PublisherGamesView.as_view(), name='publisher_games'),
    path('register/', views.register, name='register'),
    # Используем нашу форму для входа
    path('logout/', views.custom_logout, name='logout'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('checkout/', views.checkout, name='checkout'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
]