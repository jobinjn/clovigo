from django.contrib import admin
from products.models import (ProductModel,
                            ReviewModel)


admin.site.register(ProductModel)
admin.site.register(ReviewModel)