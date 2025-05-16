from rest_framework import serializers
from .models import CartModel, FavoriteModel
from products.models import ProductModel


class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name") 
    customer_name = serializers.ReadOnlyField(source="customer.name")
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartModel
        fields ="__all__"
        read_only_fields = ['unit_price', 'total_price', 'created_at', 'updated_at']

    def get_total_price(self, obj):
        return obj.quantity * obj.unit_price

    def create(self, validated_data):
        product = validated_data.get("product")
        quantity = validated_data.get("quantity")
        unit_price = product.actual_price
        total_price = quantity * unit_price

        validated_data["unit_price"] = unit_price
        validated_data["total_price"] = total_price
        return super().create(validated_data)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = ['id', 'product_name', 'actual_price', 'discount_price', 'image_id']

class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=ProductModel.objects.all(), source='product', write_only=True)

    class Meta:
        model = FavoriteModel
        fields = ['id', 'product', 'product_id', 'created_at']