from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from .models import CartModel, FavoriteModel
from .serializer import CartSerializer, FavoriteSerializer
from products.models import ProductModel
from accounts.models import CustomerModel

class CartView(APIView):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        user = request.user
        if isinstance(user, AnonymousUser):
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            customer = CustomerModel.objects.get(user=user)
        except CustomerModel.DoesNotExist:
            return Response({"error": "Customer profile not found."}, status=status.HTTP_400_BAD_REQUEST)

        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity'))

        if not product_id or not quantity:
            return Response({"error": "Product ID and quantity are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = ProductModel.objects.get(id=product_id)
        except ProductModel.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        if int(quantity) <= 0:
            return Response({"error": "Quantity must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartModel.objects.get_or_create(
            customer=customer,
            product=product,
            defaults={'quantity': quantity, 'unit_price': product.actual_price,'total_price':quantity*product.actual_price}
        )

        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()

        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        user = request.user

        try:
            customer = CustomerModel.objects.get(user=user)
        except CustomerModel.DoesNotExist:
            return Response({"error": "Customer profile not found."}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = CartModel.objects.filter(customer=customer)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartRemoveView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, cart_id):
        user = request.user

        try:
            customer = CustomerModel.objects.get(user=user)
        except CustomerModel.DoesNotExist:
            return Response({"error": "Customer profile not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartModel.objects.get(id=cart_id, customer=customer)
        except CartModel.DoesNotExist:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response({"message": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT)

class FavoriteListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        customer_id = self.request.query_params.get('customer_id')
        return FavoriteModel.objects.filter(customer_id=customer_id).select_related('product')

    def perform_create(self, serializer):
        customer = self.request.user.customer  # Assuming a OneToOne link from User → CustomerModel
        serializer.save(customer=customer)

class FavoriteDeleteAPIView(generics.DestroyAPIView):
    queryset = FavoriteModel.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavoriteSerializer