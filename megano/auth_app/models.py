from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def profile_image_directory_path(instance: 'Profile', filename: str) -> str:
    return 'profile/user_{pk}/avatar/{filename}'.format(
        pk=instance.user.pk,
        filename=filename,
    )


def validate_number(number: str):
    if len(number) == 10:
        try:
            int(number)
        except ValueError:
            raise ValidationError('Number must contain 10 digits')
    else:
        raise ValidationError('Number must contain 10 digits')


class Profile(models.Model):
    """
    The Profile class describes the user profile model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_src = models.ImageField(blank=True, upload_to=profile_image_directory_path)
    avatar_alt = models.CharField(max_length=255, blank=True, default='Description avatar no yet')
    phone = models.CharField(max_length=10, blank=True, validators=[validate_number])

    def __str__(self):
        return self.user.username


