# Generated by Django 4.2.1 on 2023-06-30 06:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop_app', '0009_productoptions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8)),
                ('data_from', models.DateTimeField()),
                ('data_to', models.DateTimeField()),
                ('status', models.BooleanField(default=False)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='shop_app.product')),
            ],
            options={
                'ordering': ['status', '-data_to', 'id'],
            },
        ),
    ]
