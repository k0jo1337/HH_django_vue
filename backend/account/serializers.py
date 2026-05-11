from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    middle_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    has_no_middle_name = serializers.BooleanField(required=False, default=False)
    room_number = serializers.CharField(max_length=20)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "middle_name",
            "has_no_middle_name",
            "room_number",
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким логином уже существует")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": "Пароли не совпадают"
            })

        if not data.get("has_no_middle_name") and not data.get("middle_name", "").strip():
            raise serializers.ValidationError({
                "middle_name": "Укажите отчество или отметьте, что оно отсутствует"
            })

        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        middle_name = validated_data.pop("middle_name", "").strip()
        has_no_middle_name = validated_data.pop("has_no_middle_name", False)
        room_number = validated_data.pop("room_number")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        UserProfile.objects.create(
            user=user,
            middle_name="" if has_no_middle_name else middle_name,
            has_no_middle_name=has_no_middle_name,
            room_number=room_number,
        )

        return user
