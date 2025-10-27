from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """
    Model profilu użytkownika, rozszerzający standardowy model User o role.
    """
    USER_ROLES = (
        ('user', 'Użytkownik'),
        ('moderator', 'Moderator'),
        ('admin', 'Administrator'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=USER_ROLES, default='user', verbose_name='Rola')

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'


class Category(models.Model):
    """
    Model kategorii dla produktów.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='Nazwa')
    description = models.TextField(blank=True, verbose_name='Opis')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class ModeratorCategory(models.Model):
    """
    Model do przypisywania moderatorów do kategorii.
    """
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'moderator'})
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('moderator', 'category')
        verbose_name_plural = "Moderator Categories"

    def __str__(self):
        return f'{self.moderator.username} moderuje {self.category.name}'


class Product(models.Model):
    """
    Model produktu (lub posta).
    """
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='Kategoria', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Autor')
    name = models.CharField(max_length=200, verbose_name='Nazwa')
    description = models.TextField(verbose_name='Opis (obsługuje HTML)', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Cena')
    image = models.ImageField(upload_to='products/', verbose_name='Obraz', null=True, blank=True)
    stock = models.PositiveIntegerField(default=1, verbose_name='Stan magazynowy')
    is_approved = models.BooleanField(default=False, verbose_name='Zatwierdzony')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name




class Comment(models.Model):
    """
    Model komentarzy do produktów.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', verbose_name='Produkt')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Autor')
    content = models.TextField(verbose_name='Treść')
    is_approved = models.BooleanField(default=False, verbose_name='Zatwierdzony')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Komentarz od {self.author.username} do {self.product.name}'


class Order(models.Model):
    """
    Model zamówienia.
    """
    ORDER_STATUS = (
        ('pending', 'Oczekujące'),
        ('processing', 'W trakcie realizacji'),
        ('shipped', 'Wysłane'),
        ('delivered', 'Dostarczone'),
        ('cancelled', 'Anulowane'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Użytkownik')
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending', verbose_name='Status')
    shipping_address = models.TextField(verbose_name='Adres wysyłki')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Zamówienie nr {self.id} od {self.user.username}'


class OrderItem(models.Model):
    """
    Model pozycji w zamówieniu.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Zamówienie')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Produkt')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Ilość')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Cena w momencie zakupu')

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'


class Cart(models.Model):
    """
    Model koszyka.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Koszyk użytkownika {self.user.username}'


class CartItem(models.Model):
    """
    Model pozycji w koszyku.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'


class Notification(models.Model):
    """
    Model powiadomień dla użytkowników.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='Użytkownik')
    message = models.TextField(verbose_name='Wiadomość')
    is_read = models.BooleanField(default=False, verbose_name='Odczytane')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Powiadomienie dla {self.user.username}'