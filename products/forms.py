from django.forms import ModelForm, forms

from products.models import ProductModel

class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = ['id','product_name', 'description', 'product_category', 'color', 'trend_order', 'actual_price', 'discount_price', 'stocks', 'image_id', 'discount_percentage', 'is_return_policy', 'return_before', 'delivered_within']
