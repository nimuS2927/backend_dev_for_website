from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
import json

from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin

from .models import Profile
from .serializers import ProfileSerializer


class SignInAPIView(APIView):
    """
    Class SignInAPIView is used for user authentication
    """
    def post(self, request: Request) -> Response:
        for key, value in request.data.items():
            data = json.loads(key)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(status=200)
        else:
            return Response(status=500)


class SignUpAPIView(APIView):
    """
    Class SignUpAPIView is used for user registration, also creates a user profile
    """
    def post(self, request: Request) -> Response:
        for key, value in request.data.items():
            data = json.loads(key)
        try:
            name = data.get('name')
            username = data.get('username')
            password = data.get('password')
            user = User.objects.get_or_create(
                first_name=name,
                username=username,
                password=password
            )
            profile = Profile.objects.get_or_create(user=user)
            return Response(status=200)
        except Exception:
            return Response(status=500)


class SignOutAPIView(APIView):
    """
    Class SignOutAPIView is used to log out the user
    """
    def post(self, request: Request) -> Response:
        logout(request)
        return Response(status=200)


class ProfileDetailAPIView(APIView):
    """
    Class ProfileDetailAPIView is used for viewing and modifying a user's profile
    """
    def get(self, request: Request) -> Response:
        """
        A function that processes a GET request to view the user's profile
        """
        cur_user = request._user
        profile = Profile.objects.select_related('user').get(user=cur_user)
        # serialized = ProfileSerializer(profile)
        data = {
            "fullName": cur_user.get_full_name(),
            "email": cur_user.email,
            "phone": (profile.phone if profile.phone else None),
            "avatar": {
                "src": (profile.avatar_src.url if profile.avatar_src else None),
                "alt": (profile.avatar_alt if profile.avatar_alt else None),
            }
        }
        return Response(data)

    def post(self, request: Request) -> Response:
        """
        A function that processes a POST request to modifying the user's profile
        """
        data = request._data
        cur_user = request._user
        profile = Profile.objects.select_related('user').get(user=cur_user)
        # serialized = ProfileSerializer(profile)
        full_name = data.get('fullName')
        email = data.get('email')
        phone = data.get('phone')
        src = data.get('avatar').get('src')
        alt = data.get('avatar').get('alt')
        if full_name:
            first_name, last_name = full_name.split(' ', 1)
            cur_user.first_name = first_name
            cur_user.last_name = last_name
            cur_user.save()
        if email:
            profile.email = email
        if phone:
            profile.phone = phone
        if src:
            profile.avatar_src = src
        if alt:
            profile.avatar_alt = alt
        profile.save()
        data = {
            "fullName": cur_user.get_full_name(),
            "email": cur_user.email,
            "phone": (profile.phone if profile.phone else None),
            "avatar": {
                "src": (profile.avatar_src.url if profile.avatar_src else None),
                "alt": (profile.avatar_alt if profile.avatar_alt else None),
            }
        }
        return Response(data)


class ProfilePasswordAPIView(APIView):
    """
    Class ProfilePasswordAPIView is used for changing the password from the user's personal account
    """
    def post(self, request: Request) -> Response or ValidationError:
        data = request._data
        cur_user = request._user
        password_current = data.get('currentPassword')
        password = data.get('newPassword')
        password_reply = data.get('passwordReply')
        if check_password(password_current, cur_user.password):
            if password == password_reply:
                cur_user.password = make_password(password)
                return Response(status=200)
            raise ValidationError('The reply password must match the new password')
        return ValidationError('The current password is incorrect')


class ProfileAvatarAPIView(APIView):
    """
    Class ProfileAvatarAPIView is used for changing the avatar from the user's personal account
    """
    def post(self, request: Request) -> Response:
        new_avatar = request.FILES['avatar']
        cur_user = request._user
        profile = Profile.objects.get(user=cur_user)
        profile.avatar = new_avatar
        profile.avatar_alt = 'Description avatar no yet'
        return Response(status=200)

