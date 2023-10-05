from django.urls import path

from .views import (
    SignInAPIView,
    SignUpAPIView,
    SignOutAPIView,
    ProfileDetailAPIView,
    ProfilePasswordAPIView,
    ProfileAvatarAPIView,
)


app_name = 'auth_app'


urlpatterns = [
    path('profile', ProfileDetailAPIView.as_view(), name='profile'),
    path('profile/password', ProfilePasswordAPIView.as_view(), name='change_password'),
    path('profile/avatar', ProfileAvatarAPIView.as_view(), name='change_avatar'),
    path('sign-in', SignInAPIView.as_view(), name='sign_in'),
    path('sign-up', SignUpAPIView.as_view(), name='sign_up'),
    path('sign-out', SignOutAPIView.as_view(), name='sign_out'),
]
