from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'middle_name', 'has_no_middle_name', 'room_number',
            'phone', 'university', 'hostel', 'avatar'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    middle_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    has_no_middle_name = serializers.BooleanField(required=False, default=False)
    room_number = serializers.CharField(max_length=20)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=11)
    university = serializers.CharField(required=False, allow_blank=True, max_length=100)
    hostel = serializers.CharField(required=False, allow_blank=True, max_length=20)

    class Meta:
        model = User
        fields = [
            "username", "email", "password", "password_confirm",
            "first_name", "last_name", "middle_name", "has_no_middle_name",
            "room_number", "phone", "university", "hostel"
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким логином уже существует")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def validate_phone(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Телефон должен содержать только цифры")
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
        phone = validated_data.pop("phone", "")
        university = validated_data.pop("university", "")
        hostel = validated_data.pop("hostel", "")

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
            phone=phone,
            university=university,
            hostel=hostel,
        )

        return user


class UpdateProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email', 'middle_name',
            'has_no_middle_name', 'room_number', 'phone',
            'university', 'hostel', 'avatar'
        ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False},
            'middle_name': {'required': False},
            'has_no_middle_name': {'required': False},
            'room_number': {'required': False},
            'phone': {'required': False},
            'university': {'required': False},
            'hostel': {'required': False},
            'avatar': {'required': False},
        }

    def update(self, instance, validated_data):
        # Обновляем поля пользователя
        user = instance.user

        if 'first_name' in validated_data:
            user.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            user.last_name = validated_data['last_name']
        if 'email' in validated_data:
            user.email = validated_data['email']

        user.save()

        # Обновляем поля профиля
        if 'middle_name' in validated_data:
            instance.middle_name = validated_data['middle_name']
        if 'has_no_middle_name' in validated_data:
            instance.has_no_middle_name = validated_data['has_no_middle_name']
        if 'room_number' in validated_data:
            instance.room_number = validated_data['room_number']
        if 'phone' in validated_data:
            instance.phone = validated_data['phone']
        if 'university' in validated_data:
            instance.university = validated_data['university']
        if 'hostel' in validated_data:
            instance.hostel = validated_data['hostel']
        if 'avatar' in validated_data:
            instance.avatar = validated_data['avatar']

        instance.save()
        return instance