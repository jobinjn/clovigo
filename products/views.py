from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView,UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.models import SellerModel
from products.models import ProductModel,ReviewModel,CustomerModel
from products.serializers import ProductSerializer,ReviewSerializer
from rest_framework.exceptions import NotFound
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import ProductModel  # or your actual Product model

class ProductCreate(CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        # Check if user is a seller and is approved
        try:
            seller = user.sellermodel
            if not seller.is_active:
                raise PermissionDenied("Your seller account is not approved by admin.")
        except SellerModel.DoesNotExist:
            raise PermissionDenied("You are not registered as a seller.")

        serializer.save(seller=seller)

class ProductListAPIView(ListAPIView):
    queryset = ProductModel.objects.select_related('seller', 'color_available').order_by('-created_at')
    serializer_class = ProductSerializer


class ProductGetView(ListAPIView):
    serializer_class = ProductSerializer
    lookup_field = "product_category"
    def get_queryset(self):
        product_category= self.kwargs.get("product_category")  
        return ProductModel.objects.filter(product_category=product_category)  

# class ProductGetbyIdView(RetrieveAPIView):
#     serializer_class = ProductSerializer
#     lookup_field = "product_name"
#     def get_queryset(self):
#         product_name= self.kwargs.get("product_name")  
#         print(product_name)
#         return ProductModel.objects.filter(product_name=product_name)

class ProductGetbyNameView(RetrieveAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'product_name'

    def get_object(self):
        product_name = self.kwargs.get('product_name')
        if not product_name:
            raise NotFound("Product name is required.")

        try:
            return ProductModel.objects.get(product_name__iexact=product_name)
        except ProductModel.DoesNotExist:
            raise NotFound(f"No product found with name: {product_name}")
        
class ProductGetIdView(RetrieveAPIView):
    serializer_class = ProductSerializer
    lookup_field = "id"
    def get_queryset(self):
        id= self.kwargs.get("id")  
        print(id)
        return ProductModel.objects.filter(id=id)        
    
class ProductUpdateView(UpdateAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated]  
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.seller.user != request.user:
            return Response({"error": "You can only edit your own products."}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)
    
class PostReviewAPIView(CreateAPIView):
    queryset = ReviewModel.objects.all()
    serializer_class = ReviewSerializer 

    def context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

class ListReviewAPIView(ListAPIView):
    serializer_class = ReviewSerializer
    def get_queryset(self):
        product_id = self.kwargs.get("product_id")  
        return ReviewModel.objects.filter(product_id=product_id)   

class UpdateReviewAPIView(UpdateAPIView):
    queryset = ReviewModel.objects.all()
    serializer_class = ReviewSerializer
    lookup_field ="pk"

    def getobject(self):
        request = self.request
        auth = JWTAuthentication()

        try:
            token = request.headers.get("Authorization").split(" ")[1]
            validated_token = auth.get_validated_token(token)
            user = auth.get_user(validated_token)

            
            customer = CustomerModel.objects.get(user=user)
            review = super().get_object()
            if review.customer != customer:
                raise PermissionDenied("You are not allowed to update this review.")

            return review

        except CustomerModel.DoesNotExist:
            raise PermissionDenied("No customer account found for this user.")
        except Exception:
            raise PermissionDenied("Invalid or expired token.")

# class ProductSearchView(APIView):
#     """
#     GET /api/customer/products/search/?q=...
#     Authenticated customers only.
#     Matches product.id, product_name, or product_category (both CharFields)
#     """
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         q = request.query_params.get('q', '').strip()
#         if not q:
#             return Response({"error": "Query parameter 'q' is required."},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         # Ensure requester is a customer
#         try:
#             CustomerModel.objects.get(user=request.user)
#         except CustomerModel.DoesNotExist:
#             return Response({"error": "Only customers can search products."},
#                             status=status.HTTP_403_FORBIDDEN)
#
#         # Build filter: match by name, category or id (if numeric)
#         filters = Q(product_name__icontains=q) | Q(product_category__icontains=q)
#         if q.isdigit():
#             filters |= Q(id=int(q))
#
#         qs = ProductModel.objects.filter(filters)[:20]
#
#         results = [
#             {
#                 "id": p.id,
#                 "name": p.product_name,
#                 "category": p.product_category,
#                 "price": float(p.price),  # Adjust field name if different
#                 "thumbnail": p.image.url if hasattr(p, 'image') and p.image else None
#             }
#             for p in qs
#         ]
#
#         return Response({"results": results})
class ProductSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response({"error": "Query parameter 'q' is required."},
                             status=status.HTTP_400_BAD_REQUEST)

        try:
            CustomerModel.objects.get(user=request.user)
        except CustomerModel.DoesNotExist:
            return Response({"error": "Only customers can search products."},
                             status=status.HTTP_403_FORBIDDEN)

        filters = Q(product_name__icontains=q) | Q(product_category__icontains=q)
        if q.isdigit():
            filters |= Q(id=int(q))

        qs = ProductModel.objects.filter(filters)[:20]

        results = [
            {
                "id": p.id,
                "name": p.product_name,
                "category": p.product_category,
                "price": float(p.discount_price),
                "thumbnail": p.image_id.url if p.image_id else None
            }
            for p in qs
        ]

        return Response({"results": results})