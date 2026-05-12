from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser  # Добавлен JSONParser
from .serializers import RegisterSerializer, UpdateProfileSerializer
from .models import UserProfile
from django.contrib.auth.models import User


@api_view(["POST"])
def register_view(request):
    """
    Регистрация нового пользователя
    """
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
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login_view(request):
    """
    Авторизация пользователя
    """
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(request, username=username, password=password)

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
    """
    Получение информации о текущем пользователе
    """
    if request.user.is_authenticated:
        user = request.user
        profile = getattr(user, "profile", None)

        avatar_url = None
        if profile and profile.avatar and profile.avatar.url:
            avatar_url = request.build_absolute_uri(profile.avatar.url)

        return Response({
            "isAuthenticated": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "middle_name": profile.middle_name if profile else "",
                "has_no_middle_name": profile.has_no_middle_name if profile else False,
                "phone": profile.phone if profile else "",
                "university": profile.university if profile else "",
                "hostel": profile.hostel if profile else "",
                "room_number": profile.room_number if profile else "",
                "avatar": avatar_url,
            }
        })

    return Response({
        "isAuthenticated": False
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
def logout_view(request):
    """
    Выход пользователя из системы
    """
    logout(request)
    return Response({"message": "Вы вышли"})


@api_view(["GET", "PUT", "PATCH"])
@login_required
@parser_classes([JSONParser, MultiPartParser, FormParser])  # Добавлен JSONParser
def profile_view(request):
    """
    Получение и обновление профиля пользователя
    GET - получение профиля
    PUT - полное обновление профиля
    PATCH - частичное обновление профиля (включая загрузку аватара)
    """
    user = request.user
    profile = getattr(user, "profile", None)

    # Если профиля нет, создаем его автоматически
    if not profile:
        profile = UserProfile.objects.create(user=user)

    # GET запрос - возвращаем полную информацию о профиле
    if request.method == "GET":
        avatar_url = None
        if profile.avatar and profile.avatar.url:
            avatar_url = request.build_absolute_uri(profile.avatar.url)

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "middle_name": profile.middle_name,
            "has_no_middle_name": profile.has_no_middle_name,
            "room_number": profile.room_number,
            "phone": profile.phone,
            "university": profile.university,
            "hostel": profile.hostel,
            "avatar": avatar_url,
        })

    # PUT или PATCH запрос - обновляем профиль
    elif request.method in ["PUT", "PATCH"]:
        # Определяем, является ли запрос частичным обновлением
        is_partial = request.method == "PATCH"

        # Функция для конвертации строковых булевых значений
        def parse_bool(value):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ['true', '1', 'yes', 'on', 'True']
            return bool(value)

        # Получаем данные в зависимости от типа контента
        if request.content_type and 'multipart' in request.content_type:
            # Для FormData
            if hasattr(request.data, 'dict'):
                data = request.data.dict()
            else:
                data = dict(request.data)
        else:
            # Для JSON
            data = request.data

        # Конвертируем has_no_middle_name из строки в булево значение
        if 'has_no_middle_name' in data:
            data['has_no_middle_name'] = parse_bool(data['has_no_middle_name'])

        # Обновляем поля пользователя
        if 'first_name' in data or not is_partial:
            user.first_name = data.get('first_name', user.first_name)
        if 'last_name' in data or not is_partial:
            user.last_name = data.get('last_name', user.last_name)
        if 'email' in data or not is_partial:
            user.email = data.get('email', user.email)

        # Обновляем поля профиля
        if 'middle_name' in data or not is_partial:
            profile.middle_name = data.get('middle_name', profile.middle_name)

        if 'has_no_middle_name' in data or not is_partial:
            profile.has_no_middle_name = data.get('has_no_middle_name', profile.has_no_middle_name)

        if 'room_number' in data or not is_partial:
            profile.room_number = data.get('room_number', profile.room_number)

        if 'phone' in data or not is_partial:
            profile.phone = data.get('phone', profile.phone)

        if 'university' in data or not is_partial:
            profile.university = data.get('university', profile.university)

        if 'hostel' in data or not is_partial:
            profile.hostel = data.get('hostel', profile.hostel)

        # Обработка аватара
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        # Валидация данных
        # Проверка наличия отчества
        if not profile.has_no_middle_name and not profile.middle_name.strip():
            return Response({
                "middle_name": "Укажите отчество или отметьте, что оно отсутствует"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Проверка телефона (если указан)
        if profile.phone and not profile.phone.isdigit():
            return Response({
                "phone": "Телефон должен содержать только цифры"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Проверка email на уникальность
        if User.objects.exclude(id=user.id).filter(email=user.email).exists():
            return Response({
                "email": "Пользователь с таким email уже существует"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Сохраняем изменения
        try:
            user.save()
            profile.save()
        except Exception as e:
            return Response({
                "error": f"Ошибка сохранения: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Возвращаем обновленные данные
        avatar_url = None
        if profile.avatar and profile.avatar.url:
            avatar_url = request.build_absolute_uri(profile.avatar.url)

        return Response({
            "message": "Профиль успешно обновлен",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "middle_name": profile.middle_name,
                "has_no_middle_name": profile.has_no_middle_name,
                "room_number": profile.room_number,
                "phone": profile.phone,
                "university": profile.university,
                "hostel": profile.hostel,
                "avatar": avatar_url,
            }
        }, status=status.HTTP_200_OK)