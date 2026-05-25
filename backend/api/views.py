from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from account.decorators import employee_required, can_view_all_appeals
from .models import Appeal, Executor
import csv
import codecs
from datetime import datetime


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
        "executor_id": appeal.executor.id if appeal.executor else None,
        "executor_name": appeal.executor.get_full_name() if appeal.executor else "-",
        "created_at": appeal.created_at.isoformat(),
        "updated_at": appeal.updated_at.isoformat(),
        "completed_at": appeal.completed_at.isoformat() if appeal.completed_at else None,
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
    """Получение всех обращений с фильтрацией"""
    appeals = Appeal.objects.all().order_by('-created_at')

    status_filter = request.query_params.get("status", "")
    if status_filter and status_filter in dict(Appeal.STATUS_CHOICES):
        appeals = appeals.filter(status=status_filter)

    specialist_filter = request.query_params.get("specialist", "")
    if specialist_filter and specialist_filter in dict(Appeal.SPECIALIST_CHOICES):
        appeals = appeals.filter(specialist=specialist_filter)

    executor_filter = request.query_params.get("executor", "")
    if executor_filter:
        try:
            appeals = appeals.filter(executor_id=int(executor_filter))
        except ValueError:
            pass

    date_from = request.query_params.get("date_from", "")
    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from)
            appeals = appeals.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass

    date_to = request.query_params.get("date_to", "")
    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to)
            appeals = appeals.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass

    return Response({"appeals": [serialize_appeal(appeal) for appeal in appeals]})


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
@employee_required
def update_appeal_status(request, pk):
    """Обновление статуса обращения"""
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

    if new_status == Appeal.STATUS_COMPLETED and not appeal.completed_at:
        appeal.completed_at = timezone.now()

    appeal.save()

    return Response({
        "message": "Статус обновлен",
        "appeal": serialize_appeal(appeal)
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
@employee_required
def assign_executor(request, pk):
    """Назначение исполнителя на заявку"""
    try:
        appeal = Appeal.objects.get(pk=pk)
    except Appeal.DoesNotExist:
        return Response({"error": "Обращение не найдено"}, status=status.HTTP_404_NOT_FOUND)

    executor_id = request.data.get("executor")
    if not executor_id:
        return Response({"error": "Не указан исполнитель"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        executor = Executor.objects.get(id=executor_id)
        appeal.executor = executor
        appeal.save()
        return Response({
            "message": "Исполнитель назначен",
            "appeal": serialize_appeal(appeal)
        })
    except Executor.DoesNotExist:
        return Response({"error": "Исполнитель не найден"}, status=status.HTTP_404_NOT_FOUND)


# ========== Управление исполнителями ==========

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@can_view_all_appeals
def get_executors(request):
    """Получение списка всех исполнителей"""
    executors = Executor.objects.filter(is_active=True)
    data = [{
        "id": e.id,
        "full_name": e.get_full_name(),
        "first_name": e.first_name,
        "last_name": e.last_name,
        "middle_name": e.middle_name,
        "position": e.position,
        "phone": e.phone,
        "work_phone": e.work_phone,
        "email": e.email,
    } for e in executors]
    return Response({"executors": data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@employee_required
def create_executor(request):
    """Создание нового исполнителя"""
    data = request.data

    errors = {}
    if not data.get("last_name"):
        errors["last_name"] = "Введите фамилию"
    if not data.get("first_name"):
        errors["first_name"] = "Введите имя"

    if errors:
        return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

    executor = Executor.objects.create(
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        middle_name=data.get("middle_name", ""),
        position=data.get("position", ""),
        phone=data.get("phone", ""),
        work_phone=data.get("work_phone", ""),
        email=data.get("email", ""),
    )

    return Response({
        "message": "Исполнитель добавлен",
        "executor": {
            "id": executor.id,
            "full_name": executor.get_full_name(),
            "first_name": executor.first_name,
            "last_name": executor.last_name,
            "middle_name": executor.middle_name,
            "position": executor.position,
            "phone": executor.phone,
            "work_phone": executor.work_phone,
            "email": executor.email,
        }
    }, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@employee_required
def update_executor(request, pk):
    """Обновление данных исполнителя"""
    try:
        executor = Executor.objects.get(pk=pk)
    except Executor.DoesNotExist:
        return Response({"error": "Исполнитель не найден"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    executor.first_name = data.get("first_name", executor.first_name)
    executor.last_name = data.get("last_name", executor.last_name)
    executor.middle_name = data.get("middle_name", executor.middle_name)
    executor.position = data.get("position", executor.position)
    executor.phone = data.get("phone", executor.phone)
    executor.work_phone = data.get("work_phone", executor.work_phone)
    executor.email = data.get("email", executor.email)
    executor.save()

    return Response({
        "message": "Данные исполнителя обновлены",
        "executor": {
            "id": executor.id,
            "full_name": executor.get_full_name(),
            "first_name": executor.first_name,
            "last_name": executor.last_name,
            "middle_name": executor.middle_name,
            "position": executor.position,
            "phone": executor.phone,
            "work_phone": executor.work_phone,
            "email": executor.email,
        }
    })


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
@employee_required
def delete_executor(request, pk):
    """Удаление исполнителя"""
    try:
        executor = Executor.objects.get(pk=pk)
        executor.delete()
        return Response({"message": "Исполнитель удален"}, status=status.HTTP_200_OK)
    except Executor.DoesNotExist:
        return Response({"error": "Исполнитель не найден"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@can_view_all_appeals
def report_by_executor(request):
    """Отчет по исполнителям за выбранный период"""
    date_from = request.query_params.get("date_from", "")
    date_to = request.query_params.get("date_to", "")

    appeals = Appeal.objects.filter(status=Appeal.STATUS_COMPLETED)

    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from)
            appeals = appeals.filter(completed_at__date__gte=date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to)
            appeals = appeals.filter(completed_at__date__lte=date_to_obj)
        except ValueError:
            pass

    report = appeals.values('executor', 'executor__last_name', 'executor__first_name', 'executor__middle_name') \
        .annotate(total=Count('id')) \
        .order_by('-total')

    result = []
    for item in report:
        if item['executor']:
            name = f"{item['executor__last_name']} {item['executor__first_name']}"
            if item['executor__middle_name']:
                name += f" {item['executor__middle_name']}"
            result.append({
                "executor_id": item['executor'],
                "executor_name": name,
                "total_completed": item['total'],
            })

    return Response({
        "period": {
            "date_from": date_from,
            "date_to": date_to,
        },
        "report": result
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@can_view_all_appeals
def export_appeals_csv(request):
    """Экспорт заявок в CSV с правильной кодировкой UTF-8-BOM"""
    appeals = Appeal.objects.all().order_by('-created_at')

    # Применяем фильтры
    status_filter = request.query_params.get("status", "")
    if status_filter and status_filter in dict(Appeal.STATUS_CHOICES):
        appeals = appeals.filter(status=status_filter)

    date_from = request.query_params.get("date_from", "")
    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from)
            appeals = appeals.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass

    date_to = request.query_params.get("date_to", "")
    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to)
            appeals = appeals.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass

    # Создаем ответ с BOM для корректного отображения кириллицы в Excel
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="appeals_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    response.write(codecs.BOM_UTF8)

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Тема', 'Специалист', 'Заявитель', 'Статус', 'Исполнитель',
        'Дата создания', 'Дата выполнения'
    ])

    for appeal in appeals:
        writer.writerow([
            appeal.id,
            appeal.subject,
            SPECIALIST_LABELS.get(appeal.specialist, appeal.specialist),
            appeal.user.get_full_name() or appeal.user.username,
            STATUS_LABELS.get(appeal.status, appeal.status),
            appeal.executor.get_full_name() if appeal.executor else '-',
            appeal.created_at.strftime("%d.%m.%Y %H:%M"),
            appeal.completed_at.strftime("%d.%m.%Y %H:%M") if appeal.completed_at else '-',
        ])

    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@can_view_all_appeals
def appeal_detail(request, pk):
    """Получение детальной информации о заявке"""
    try:
        appeal = Appeal.objects.get(pk=pk)
    except Appeal.DoesNotExist:
        return Response({"error": "Обращение не найдено"}, status=status.HTTP_404_NOT_FOUND)

    user = appeal.user
    profile = getattr(user, 'profile', None)

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