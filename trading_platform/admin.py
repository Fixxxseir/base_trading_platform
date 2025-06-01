from django.contrib import admin, messages
from django.utils.html import format_html
from .models import Contact, Product, NetworkNode


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("email", "country", "city", "street", "house_number")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "release_date")


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "supplier", "city", "debt", "created_at")
    list_filter = ("contact__country", "contact__city", "level")
    actions = ("clear_debt",)
    readonly_fields = ("created_at", "level")

    fieldsets = (
        (None, {"fields": ("name", "level", "contact", "supplier", "debt")}),
        ("Продукты", {"fields": ("products",)}),
        ("Дополнительно", {"fields": ("created_at", "owner")}),
    )

    def supplier(self, obj):
        if obj.supplier:
            return format_html(
                '<a href="/admin/network/networknode/{}/change/">{}</a>',
                obj.supplier.id,
                obj.supplier.name,
            )
        return "-"

    supplier.short_description = "Поставщик"

    def city(self, obj):
        return obj.contact.city

    city.short_description = "Город"

    @admin.action(description="Обнулить задолженность")
    def clear_debt(self, request, queryset):
        queryset.update(debt=0)
        self.message_user(request, "Задолженность обнулена", messages.SUCCESS)
