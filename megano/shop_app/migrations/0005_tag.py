# Generated by Django 4.2.1 on 2023-06-30 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop_app', '0004_imageproduct'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('products', models.ManyToManyField(related_name='tags', to='shop_app.product')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
