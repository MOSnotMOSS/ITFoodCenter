from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'address', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Branch Name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Branch Address', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }
        phone_number = forms.CharField(max_length=10)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must be numeric.")
        
        return phone



class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=10, required=True)
    address = forms.CharField(max_length=200, required=True)

    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'password', 'confirm_password']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError("Phone number must be numeric.")
        
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data
        

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'price', 'category']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise ValidationError("Price must be greater than 0.")
        return price

