from rest_framework import serializers
from .models import ProductModel,ReviewModel,CustomerModel
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        discount_price = serializers.ReadOnlyField()
        fields = ['id','product_name', 'description', 'product_category', 'color', 'trend_order', 'actual_price', 'discount_price', 'stocks', 'image_id', 'discount_percentage', 'is_return_policy', 'return_before', 'delivered_within']
        read_only_fields = ["id", "discount_price", "created_at", "updated_at"]
    def discount_price(self):
        return round(self.actual_price * (1 - (self.discount_percentage / 100)), 2)

    def create(self, validated_data):
        validated_data["discount_price"]=(validated_data["actual_price"]-((validated_data["actual_price"]*validated_data["discount_percentage"])/100)) 
        return ProductModel.objects.create(**validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)  
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = ReviewModel
        exclude = ["customer"] 
        read_only_fields = ['id', 'created_at']  

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise AuthenticationFailed("Request object is missing.")
        auth = JWTAuthentication()
        try:
            validated_token = auth.get_validated_token(request.headers.get('Authorization').split(" ")[1])
            user = auth.get_user(validated_token) 
            customer = CustomerModel.objects.get(user=user)
        except CustomerModel.DoesNotExist:
            raise AuthenticationFailed("No customer associated with this user.")
        except Exception:
            raise AuthenticationFailed("Invalid or expired token.")
        validated_data["customer"] = customer  
        return super().create(validated_data)

