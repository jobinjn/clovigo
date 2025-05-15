from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from orders.models import OrderModel
from cart.models import CartModel
from accounts.models import CustomerModel
from django.contrib.auth.models import AnonymousUser
from .serializers import OrderSerializer

from rest_framework.pagination import PageNumberPagination

class OrderPagination(PageNumberPagination):
    page_size = 10  # This defines the number of orders per page.
    page_size_query_param = 'page_size'  # Allows clients to specify page size via a query parameter.
    max_page_size = 100  # Max limit for page size.

class OrderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Validate serializer upfront
        serializer = OrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if isinstance(user, AnonymousUser):
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            customer = CustomerModel.objects.get(user=user)
        except CustomerModel.DoesNotExist:
            return Response({"error": "Customer profile not found."}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = CartModel.objects.filter(customer=customer)
        if not cart_items.exists():
            return Response({"error": "Cart is empty. Add items before placing an order."},
                            status=status.HTTP_400_BAD_REQUEST)

        total_quantity = sum(item.quantity for item in cart_items)
        total_price = sum(float(item.total_price) for item in cart_items)

        order_data = {
            "customer": customer,
            "quantity": total_quantity,
            "product": [
                {
                    "product": item.product.product_name,
                    "price": float(item.total_price),
                    "quantity": item.quantity
                }
                for item in cart_items
            ],
            "total_price": total_price,
            "order_status": serializer.validated_data.get("order_status", "pending")
        }

        order = OrderModel.objects.create(**order_data)

        # Optionally clear the cart after order is placed
        cart_items.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        user = request.user

        if isinstance(user, AnonymousUser):
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            customer = CustomerModel.objects.get(user=user)
        except CustomerModel.DoesNotExist:
            return Response({"error": "Customer profile not found."}, status=status.HTTP_400_BAD_REQUEST)

        orders = OrderModel.objects.filter(customer=customer).order_by("-id")
        if not orders.exists():
            return Response({"message": "No orders found."}, status=status.HTTP_404_NOT_FOUND)

        # Apply pagination (if needed)
        pagination_class = OrderPagination
        paginator = pagination_class()
        result_page = paginator.paginate_queryset(orders, request)
        return paginator.get_paginated_response(OrderSerializer(result_page, many=True).data)