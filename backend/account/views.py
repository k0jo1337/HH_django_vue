from django.contrib.auth import login
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout




@api_view(["POST"])
def register_view(request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():

        user = serializer.save()

        login(request, user)

        return Response({
            "message": "Регистрация успешна",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        }, status=status.HTTP_201_CREATED)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(["POST"])
def login_view(request):

    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is not None:

        login(request, user)

        return Response({
            "message": "Вход выполнен",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        })

    return Response({
        "error": "Неверный логин или пароль"
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def me_view(request):
    if request.user.is_authenticated:
        user = request.user
        profile = getattr(user, "profile", None)

        avatar_url = None
        avatar = getattr(profile, "avatar", None)
        if avatar:
            avatar_url = request.build_absolute_uri(avatar.url)

        middle_name = getattr(profile, "middle_name", "")
        room_number = getattr(profile, "room_number", "")

        return Response({
    "isAuthenticated": True,
    "user": {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "middle_name": middle_name,
        "phone": getattr(user, "phone", ""),
        "university": getattr(user, "university", ""),
        "hostel": getattr(user, "hostel", ""),
        "room_number": room_number,
        "avatar": avatar_url,

        "profile_fields": [
            {"label": "Фамилия", "value": user.last_name},
            {"label": "Отчество", "value": middle_name},
            {"label": "Институт", "value": getattr(user, "university", "")},
            {"label": "Комната", "value": room_number},
            {"label": "Имя", "value": user.first_name},
            {"label": "Номер телефона", "value": getattr(user, "phone", "")},
            {"label": "Общежитие", "value": getattr(user, "hostel", "")},
            {"label": "E-mail", "value": user.email},
        ]
    }
})

    return Response({
        "isAuthenticated": False
    }, status=401)

@api_view(["POST"])
def logout_view(request):

    logout(request)

    return Response({
        "message": "Вы вышли"
    })
