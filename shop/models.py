import os

from PIL import Image
from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, F

from DjangoProjectPK import settings


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
    Model reprezentujący kategorię produktu.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ('name',)

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])



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
    image = models.ImageField(upload_to='products/', verbose_name='Obraz', null=True, blank=True)


    # Rozmiar docelowy obrazów (np. 600x600 px)
    TARGET_WIDTH = 600
    TARGET_HEIGHT = 600

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img_path = os.path.join(settings.MEDIA_ROOT, self.image.name)
            img = Image.open(img_path)

            # Konwersja do RGB (dla obrazów PNG z alfa)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            img = img.resize((self.TARGET_WIDTH, self.TARGET_HEIGHT), Image.LANCZOS)
            img.save(img_path)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='Kategoria')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Autor')
    name = models.CharField(max_length=200, verbose_name='Nazwa')
    description = models.TextField(verbose_name='Opis (obsługuje HTML)', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Cena')
    image = models.ImageField(upload_to='products/', verbose_name='Obraz', null=True, blank=True)
    stock = models.PositiveIntegerField(default=1, verbose_name='Stan magazynowy')
    is_approved = models.BooleanField(default=False, verbose_name='Zatwierdzony')
    is_hidden = models.BooleanField(default=False, verbose_name="Ukryty")
    created_at = models.DateTimeField(auto_now_add=True)
    hidden_by_admin = models.BooleanField(default=False, verbose_name="Ukryty przez administratora")
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
    PAYMENT_METHODS = (
        ('card', 'Karta płatnicza'),
        ('blik', 'BLIK'),
        ('przelew', 'Przelew bankowy'),
    )

    ORDER_STATUS = (
        ('pending_approval', 'Oczekuje na zatwierdzenie'),
        ('pending', 'Oczekujące'),
        ('processing', 'W trakcie realizacji'),
        ('shipped', 'Wysłane'),
        ('delivered', 'Dostarczone'),
        ('canceled', 'Anulowane'),
        ('rejected', 'Odrzucone'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50,default='')
    last_name = models.CharField(max_length=50,default='')
    city = models.CharField(max_length=100,default='')
    street_address = models.CharField(max_length=255,default='')
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending_approval')
    rejection_reason = models.TextField(blank=True, null=True)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='card'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Zamówienie nr {self.id} dla {self.user.username}"

    @property
    def total_price(self):
        return self.items.aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total'] or 0



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

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """
    Model pozycji w koszyku.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    @property
    def total_price(self):
        return self.quantity * self.product.price


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


