from rest_framework import serializers
from orders.models import OrderModel
from cart.models import CartModel

from accounts.models import UserManagementModel, CustomerModel

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserManagementModel
        fields = ['first_name', 'last_name', 'email', 'phone_no', 'address_1', 'address_2', 'landmark', 'city', 'district', 'state', 'pincode']

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = CustomerModel
        fields = ['id', 'clo_coin', 'customer_rank', 'user']


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    product_name = serializers.CharField(source='product.product_name', read_only=True)

    class Meta:
        model = OrderModel
        fields = ['id', 'product_name', 'customer', 'quantity', 'order_status', 'total_price', 'created_at']