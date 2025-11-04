from .models import Cart

def cart_item_count(request):
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            count = sum(item.quantity for item in cart.items.all())
            return {'cart_item_count': count if count <= 9 else '9+'}
        except Cart.DoesNotExist:
            return {'cart_item_count': 0}
    return {'cart_item_count': 0}
