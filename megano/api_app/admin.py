from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _
from .models import (Image, Category, Subcategory, Product, Sale, Review, Specification, OrderProduct,
                     Order, Basket, Tag, OrderHistory)
from django.contrib import admin

admin.site.site_header = _("Administrative  panel of Megano")
admin.site.site_title = _("Megano panel")
admin.site.index_title = _("Welcome to megano panel")


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("alt", "src",)
    list_filter = ("alt",)
    search_fields = ("alt",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "image",)
    list_filter = ("title", "image",)
    search_fields = ("title", "image",)


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "image",)
    list_filter = ("category", "title", "image",)
    search_fields = ("category", "title", "image",)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("product", "salePrice", "dateFrom", "dateTo", "is_active")
    list_filter = ('product', "dateFrom", "dateTo")
    search_fields = ('product__title', 'dateFrom', 'dateTo')
    ordering = ('dateFrom',)
    actions = ['cancel_the_sale']

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            fieldsets = [
                (_("Information"), {"fields": ("product", "salePrice")}),
                (_("Dates"), {"fields": ("dateFrom", "dateTo")}),
                (_("Additional"), {"fields": ("is_applied", "is_active")}),
            ]
        else:
            fieldsets = [
                (_("Information"),
                 {"fields": ("product", "salePrice")}),
                (_("Dates"),
                 {"fields": ("dateFrom", "dateTo")})
            ]
        return fieldsets

    def cancel_the_sale(self, request, queryset):
        for sale in queryset:
            if sale.is_active:
                product = sale.product
                product.price = sale.oldPrice
                product.save(update_fields=["price"])
            sale.delete()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "count", "sold",)
    list_display_links = ("id", "title")
    list_filter = ("title", )
    search_fields = ("id", "title",)
    ordering = ('date',)
    fieldsets = [
        (_("General"), {"fields": ("title", "price", "category",)}),
        (_("In store"), {"fields": ("count", "sold",)}),
        (_("Details"), {"fields": ("freeDelivery", "is_limited", "description",
                                   "fullDescription", "images", "tags", "specifications",)}),
        (_("User experience"), {"fields": ("rating", "reviews",)}),
        (_("Date"), {"fields": ("date",)}),
    ]

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs['widget'] = FilteredSelectMultiple(db_field.verbose_name, is_stacked=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            self.readonly_fields = ("date",)
        else:
            self.readonly_fields = ("date", "sold", "rating", "reviews")
        return self.readonly_fields


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("author", "rate", "date",)
    list_filter = ("date", "rate")
    search_fields = ("author", "rate", "text", "email")
    ordering = ('date',)

    fieldsets = [
        (_("Author"), {"fields": ("author", "email",)}),
        (_("Review"), {"fields": ("text", "rate",)}),
        (_("Date"), {"fields": ("date", )}),
    ]

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            self.readonly_fields = ("date",)
        else:
            self.readonly_fields = ("author", "email", "text", "rate", "date",)
        return self.readonly_fields


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ("name", "value", )
    list_filter = ("name", "value", )
    search_fields = ("name", "value", )


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "count")
    list_display_links = ("id",)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            self.readonly_fields = ("price", "product", "count")
            return self.readonly_fields
        return ()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "fullName", "status",)
    list_display_links = ("id", "fullName",)
    list_filter = ("createdAt", "paymentType", "status")
    search_fields = ("id", "fullName", "email", "phone", "city", "address")

    fieldsets = [
        (_("User"), {"fields": ("fullName", "email", "phone")}),
        (_("Information"), {"fields": ("deliveryType", "paymentType", "status", "city", "address", "createdAt",)}),
        (_("Content"), {"fields": ("totalCost", "products")}),
    ]

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            self.readonly_fields = ("createdAt",)
        else:
            self.readonly_fields = ("createdAt", "fullName", "email", "phone", "deliveryType",
                                    "paymentType", "status", "city", "address", "totalCost", "products")
        return self.readonly_fields


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "count",)
    list_display_links = ("id", "user",)
    list_filter = ("user", "product",)
    search_fields = ("user", "product",)
    fieldsets = [
        (_("User"), {"fields": ("user",)}),
        (_("Content"), {"fields": ("product", "count")}),
    ]

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            self.readonly_fields = ("user", "product", "count",)
            return self.readonly_fields
        return ()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "order",)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            self.readonly_fields = ("user", "order",)
            return self.readonly_fields
        return ()
