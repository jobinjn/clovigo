from django.contrib import admin
from cart.models import (CartModel,
                         FavoriteModel)


admin.site.register(CartModel)
admin.site.register(FavoriteModel)