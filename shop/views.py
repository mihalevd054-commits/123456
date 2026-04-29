from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Game, Category, Publisher, Cart, CartItem
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django.http import JsonResponse
# Вспомогательный миксин — только для администратора
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff
    def handle_no_permission(self):
        return redirect('home')

# ---- Главная страница (список игр) ----
class GameListView(ListView):
    model = Game
    template_name = 'shop/game_list.html'
    context_object_name = 'games'
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset().select_related('category', 'publisher')
        cat_slug = self.kwargs.get('category_slug')
        if cat_slug:
            category = get_object_or_404(Category, slug=cat_slug)
            qs = qs.filter(category=category)
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(name__icontains=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        if 'category_slug' in self.kwargs:
            context['current_category'] = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        context['search_query'] = self.request.GET.get('q', '')
        return context

# ---- Детальная страница игры ----
class GameDetailView(DetailView):
    model = Game
    template_name = 'shop/game_detail.html'
    context_object_name = 'game'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publisher = self.object.publisher
        idx = (publisher.id - 1) % len(ANIMAL_EMOJIS)
        context['publisher_emoji'] = ANIMAL_EMOJIS[idx]
        return context
    
# ---- Добавление игры (только админ) ----
class GameCreateView(AdminRequiredMixin, CreateView):
    model = Game
    template_name = 'shop/game_form.html'
    fields = ['name', 'slug', 'description', 'price', 'stock', 'image', 'category', 'publisher']
    success_url = reverse_lazy('home')

# ---- Редактирование игры ----
class GameUpdateView(AdminRequiredMixin, UpdateView):
    model = Game
    template_name = 'shop/game_form.html'
    fields = ['name', 'slug', 'description', 'price', 'stock', 'image', 'category', 'publisher']
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        return reverse_lazy('game_detail', kwargs={'slug': self.object.slug})

# ---- Список категорий ----
class CategoryListView(ListView):
    model = Category
    template_name = 'shop/category_list.html'
    context_object_name = 'categories'

# ---- Список издателей ----
class PublisherListView(ListView):
    model = Publisher
    template_name = 'shop/publisher_list.html'
    context_object_name = 'publishers'

# ---- Игры издателя ----
ANIMAL_EMOJIS = ['🐺', '🦊', '🐻', '🐰', '🦝', '🐱', '🐶', '🦉', '🦌', '🐼']

class PublisherGamesView(ListView):
    model = Game
    template_name = 'shop/publisher_games.html'
    context_object_name = 'games'
    paginate_by = 12

    def get_queryset(self):
        self.publisher = get_object_or_404(Publisher, pk=self.kwargs['pk'])
        return Game.objects.filter(publisher=self.publisher)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['publisher'] = self.publisher
        # Выбираем эмодзи на основе id издателя (чтобы соответствовало порядку в каталоге)
        idx = (self.publisher.id - 1) % len(ANIMAL_EMOJIS)
        context['publisher_emoji'] = ANIMAL_EMOJIS[idx]
        return context

# ---- Регистрация (с отключением CSRF) ----
@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# ---- Корзина (с отключением CSRF для POST-запросов) ----
@login_required
@csrf_exempt
def add_to_cart(request, slug):
    game = get_object_or_404(Game, slug=slug)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, game=game)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    # Возвращаем пользователя обратно на ту страницу, откуда пришёл запрос
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'shop/cart_detail.html', {'cart': cart})

@login_required
@csrf_exempt
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart_detail')

@login_required
@csrf_exempt
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart_detail')

@csrf_exempt
def custom_logout(request):
    logout(request)
    return redirect('home')

@method_decorator(csrf_exempt, name='dispatch')
class CustomLoginView(LoginView):
    pass

@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    if not cart.items.exists():
        return redirect('cart_detail')
    # Здесь можно создать заказ, но нужны модели Order и OrderItem
    # Пока просто очистим корзину и покажем сообщение
    cart.items.all().delete()
    return render(request, 'shop/checkout_done.html', {'message': 'Заказ оформлен!'})

@method_decorator(csrf_exempt, name='dispatch')
class CustomLoginView(LoginView):
    pass
