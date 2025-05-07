from django.contrib import admin
from accounts.models import (UserManagementModel,
                             CustomerModel,
                             SellerModel,
                             DeliveryBoyModel,
                             OTPVerifyModel)

@admin.register(SellerModel)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "shop_name", "GST_no")
    actions = ['approve_selected_sellers']

    def approve_selected_sellers(self, request, queryset):
        for seller in queryset:
            seller.is_active = True
            seller.save()
            user = seller.user
            user.role = 'seller'  # Or set appropriate flag
            user.save()
        self.message_user(request, "Selected sellers approved.")
    approve_selected_sellers.short_description = "Approve selected sellers"


admin.site.register(UserManagementModel)
admin.site.register(CustomerModel)
admin.site.register(DeliveryBoyModel)
admin.site.register(OTPVerifyModel)