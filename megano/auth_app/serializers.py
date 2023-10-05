from .models import Profile
from rest_framework import serializers


class AvatarSerializer(serializers.ModelSerializer):
    src = serializers.ImageField(source='avatar_src')
    alt = serializers.CharField(source='avatar_alt')

    class Meta:
        model = Profile
        fields = [
            'src',
            'alt',
        ]


class ProfileSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source='user.get_full_name')
    email = serializers.CharField(source='user.email')
    avatar = AvatarSerializer(required=False)

    class Meta:
        model = Profile

        fields = [
            'fullName',
            'email',
            'phone',
            'avatar',
        ]

