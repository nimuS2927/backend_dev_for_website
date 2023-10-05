from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = "pk", "user", "phone", "avatar_src", "avatar_alt"
    list_display_links = "pk", "user"
    ordering = "pk",
    search_fields = "user",




