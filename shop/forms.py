# shop/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from shop.models import Product, Order


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'image']
        labels = {
            'name': 'Tytuł',
            'category': 'Kategoria',
            'description': 'Opis',
            'price': 'Cena (PLN)',
            'image': 'Plik z memem',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'category': forms.Select(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'input', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'input', 'accept': 'image/*'}),
        }

class RejectProductForm(forms.Form):
    reason = forms.CharField(
        label="Powód odrzucenia",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Podaj powód odrzucenia ogłoszenia"}),
        required=True
    )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'city', 'street_address', 'payment_method']
        labels = {
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
            'city': 'Miasto',
            'street_address': 'Ulica i numer',
            'payment_method': 'Sposób płatności',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }

class HideProductForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea, label="Powód ukrycia")





