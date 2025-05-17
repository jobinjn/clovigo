from django.contrib import admin
from products.models import (ProductModel,
                            ReviewModel, Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

admin.site.register(Category, CategoryAdmin)

admin.site.register(ProductModel)
admin.site.register(ReviewModel)