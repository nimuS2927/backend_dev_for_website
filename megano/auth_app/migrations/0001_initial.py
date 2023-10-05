# Generated by Django 4.2.1 on 2023-06-09 15:28

import auth_app.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, upload_to=auth_app.models.profile_image_directory_path)),
                ('avatar_alt', models.CharField(blank=True, default='Description avatar no yet', max_length=255)),
                ('phone', models.CharField(max_length=12, validators=[auth_app.models.validate_number])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]