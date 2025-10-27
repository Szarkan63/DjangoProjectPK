from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm, ProductForm
from django.http import HttpResponse

from .models import Product


@staff_member_required
def admin_panel(request):
    """
    Wyświetla panel z produktami do zatwierdzenia.
    """
    products_to_approve = Product.objects.filter(is_approved=False).order_by('-created_at')
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
    Wyświetla listę wszystkich zatwierdzonych produktów (memów).
    """
    products = Product.objects.filter(is_approved=True).order_by('-created_at')
    context = {
        'products': products
    }
    return render(request, 'browse_products.html', context)


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Konto zostało utworzone. Możesz się zalogować.")
            return redirect('login')
        else:
            messages.error(request, "Popraw błędy w formularzu.")
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

