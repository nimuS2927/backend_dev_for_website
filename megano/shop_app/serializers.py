from django.contrib.gis.gdal.raster import source
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

from .models import (
    Product,
    Category,
    ImageCategory,
    ImageProduct,
    Tag,
    Review,
    Specification,
    Order,
    Sale,
)
from rest_framework import serializers, pagination


class ImageCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageCategory
        fields = [
            'src',
            'alt',
        ]


class SubCategoriesSerializer(serializers.ModelSerializer):
    image = ImageCategorySerializer(read_only=True)

    class Meta:
        model = Category

        fields = [
            'id',
            'title',
            'image',
        ]


class CategoriesSerializer(serializers.ModelSerializer):
    image = ImageCategorySerializer(read_only=True)
    subcategories = SubCategoriesSerializer(
        'self.get_children',
        many=True,
        read_only=True,
    )

    class Meta:
        model = Category
        fields = [
            'id',
            'title',
            'image',
            'subcategories',
        ]


class ImageProductSerializer(serializers.ModelSerializer):
    src = serializers.URLField(source='src.url')

    class Meta:
        model = ImageProduct
        fields = [
            'src',
            'alt',
        ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
        ]


class ProductSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(source='count_p')
    price = serializers.DecimalField(source='price_p', max_digits=8, decimal_places=2)
    date = serializers.DateTimeField(source='data_created')
    freeDelivery = serializers.BooleanField(source='free_delivery')
    images = ImageProductSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reviews = serializers.IntegerField(source='reviews.count')

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'price',
            'count',
            'date',
            'title',
            'description',
            'freeDelivery',
            'images',
            'tags',
            'reviews',
            'rating',
        ]


class CatalogPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'

    def get_paginated_response(self, data):
        return Response({
            'items': data,
            'currentPage': self.page.number,
            'lastPage': self.page.paginator.num_pages
        })


class ImageProductSaleSerializer(serializers.ModelSerializer):
    src = serializers.URLField(source='product.images.src.url')
    alt = serializers.CharField(source='product.images.alt')

    class Meta:
        model = Sale
        fields = [
            'src',
            'alt',
        ]


class SaleSerializer(serializers.ModelSerializer):
    id =serializers.IntegerField(source='product.id')
    price = serializers.DecimalField(source='product.price_p', max_digits=8, decimal_places=2)
    salePrice = serializers.DecimalField(source='sale_price', max_digits=8, decimal_places=2)
    dateFrom = serializers.DateTimeField(source='data_from', format='%d.%m')
    dateTo = serializers.DateTimeField(source='data_to', format='%d.%m')
    title = serializers.CharField(source='product.title', max_length=255)
    images = serializers.ListField(source='get_images')

    class Meta:
        model = Sale
        fields = [
            'id',
            'price',
            'salePrice',
            'dateFrom',
            'dateTo',
            'title',
            'images',
        ]


class TagDictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            'name',
        ]


class ReviewsSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source=('user.get_full_name'
                                           if 'user.get_full_name'
                                           else 'user.username')
                                   )
    email = serializers.EmailField(source='user.email')
    date = serializers.DateTimeField(source='date_created', format='%Y-%m-%d %H:%M')

    class Meta:
        model = Review
        fields = [
            'author',
            'email',
            'text',
            'rate',
            'date',
        ]


class SpecificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Specification
        fields = [
            'name',
            'value',
        ]


class ProductIdSerializer(ProductSerializer, serializers.ModelSerializer):
    price = serializers.DecimalField(source='price_p', max_digits=8, decimal_places=2)
    count = serializers.IntegerField(source='count_p')
    tags = TagSerializer(many=True, read_only=True)
    reviews = ReviewsSerializer(many=True, read_only=True)
    specifications = SpecificationSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'price',
            'count',
            'date',
            'title',
            'description',
            'freeDelivery',
            'images',
            'tags',
            'reviews',
            'rating',
            'specifications',
        ]


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source=('user.get_full_name'
                                           if 'user.get_full_name'
                                           else 'user.username')
                                   )
    email = serializers.EmailField(source='user.email')
    date = serializers.DateTimeField(source='date_created', format='%Y-%m-%d %H:%M')

    class Meta:
        model = Review
        fields = [
            'author',
            'email',
            'text',
            'rate',
            'date',
        ]


def validate_payment_number(number: str):
    if len(number) != 16 and not number.isdigit():
        raise ValidationError('Card number must contain 16 digits')


def validate_payment_name(name: str):
    if name.isdigit():
        raise ValidationError('Name must contain letters only')


def validate_payment_month(month: str):
    if len(month) != 2 and not 0 < int(month) < 13:
        raise ValidationError('Month must be between 01 and 12')


def validate_payment_year(year: str):
    if not timezone.now().year - 2000 <= int(year) <= timezone.now().year - 1995:
        raise ValidationError(f'Year must be between {timezone.now().year - 2000} and {timezone.now().year - 1995}')


def validate_payment_code(code: str):
    if len(code) != 3 and not code.isdigit():
        raise ValidationError('Code must contain 3 digits')


class PaymentSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=16, validators=[validate_payment_number])
    name = serializers.CharField(max_length=100, validators=[validate_payment_name])
    month = serializers.CharField(max_length=2, validators=[validate_payment_month])
    year = serializers.CharField(max_length=4, validators=[validate_payment_year])
    code = serializers.CharField(max_length=3, validators=[validate_payment_code])


class ProductInOrderSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(source='options__count_optional',)
    price = serializers.DecimalField(source='options__price_option', max_digits=8, decimal_places=2)
    date = serializers.DateTimeField(source='data_created')
    freeDelivery = serializers.BooleanField(source='free_delivery')
    images = ImageProductSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reviews = serializers.IntegerField(source='reviews.count')

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'price',
            'count',
            'date',
            'title',
            'description',
            'freeDelivery',
            'images',
            'tags',
            'reviews',
            'rating',
        ]


class OrderSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='data_created', format='%Y-%m-%d %H:%M')
    fullName = serializers.CharField(source='user.get_full_name')
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.profile.phone')
    deliveryType = serializers.CharField(source='delivery_type')
    paymentType = serializers.CharField(source='payment_type')
    totalCost = serializers.DecimalField(source='total_cost', max_digits=8, decimal_places=2)
    products = ProductInOrderSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products"
        ]

