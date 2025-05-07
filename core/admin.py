from django.contrib import admin
from .models import ColorModel

@admin.register(ColorModel)
class ColorModelAdmin(admin.ModelAdmin):
    list_display = ('color', 'slug', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('color', 'slug')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    ordering = ('color',)

    actions = ['deactivate_colors']

    def deactivate_colors(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} color(s) deactivated.")
    deactivate_colors.short_description = "Deactivate selected colors"