from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from account.decorators import employee_required, can_view_all_appeals
from .models import Appeal


@api_view(["GET"])
def hello(request):
    return Response({"message": "Привет из Django!"})


SPECIALIST_LABELS = {
    "plumber": "Сантехник",
    "carpenter": "Плотник",
    "electrician": "Электрик",
    "other": "Другое",
}

STATUS_LABELS = dict(Appeal.STATUS_CHOICES)


def serialize_appeal(appeal):
    return {
        "id": appeal.id,
        "subject": appeal.subject,
        "specialist": appeal.specialist,
        "specialist_label": SPECIALIST_LABELS.get(appeal.specialist, appeal.specialist),
        "message": appeal.message,
        "status": appeal.status,
        "status_label": STATUS_LABELS.get(appeal.status, appeal.status),
        "created_at": appeal.created_at.isoformat(),
        "updated_at": appeal.updated_at.isoformat(),
    }


def send_appeal_email(subject, message):
    senders = [
        sender
        for sender in settings.APPEAL_EMAIL_SENDERS
        if sender["username"] and sender["password"] and sender["from_email"]
    ]

    if not senders:
        raise ValueError("No configured email senders")

    last_error = None
    for sender in senders:
        try:
            connection = get_connection(
                host=sender["host"],
                port=sender["port"],
                username=sender["username"],
                password=sender["password"],
                use_ssl=sender["use_ssl"],
                use_tls=sender["use_tls"],
            )
            email = EmailMessage(
                subject,
                message,
                sender["from_email"],
                settings.APPEAL_RECIPIENT_EMAILS,
                connection=connection,
            )
            email.send(fail_silently=False)
            return
        except Exception as exc:
            last_error = exc

    raise last_error


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_appeal(request):
    subject = str(request.data.get("subject", "")).strip()
    specialist = str(request.data.get("specialist", "")).strip()
    message = str(request.data.get("message", "")).strip()

    errors = {}
    if not subject:
        errors["subject"] = "Укажите тему заявки"
    elif len(subject) > 120:
        errors["subject"] = "Тема не должна быть длиннее 120 символов"

    if specialist not in SPECIALIST_LABELS:
        errors["specialist"] = "Выберите специалиста"

    if not message:
        errors["message"] = "Опишите обращение"
    elif len(message) > 1000:
        errors["message"] = "Обращение не должно быть длиннее 1000 символов"

    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    if not any(
            sender["username"] and sender["password"]
            for sender in settings.APPEAL_EMAIL_SENDERS
    ):
        return Response(
            {"error": "Не настроены данные SMTP-отправителя"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if not settings.APPEAL_RECIPIENT_EMAILS:
        return Response(
            {"error": "Не настроены адреса получателей заявок"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    user = request.user
    profile = getattr(user, "profile", None)

    user_lines = []
    if user:
        user_lines = [
            f"Пользователь: {user.get_full_name() or user.username}",
            f"Логин: {user.username}",
            f"Email: {user.email or '-'}",
        ]
        if profile:
            user_lines.extend(
                [
                    f"Телефон: {profile.phone or '-'}",
                    f"Институт: {profile.university or '-'}",
                    f"Общежитие: {profile.hostel or '-'}",
                    f"Комната: {profile.room_number or '-'}",
                ]
            )
    email_subject = f"Новая заявка Hostel Helper: {subject}"
    email_message = "\n".join(
        [
            "Создана новая заявка.",
            "",
            f"Тема: {subject}",
            f"Специалист: {SPECIALIST_LABELS[specialist]}",
            "",
            "Обращение:",
            message,
            "",
            "Данные пользователя:",
            *user_lines,
        ]
    )

    try:
        send_appeal_email(email_subject, email_message)
    except Exception:
        return Response(
            {"error": "Не удалось отправить заявку на почту"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    appeal = Appeal.objects.create(
        user=user,
        subject=subject,
        specialist=specialist,
        message=message,
    )

    return Response(
        {
            "message": "Заявка отправлена",
            "appeal": serialize_appeal(appeal),
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_appeals(request):
    appeal_type = request.query_params.get("type", "active")
    appeals = Appeal.objects.filter(user=request.user)

    if appeal_type == "history":
        appeals = appeals.filter(status=Appeal.STATUS_COMPLETED)
    else:
        appeals = appeals.exclude(status=Appeal.STATUS_COMPLETED)

    return Response({"appeals": [serialize_appeal(appeal) for appeal in appeals]})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@can_view_all_appeals
def list_all_appeals(request):
    """
    Получение всех обращений (только для сотрудников)
    """
    appeals = Appeal.objects.all().order_by('-created_at')

    appeal_type = request.query_params.get("type", "all")
    if appeal_type == "new":
        appeals = appeals.filter(status=Appeal.STATUS_NEW)
    elif appeal_type == "in_progress":
        appeals = appeals.filter(status=Appeal.STATUS_IN_PROGRESS)
    elif appeal_type == "completed":
        appeals = appeals.filter(status=Appeal.STATUS_COMPLETED)

    return Response({"appeals": [serialize_appeal(appeal) for appeal in appeals]})


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
@employee_required
def update_appeal_status(request, pk):
    """
    Обновление статуса обращения (только для сотрудников)
    """
    try:
        appeal = Appeal.objects.get(pk=pk)
    except Appeal.DoesNotExist:
        return Response({"error": "Обращение не найдено"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("status")
    if not new_status:
        return Response({"error": "Не указан статус"}, status=status.HTTP_400_BAD_REQUEST)

    if new_status not in dict(Appeal.STATUS_CHOICES):
        return Response({"error": "Неверный статус"}, status=status.HTTP_400_BAD_REQUEST)

    appeal.status = new_status
    appeal.save()

    return Response({
        "message": "Статус обновлен",
        "appeal": serialize_appeal(appeal)
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@can_view_all_appeals
def appeal_detail(request, pk):
    """
    Получение детальной информации о заявке (для сотрудников)
    """
    try:
        appeal = Appeal.objects.get(pk=pk)
    except Appeal.DoesNotExist:
        return Response({"error": "Обращение не найдено"}, status=status.HTTP_404_NOT_FOUND)

    user = appeal.user
    profile = getattr(user, 'profile', None)

    # Формируем ФИО с учетом отчества
    middle_name = ""
    has_no_middle_name = False
    if profile:
        middle_name = profile.middle_name if not profile.has_no_middle_name else ""
        has_no_middle_name = profile.has_no_middle_name

    full_name = f"{user.last_name} {user.first_name}"
    if middle_name:
        full_name += f" {middle_name}"
    elif not has_no_middle_name and not middle_name:
        full_name += " (отчество не указано)"

    return Response({
        "appeal": serialize_appeal(appeal),
        "user_info": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "middle_name": middle_name,
            "has_no_middle_name": has_no_middle_name,
            "full_name": full_name,
            "phone": profile.phone if profile else "-",
            "room_number": profile.room_number if profile else "-",
            "hostel": profile.hostel if profile else "-",
            "university": profile.university if profile else "-",
        }
    })