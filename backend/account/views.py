from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import RegisterSerializer, UpdateProfileSerializer
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from rest_framework.permissions import AllowAny
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings


def get_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={"room_number": ""},
    )
    return profile


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
        profile = get_user_profile(user)

        avatar_url = None
        if profile.avatar and profile.avatar.url:
            avatar_url = request.build_absolute_uri(profile.avatar.url)

        return Response({
            "isAuthenticated": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "middle_name": profile.middle_name,
                "has_no_middle_name": profile.has_no_middle_name,
                "phone": profile.phone,
                "university": profile.university,
                "hostel": profile.hostel,
                "room_number": profile.room_number,
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
@parser_classes([JSONParser, MultiPartParser, FormParser])
def profile_view(request):
    """
    Получение и обновление профиля пользователя
    """
    user = request.user
    profile = get_user_profile(user)

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

    elif request.method in ["PUT", "PATCH"]:
        is_partial = request.method == "PATCH"

        def parse_bool(value):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ['true', '1', 'yes', 'on', 'True']
            return bool(value)

        if request.content_type and 'multipart' in request.content_type:
            if hasattr(request.data, 'dict'):
                data = request.data.dict()
            else:
                data = dict(request.data)
        else:
            data = request.data

        if 'has_no_middle_name' in data:
            data['has_no_middle_name'] = parse_bool(data['has_no_middle_name'])

        if 'first_name' in data or not is_partial:
            user.first_name = data.get('first_name', user.first_name)
        if 'last_name' in data or not is_partial:
            user.last_name = data.get('last_name', user.last_name)
        if 'email' in data or not is_partial:
            user.email = data.get('email', user.email)

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

        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        if not profile.has_no_middle_name and not profile.middle_name.strip():
            return Response({
                "middle_name": "Укажите отчество или отметьте, что оно отсутствует"
            }, status=status.HTTP_400_BAD_REQUEST)

        if profile.phone and not profile.phone.isdigit():
            return Response({
                "phone": "Телефон должен содержать только цифры"
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.exclude(id=user.id).filter(email=user.email).exists():
            return Response({
                "email": "Пользователь с таким email уже существует"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.save()
            profile.save()
        except Exception as e:
            return Response({
                "error": f"Ошибка сохранения: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

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


@api_view(["POST"])
@login_required
def change_password_view(request):
    """
    Смена пароля пользователя
    """
    form = PasswordChangeForm(user=request.user, data=request.data)

    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return Response({
            "message": "Пароль успешно изменен"
        }, status=status.HTTP_200_OK)

    errors = {}
    for field, error_list in form.errors.items():
        errors[field] = error_list[0]

    return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@login_required
def user_role(request):
    """
    Получение роли пользователя
    """
    is_employee = request.user.groups.filter(name='Сотрудник').exists()
    return Response({
        "is_employee": is_employee,
        "is_superuser": request.user.is_superuser,
        "groups": [group.name for group in request.user.groups.all()]
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request(request):
    """
    Запрос на сброс пароля
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from django.template.loader import render_to_string

    email = request.data.get("email")

    if not email:
        return Response({"error": "Email обязателен"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            "message": "Если пользователь с таким email существует, инструкции по сбросу пароля отправлены"
        }, status=status.HTTP_200_OK)

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

    html_message = render_to_string('account/password_reset_email.html', {
        'user': user,
        'reset_url': reset_url,
        'site_name': 'Hostel Helper',
    })

    gmail_user = settings.GMAIL_EMAIL_HOST_USER
    gmail_password = settings.GMAIL_EMAIL_HOST_PASSWORD

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = email
    msg['Subject'] = 'Сброс пароля на сайте Hostel Helper'
    msg.attach(MIMEText(html_message, 'html'))

    try:
        server = smtplib.SMTP(settings.GMAIL_EMAIL_HOST, settings.GMAIL_EMAIL_PORT)
        if settings.GMAIL_EMAIL_USE_TLS:
            server.starttls()
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        return Response({"error": f"Ошибка отправки письма: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        "message": "Инструкции по сбросу пароля отправлены на ваш email"
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def password_reset_verify(request, uidb64, token):
    """
    Проверка валидности ссылки сброса пароля
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"valid": False, "error": "Недействительная ссылка"},
                        status=status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, token):
        return Response({"valid": True, "uid": uidb64, "token": token})

    return Response({"valid": False, "error": "Ссылка устарела или недействительна"},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """
    Установка нового пароля
    """
    uidb64 = request.data.get("uid")
    token = request.data.get("token")
    new_password1 = request.data.get("new_password1")
    new_password2 = request.data.get("new_password2")

    if new_password1 != new_password2:
        return Response({"error": "Пароли не совпадают"},
                        status=status.HTTP_400_BAD_REQUEST)

    if len(new_password1) < 6:
        return Response({"error": "Пароль должен содержать минимум 6 символов"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"error": "Недействительная ссылка"},
                        status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({"error": "Ссылка устарела или недействительна"},
                        status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password1)
    user.save()

    return Response({
        "message": "Пароль успешно изменен. Теперь вы можете войти с новым паролем."
    }, status=status.HTTP_200_OK)