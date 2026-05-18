from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from rest_framework.response import Response
from rest_framework import status


def employee_required(function=None, redirect_field_name=None, login_url=None):
    """
    Декоратор для проверки, является ли пользователь сотрудником
    Возвращает 403 ошибку для REST API
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Необходима авторизация"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if not request.user.groups.filter(name='Сотрудник').exists():
                return Response(
                    {"error": "Доступ запрещен. Требуются права сотрудника."},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(request, *args, **kwargs)

        return wrapped_view

    if function:
        return decorator(function)
    return decorator


def can_view_all_appeals(function=None):
    """
    Декоратор для проверки права просмотра всех обращений
    Возвращает 403 ошибку для REST API
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Необходима авторизация"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            has_permission = (
                    request.user.is_superuser or
                    request.user.has_perm('api.can_view_all_appeals') or
                    request.user.groups.filter(name='Сотрудник').exists()
            )

            if not has_permission:
                return Response(
                    {"error": "У вас нет прав для просмотра всех обращений"},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(request, *args, **kwargs)

        return wrapped_view

    if function:
        return decorator(function)
    return decorator