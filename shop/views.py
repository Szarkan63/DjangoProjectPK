from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse

from .forms import SignUpForm, ProductForm, OrderForm, HideProductForm
from django.http import HttpResponse

from .models import Product, Cart, CartItem, Order, Comment, OrderItem, Category


@staff_member_required()
def admin_panel(request):
    view_type = request.GET.get('view', 'products')

    products_to_approve_list = Product.objects.filter(is_approved=False).order_by('-created_at')
    comments_to_approve_list = Comment.objects.filter(is_approved=False).order_by('-created_at')
    # Poprawiono prefetch_related na 'items__product'
    orders_to_approve_list = Order.objects.filter(status='pending_approval').prefetch_related('items__product').order_by('-created_at')
    all_products_list = Product.objects.all().order_by('-created_at')

    products_count = products_to_approve_list.count()
    comments_count = comments_to_approve_list.count()
    orders_count = orders_to_approve_list.count()
    all_products_count = all_products_list.count()

    page_obj = None
    items_per_page = 4

    if view_type == 'products':
        paginator = Paginator(products_to_approve_list, items_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    elif view_type == 'comments':
        paginator = Paginator(comments_to_approve_list, items_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    elif view_type == 'orders':
        paginator = Paginator(orders_to_approve_list, items_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    elif view_type == 'all_products':
        paginator = Paginator(all_products_list, items_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    context = {
        'view_type': view_type,
        'page_obj': page_obj,
        'products_to_approve_count': products_count,
        'comments_to_approve_count': comments_count,
        'orders_to_approve_count': orders_count,
        'all_products_count': all_products_count,
    }
    return render(request, 'admin_panel.html', context)





@staff_member_required
def approve_product(request, product_id):
    if not request.user.is_staff:
        return redirect('home')
    product = get_object_or_404(Product, id=product_id)
    product.is_approved = True
    product.save()
    return redirect('admin_panel')



@login_required
def home(request):
    products = Product.objects.filter(is_approved=True)[:10]  # Pobieramy 10 zatwierdzonych produktów
    return render(request, 'home.html', {'products': products})



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
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    products = Product.objects.filter(is_approved=True, is_hidden=False, hidden_by_admin=False)

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()
    return render(request, 'browse_products.html', {
        'products': products,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None
    })



@login_required
def toggle_hide_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, author=request.user)
    product.is_hidden = not product.is_hidden
    product.save()
    return redirect('user_panel')




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
    user = request.user
    # Filtrujemy produkty, które nie są ukryte przez admina
    user_products = Product.objects.filter(author=user, hidden_by_admin=False).order_by('-created_at')
    user_orders = Order.objects.filter(user=user).order_by('-created_at')
    user_notifications = Notification.objects.filter(user=user).order_by('-created_at')

    return render(request, 'user_panel.html', {
        'user_products': user_products,
        'user_orders': user_orders,
        'user_notifications': user_notifications,
    })




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
    product = get_object_or_404(Product, id=product_id)
    comments = product.comments.filter(is_approved=True).order_by('-created_at')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                product=product,
                author=request.user,
                content=content
            )
            messages.success(request, 'Twój komentarz został dodany i czeka na zatwierdzenie.')
            return redirect('product_detail', product_id=product.id)

    context = {
        'product': product,
        'comments': comments
    }
    return render(request, 'product_detail.html', context)

@login_required
def approve_comment(request, comment_id):
    if not request.user.is_staff:
        return redirect('home')
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = True
    comment.save()
    messages.success(request, f"Komentarz do '{comment.product.name}' został zatwierdzony.")
    return redirect(f"{reverse('admin_panel')}?view=comments")

@login_required
def reject_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.profile.role != 'admin':
        return redirect('home')

    comment.is_approved = False
    comment.save()

    # Utworzenie powiadomienia dla autora komentarza
    Notification.objects.create(
        user=comment.author,
        message=f'Twój komentarz do produktu "{comment.product.name}" został odrzucony.'
    )

    return redirect('admin_panel', view='comments')




@staff_member_required
def hide_product_by_admin(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = HideProductForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            product.hidden_by_admin = True
            product.save()

            if product.author:
                Notification.objects.create(
                    user=product.author,
                    message=f'Twoje ogłoszenie "{product.name}" zostało ukryte przez administratora z powodu: {reason}'
                )

            redirect_url = reverse('admin_panel') + '?view=all_products'
            return redirect(redirect_url)
    else:
        form = HideProductForm()

    return render(request, 'hide_product_by_admin.html', {'form': form, 'product': product})



@staff_member_required
def restore_product_by_admin(request, product_id):
    """
    Przywraca produkt, który został wcześniej ukryty przez administratora,
    i wysyła powiadomienie do autora ogłoszenia.
    """
    product = get_object_or_404(Product, id=product_id)
    product.hidden_by_admin = False
    product.save()

    # Utworzenie powiadomienia dla autora ogłoszenia
    if product.author:
        Notification.objects.create(
            user=product.author,
            message=f'Dobra wiadomość! Twoje ogłoszenie "{product.name}" zostało przywrócone przez administratora i jest ponownie widoczne w serwisie.'
        )

    # Przekierowanie z powrotem do panelu admina z odpowiednim widokiem
    redirect_url = reverse('admin_panel') + '?view=all_products'
    return redirect(redirect_url)




@login_required
def create_order(request):
    cart = Cart.objects.get(user=request.user)
    if not cart.items.exists():
        messages.info(request, "Twój koszyk jest pusty.")
        return redirect('cart_view')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.status = 'pending_approval'
            order.save()

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )

            cart.items.all().delete()
            return redirect('order_success')
    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'create_order.html', context)



@login_required
def order_success(request):
    return render(request, 'order_success.html')


@staff_member_required
def approve_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'processing'
    order.save()
    Notification.objects.create(
        user=order.user,
        message=f"Twoje zamówienie #{order.id} zostało zatwierdzone i jest w trakcie realizacji."
    )
    messages.success(request, f"Zamówienie #{order.id} zostało zatwierdzone.")
    return redirect('admin_panel')

@staff_member_required
def reject_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()
        if not reason:
            messages.error(request, "Musisz podać powód odrzucenia.")
            return render(request, 'reject_order.html', {'order': order})

        order.status = 'rejected'
        order.rejection_reason = reason
        order.save()

        Notification.objects.create(
            user=order.user,
            message=f"Twoje zamówienie #{order.id} zostało odrzucone. Powód: {reason}"
        )

        messages.success(request, f"Zamówienie #{order.id} zostało odrzucone, a użytkownik powiadomiony.")
        return redirect('admin_panel')

    return render(request, 'reject_order.html', {'order': order})


