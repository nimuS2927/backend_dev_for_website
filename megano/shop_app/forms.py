from django import forms
from .models import Sale, Product
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class MySalesAdminForm(forms.ModelForm):
    def clean_sale_price(self):
        sale_price = self.cleaned_data['sale_price']
        product_id = self.data.get('product')
        product = Product.objects.get(id=product_id)
        if Decimal(sale_price) > product.price_p:
            raise ValidationError('Discount price above standard price')
        return sale_price

    def clean_data_to(self):
        data_from = self.cleaned_data['data_from']
        data_to = self.cleaned_data['data_to']
        if data_from > data_to or data_to < timezone.now():
            raise ValidationError('Incorrect date from or to')
        return data_to

    def clean_status(self):
        status = self.cleaned_data['status']
        product = self.cleaned_data['product']
        if status:
            sales = Sale.objects.filter(product=product)
            for sale in sales:
                if sale.status:
                    if sale.data_to < timezone.now():
                        sale.status = False
                        sale.save()
                    else:
                        raise ValidationError('During this period there is already a valid sale')
        return status





