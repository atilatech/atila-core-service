
from rest_framework import permissions

from userprofile.models import UserProfile


class UserProfilePermission(permissions.BasePermission):
    public_actions = ["create", "login"]

    def has_permission(self, request, view):
        print("view.action", view.action)
        user_profile = UserProfile.get_user_profile_from_request(request)
        if view.action == "retrieve":
            return bool(user_profile)
        else:
            return user_profile and user_profile.user.is_staff

    def has_object_permission(self, request, view, obj: UserProfile):
        user_profile = UserProfile.get_user_profile_from_request(request)
        return user_profile and (user_profile.user.is_staff or user_profile == obj)
