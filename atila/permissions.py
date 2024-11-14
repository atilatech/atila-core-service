from django.contrib.auth.models import User
from rest_framework import permissions

from userprofile.models import UserProfile


class UserPermission(permissions.BasePermission):
    public_actions = ["create", "login"]

    def has_permission(self, request, view):
        print("view.action", view.action)
        if view.action in self.public_actions:
            return True
        else:
            user_profile = UserProfile.get_user_profile_from_request(request)

            return user_profile and user_profile.user.is_staff

    def has_object_permission(self, request, view, obj: User):
        user_profile = UserProfile.get_user_profile_from_request(request)
        return user_profile and (user_profile.user.is_staff or user_profile.user == obj)
