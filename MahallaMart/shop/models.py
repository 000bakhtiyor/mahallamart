from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    svg = models.TextField()
    description = models.TextField()

    def __str__(self):
        return self.name

class Shop(models.Model):
    shop_name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.shop_name

# shop/models.py

class Product(models.Model):
    UNIT_CHOICES = [
        ('kg', 'kg'),
        ('l', 'l'),
        ('m', 'm'),
        ('dona', 'dona'),
    ]

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField()
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='dona')
    image_url = models.URLField(blank=True, null=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return f"{self.name} ({self.unit})"

class Offer(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    discount_percent = models.PositiveIntegerField()
    valid_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ProductDiscount(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='discount')
    percent = models.PositiveIntegerField()
    valid_from = models.DateField()
    valid_until = models.DateField()

    def is_valid(self):
        from datetime import date
        today = date.today()
        return self.valid_from <= today <= self.valid_until

    def discounted_price(self):
        return self.product.price - (self.product.price * self.percent / 100)

    def __str__(self):
        return f"{self.percent}% off on {self.product.name}"
