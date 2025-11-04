# shop/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from shop.models import Product


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
