from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=50, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=10)
    address = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=50, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=10)
    address = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Menu(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menus')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='menus',default=1)

    def __str__(self):
        return self.name


class Order(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    menu_items = models.ManyToManyField(Menu, related_name='orders')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE,default=1)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders',default=1)

