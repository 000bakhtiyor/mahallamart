from django import forms
from .models import *

from django.utils import timezone

class ProductDiscountForm(forms.ModelForm):
    class Meta:
        model = ProductDiscount
        fields = ['product', 'percent', 'valid_from', 'valid_until']
        widgets = {
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_percent(self):
        percent = self.cleaned_data.get('percent')
        if not (0 < percent <= 100):
            raise forms.ValidationError("Chegirma 1% dan 100% gacha bo'lishi kerak.")
        return percent

    def clean(self):
        cleaned_data = super().clean()
        valid_from = cleaned_data.get("valid_from")
        valid_until = cleaned_data.get("valid_until")
        if valid_from and valid_until and valid_from > valid_until:
            raise forms.ValidationError("Boshlanish sanasi tugash sanasidan oldin bo'lishi kerak.")


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['title', 'description', 'image_url', 'discount_percent', 'valid_until']
        widgets = {
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'stock', 'unit', 'image_url', 'shop']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mahsulot nomini kiriting'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Mahsulot narxi', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Mahsulot miqdori'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/product.jpg'}),
            'shop': forms.Select(attrs={'class': 'form-control'}),
        }


class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['shop_name', 'owner_name', 'location', 'contact_number', 'image_url']

        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Do`kon nomini kiriting'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Do`kon egasi ismini kiriting'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Do`kon manzilini kiriting'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Do`kon egasi telefon raqamini kiriting'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Do`kon rasmi uchun URL manzil kiriting'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'svg', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Katalog nomi'
            }),
            'svg': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': "Katalog uchun svg rasm kiriting"
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',


                
                'rows': 4,
                'placeholder': "Katalog haqida qisqacha ma'lumot"
            }),
        }
