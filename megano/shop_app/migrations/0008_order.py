# Generated by Django 4.2.1 on 2023-06-30 06:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import shop_app.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop_app', '0007_specification'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('city', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
                ('data_created', models.DateTimeField(auto_now_add=True)),
                ('delivery_type', models.CharField(max_length=7, validators=[shop_app.models.validate_delivery_type])),
                ('payment_type', models.CharField(max_length=11, validators=[shop_app.models.validate_payment_type])),
                ('status', models.CharField(max_length=8, validators=[shop_app.models.validate_status_type])),
                ('products_in_order', models.ManyToManyField(related_name='orders', to='shop_app.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user', 'id'],
            },
        ),
    ]
