from django.db import models
from core.globalchoices import (PRODUCTS_CHOICES,
                                COLOR_CHOICES,
                                RATING_CHOICES)
from core.models import  ColorModel, ImageModel
from accounts.models import (SellerModel,
                             CustomerModel)
from decimal import Decimal


UNIT_CHOICES = [
    ('kg', 'Kilogram'),
    ('g', 'Gram'),
    ('litre', 'Litre'),
    ('ml', 'Millilitre'),
    ('piece', 'Piece'),
    ('pack', 'Pack'),
]

class ProductModel(models.Model):
    seller = models.ForeignKey(SellerModel, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    product_category = models.CharField(max_length=50, choices=PRODUCTS_CHOICES, null=True, blank=True)
    color_available = models.ForeignKey(ColorModel, on_delete=models.SET_NULL, null=True, blank=True)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)
    trend_order = models.IntegerField()
    actual_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stocks = models.PositiveIntegerField()
    image_id = models.ImageField(upload_to="images/", null=True, blank=True)
    discount_percentage = models.PositiveIntegerField(default=0)
    is_return_policy = models.BooleanField(default=False)
    return_before = models.CharField(max_length=255)
    delivered_within = models.CharField(max_length=255)
    product_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='piece')  # ✅ New Field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    @property
    def calculated_discount_price(self):
        discount_rate = Decimal(self.discount_percentage) / Decimal('100')
        discounted_price = self.actual_price * (Decimal('1.0') - discount_rate)
        return round(discounted_price, 2)

    def save(self, *args, **kwargs):
        if self.discount_percentage > 0:
            self.discount_price = self.calculated_discount_price
        else:
            self.discount_price = self.actual_price  # or None
        super().save(*args, **kwargs)

# models.py
class ReviewModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1 to 5 stars
    customer = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer} - {self.product} ({self.rating})"

    @property
    def stars(self):
        return "★" * self.rating + "☆" * (5 - self.rating)  # Display as stars (★ = filled, ☆ = empty)
