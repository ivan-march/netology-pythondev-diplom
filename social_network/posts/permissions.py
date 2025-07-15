from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает редактирование/удаление только владельцу объекта.
    """
    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли пользователь право взаимодействовать с объектом.
        Для безопасных методов (GET, HEAD, OPTIONS) — всегда разрешено.
        Для остальных (POST, PUT, PATCH, DELETE):
        - Доступ разрешён, если пользователь — автор объекта
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
