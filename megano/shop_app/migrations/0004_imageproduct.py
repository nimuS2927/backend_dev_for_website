# Generated by Django 4.2.1 on 2023-06-30 06:56

from django.db import migrations, models
import django.db.models.deletion
import shop_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_app', '0003_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src', models.ImageField(blank=True, null=True, upload_to=shop_app.models.product_image_directory_path)),
                ('alt', models.CharField(blank=True, default='Description image no yet', max_length=255)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='shop_app.product')),
            ],
        ),
    ]
