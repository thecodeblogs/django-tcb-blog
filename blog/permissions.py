from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.author == request.user


class IsUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class InOrganization(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj.organization in user.memberships.all():
            return True
        else:
            return False


class InOrganizationForObjectWithRoom(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if obj.room.organization in user.memberships.all():
            return True
        else:
            return False
