from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm, ProductForm
from django.http import HttpResponse

from .models import Product, Cart, CartItem, Order, Comment


@staff_member_required
def admin_panel(request):
    """
    Wyświetla panel z produktami do zatwierdzenia.
    """
    products_to_approve = Product.objects.select_related('category', 'author').filter(is_approved=False).order_by('-created_at')
    context = {
        'products_to_approve': products_to_approve
    }
    # Zmieniamy ścieżkę, aby pasowała do lokalizacji pliku: shop/templates/admin_panel.html
    return render(request, 'admin_panel.html', context)


@staff_member_required
def approve_product(request, product_id):
    """
    Zatwierdza produkt. Oczekuje żądania POST.
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.is_approved = True
        product.save()
    return redirect('admin_panel')


@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def sell_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.author = request.user  # Poprawiona nazwa pola
            product.save()
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'sell.html', {'form': form})


@login_required
def browse_products(request):
    """
    Wyświetla listę wszystkich zatwierdzonych produktów (memów) i liczbę rzeczy w koszyku.
    """
    products = Product.objects.filter(is_approved=True).order_by('-created_at')

    # Liczba przedmiotów w koszyku
    try:
        cart = request.user.cart
        cart_count = sum(item.quantity for item in cart.items.all())
        if cart_count > 9:
            cart_count_display = "9+"
        else:
            cart_count_display = str(cart_count)
    except Cart.DoesNotExist:
        cart_count_display = "0"

    context = {
        'products': products,
        'cart_item_count': cart_count_display
    }
    return render(request, 'browse_products.html', context)


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Cart.objects.create(user=user)  # Utworzenie koszyka dla nowego użytkownika
            messages.success(request, "Konto zostało utworzone. Możesz się zalogować.")
            return redirect('login')
        else:
            messages.error(request, "Popraw błędy w formularzu.")
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def cart_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    return render(request, 'cart.html', {'cart': cart})


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_approved=True)
        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        messages.success(request, f'Produkt "{product.name}" został dodany do koszyka.')
    return redirect('browse_products')

@login_required
def user_panel(request):
    """
    Panel użytkownika - pokazuje jego produkty i zamówienia.
    """
    user_products = Product.objects.filter(author=request.user).order_by('-created_at')
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'user_products': user_products,
        'user_orders': user_orders
    }
    return render(request, 'user_panel.html', context)


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, author=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ogłoszenie zostało zaktualizowane.')
            return redirect('user_panel')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, author=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Ogłoszenie zostało usunięte.')
        return redirect('user_panel')
    return render(request, 'confirm_delete.html', {'product': product})


def cart_item_count(request):
    """
    Dodaje do kontekstu liczbę pozycji w koszyku użytkownika.
    """
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            count = sum(item.quantity for item in cart.items.all())
            if count > 9:
                count_display = "9+"
            else:
                count_display = str(count)
        except Cart.DoesNotExist:
            count_display = "0"
    else:
        count_display = "0"
    return {'cart_item_count': count_display}


@login_required
def add_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.quantity += 1
    item.save()
    return redirect('cart')

@login_required
def subtract_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        # Jeśli ilość wynosi 1 i klikniemy "-", usuń produkt
        item.delete()
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart')


from .forms import RejectProductForm
from .models import Notification


@staff_member_required
def reject_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()
        if not reason:
            messages.error(request, "Musisz podać powód odrzucenia.")
            return redirect('admin_panel')

        # Tworzymy powiadomienie dla użytkownika
        Notification.objects.create(
            user=product.author,
            message=f"Twój produkt '{product.name}' został odrzucony przez administratora. Powód: {reason}"
        )

        # Usuwamy produkt
        product.delete()
        messages.success(request, f"Produkt '{product.name}' został odrzucony i użytkownik powiadomiony.")
        return redirect('admin_panel')

    return render(request, 'reject_product.html', {'product': product})


@login_required
def product_detail(request, product_id):
    """
    Strona szczegółów pojedynczego produktu z możliwością dodawania komentarzy.
    """
    product = get_object_or_404(Product, id=product_id, is_approved=True)
    comments = product.comments.filter(is_approved=True).order_by('-created_at')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(
                product=product,
                author=request.user,
                content=content,
                is_approved=True  # Można zmienić na False jeśli chcesz moderację
            )
            messages.success(request, "Twój komentarz został dodany.")
            return redirect('product_detail', product_id=product.id)
        else:
            messages.error(request, "Komentarz nie może być pusty.")

    context = {
        'product': product,
        'comments': comments,
    }
    return render(request, 'product_detail.html', context)
