from django.contrib import admin
from .models import (
    Category,
    ImageCategory,
    Product,
    ImageProduct,
    Tag,
    Review,
    Specification,
    Order,
    Sale,
)
from .forms import MySalesAdminForm


class ProductOrderInline(admin.TabularInline):
    model = Order.products_in_order.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        ProductOrderInline,
    ]
    list_display = (
        "id",
        "city",
        "address",
        "data_created",
        "user",
        "delivery_type",
        "payment_type",
        "status",
    )
    list_display_links = "id", "user"
    ordering = "id",
    search_fields = "user",


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "value",
    )
    list_display_links = "pk", "name"
    ordering = "pk",
    search_fields = "name", "value",


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "product",
        "text",
        "rate",
        "date_created",
    )
    list_display_links = "pk", "user", "product"
    ordering = "user", "-date_created", "product", "pk",
    search_fields = "user", "product", "text", "date_created",


class ProductTagInline(admin.TabularInline):
    model = Tag.products.through


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    list_display_links = "id", "name"
    ordering = "name",
    search_fields = "name",


@admin.register(ImageProduct)
class ImageProductAdmin(admin.ModelAdmin):

    list_display = (
        "pk",
        "src",
        "alt",
        "product",
    )
    list_display_links = "pk", "src"
    ordering = "product", "pk",
    search_fields = "alt", "product",


class TagInline(admin.TabularInline):
    model = Product.tags.through


class SpecificationInline(admin.TabularInline):
    model = Product.specifications.through


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        TagInline,
        SpecificationInline,
    ]
    list_display = (
        "id",
        "title",
        "category",
        "price_p",
        "description",
        "count_p",
        "data_created",
        "free_delivery",
    )
    list_display_links = "id", "title"
    ordering = "title",
    search_fields = "title", "price", "description",


@admin.register(ImageCategory)
class ImageCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "src",
        "alt",
        "category",
    )
    list_display_links = "pk", "src"
    ordering = "category", "pk",
    search_fields = "alt", "category",


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "parent",
    )
    list_display_links = "id", "title"
    ordering = "title", "id",
    search_fields = "title",


# class ProductInline(admin.TabularInline):
#     model = Product


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    form = MySalesAdminForm
    list_display = (
        "id",
        "sale_price",
        "data_from",
        "data_to",
        "product",
        "status",
    )
    list_display_links = "id", "status",
    ordering = "status", "data_from",
    search_fields = "data_from", "data_to",
