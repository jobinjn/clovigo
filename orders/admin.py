from django.contrib import admin
from orders.models import (OrderModel,
                            LatestDealModel)


admin.site.register(OrderModel)
admin.site.register(LatestDealModel)