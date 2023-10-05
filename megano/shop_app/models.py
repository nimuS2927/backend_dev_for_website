from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields import related
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from django.utils import timezone


class Category(MPTTModel):
    class MPTTMeta:
        order_insertion_by = ['title']

    id = models.BigAutoField(auto_created=True, primary_key=True)
    title = models.CharField(max_length=100, blank=False)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='subcategories',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title


def category_image_directory_path(instance: 'ImageCategory', filename: str) -> str:
    return 'category_{pk}/images/{filename}'.format(
        pk=instance.category.id,
        filename=filename,
    )


class ImageCategory(models.Model):
    src = models.ImageField(null=True, blank=True, upload_to=category_image_directory_path)
    alt = models.CharField(max_length=255, blank=True, default='Description image no yet')
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name='image')

    def __str__(self):
        return str(self.src)


class Product(models.Model):
    class Meta:
        ordering = ['title']

    id = models.BigAutoField(auto_created=True, primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price_p = models.DecimalField(blank=True, max_digits=8, decimal_places=2)
    count_p = models.PositiveSmallIntegerField(blank=True, default=1)
    data_created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    free_delivery = models.BooleanField(default=False)
    rating = models.FloatField(null=True)
    available = models.BooleanField(default=True)
    quantity_sold = models.SmallIntegerField(default=0)

    def __str__(self):
        return f'{self.title} - {self.price_p}'

    def get_short_description(self):
        if len(str(self.description)) > 50:
            return str(self.description)[:50] + '...'
        else:
            return self.description

    def get_rating(self):
        reviews = Review.objects.filter(product=self)
        if reviews:
            total_sum_rate = sum(review.rate for review in reviews)
            total_count_rate = len(reviews)
            self.rating = round(total_sum_rate/total_count_rate, 1)
            self.save()
            return self.rating
        return None

    def get_available(self):
        self.available = True if self.count_p != 0 else False
        self.save()
        return self.available

    def get_tags_dict(self):
        return [name for name in self.tags.name]

    def get_images(self):
        # product = Product.objects.get(product=self.product)
        return [
            {'src': image.src.url,
             'alt': image.alt, }
            for image in self.images.all()
        ]


def product_image_directory_path(instance: 'ImageProduct', filename: str) -> str:
    return 'product_{pk}/images/{filename}'.format(
        pk=instance.product.id,
        filename=filename,
    )


class ImageProduct(models.Model):
    src = models.ImageField(null=True, blank=True, upload_to=product_image_directory_path)
    alt = models.CharField(max_length=255, blank=True, default='Description image no yet')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return str(self.src)


class Tag(models.Model):
    class Meta:
        ordering = ['name']

    id = models.BigAutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100)
    products = models.ManyToManyField(Product, related_name='tags')

    def __str__(self):
        return self.name


def validate_rate(rate: float):
    if rate > 10:
        raise ValidationError('Rate must be between 0 and 10')


class Review(models.Model):
    class Meta:
        ordering = ['product', '-date_created']

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    text = models.TextField()
    rate = models.SmallIntegerField(validators=[validate_rate])
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.title} - {self.user.username}'

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save()
        product = Product.objects\
            .prefetch_related('reviews')\
            .get(pk=self.product.id)
        product.get_rating()


class Specification(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    products = models.ManyToManyField(Product, related_name='specifications')

    def __str__(self):
        return self.name


def validate_delivery_type(string: str):
    if string.isdigit():
        raise ValidationError('Delivery type must contains only letters')
    # if string.lower != 'free' or 'paid':
    #     raise ValidationError('Delivery type can be "free", "paid" or "express"')


def validate_payment_type(string: str):
    if string.isdigit():
        raise ValidationError('Payment type must contains only letters')
    # if string.lower != 'cash' or 'cashless' or 'prepayment' or 'credit' or 'installment':
    #     raise ValidationError('Payment type can be "cash", "cashless", "prepayment", "credit" or "installment"')


def validate_status_type(string: str):
    if string.isdigit():
        raise ValidationError('Status type must contains only letters')
    # if string.lower != 'accepted' or 'canceled' or 'paid':
    #     raise ValidationError('Status type can be "accepted", "canceled" or "paid"')


class Order(models.Model):
    class Meta:
        ordering = ['user', 'id']

    id = models.BigAutoField(auto_created=True, primary_key=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    data_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    delivery_type = models.CharField(max_length=7, validators=[validate_delivery_type])
    payment_type = models.CharField(max_length=11, validators=[validate_payment_type])
    status = models.CharField(max_length=8, validators=[validate_status_type])
    products_in_order = models.ManyToManyField(Product, related_name='orders')

    def __str__(self):
        return str(self.id)

    def total_cost(self):
        products = Product.objects.filter(orders=self)
        return sum(product.price_p for product in products)

    def confirm_payment(self):
        self.status = 'Paid'
        self.save()
        return self.status


class ProductOptions(models.Model):
    id_product = models.PositiveIntegerField(db_index=True)
    price_option = models.DecimalField(max_digits=8, decimal_places=2)
    count_option = models.PositiveSmallIntegerField(default=1)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='options')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options')


class Sale(models.Model):
    class Meta:
        ordering = ['status', '-data_to', 'id']

    id = models.BigAutoField(auto_created=True, primary_key=True)
    sale_price = models.DecimalField(blank=True, max_digits=8, decimal_places=2)
    data_from = models.DateTimeField()
    data_to = models.DateTimeField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    status = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.id}: {self.product.title} from {self.data_from} to {self.data_to}'

    def get_images(self):
        product = Product.objects.get(id=self.product.id)
        return [
            {'src': image.src.url,
             'alt': image.alt, }
            for image in product.images.all()
        ]






