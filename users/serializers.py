import secrets

from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from config import settings
from config.settings import EMAIL_HOST_USER

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания пользователя
    """

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "phone_number",
            "avatar",
            "country",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.is_active = False
        user.set_password(password)
        user.token = secrets.token_hex(16)
        user.save()

        host = self.context["request"].get_host()
        url = (
            f"http://{host}/{settings.API_VERSION}email-confirm/{user.token}/"
        )
        send_mail(
            subject="Подтверждение почты",
            message=f"Переход по ссылке для подтверждения почты {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        return user


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()


class UserLoginSerializer(serializers.Serializer):
    """
    Сериализатор входа пользователя
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = User.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Неверные учетные данные")

        if not user.is_active:
            raise serializers.ValidationError(
                "Аккаунт не активирован. Пожалуйста, подтвердите email."
            )

        refresh = RefreshToken.for_user(user)

        data["user"] = user
        data["access"] = str(refresh.access_token)
        data["refresh"] = str(refresh)

        return data


class CustomPasswordChangeSerializer(serializers.Serializer):
    """
    Кастомный сериализатор для изменения пароля пользователя.
    Проверяет старый пароль и устанавливает новый.
    """

    old_password = serializers.CharField(required=True, max_length=128)
    new_password = serializers.CharField(required=True, max_length=128)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not authenticate(username=user.email, password=value):
            raise serializers.ValidationError("Старый пароль неверный.")
        return value


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор представления для модели User."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "email",
            "phone_number",
            "avatar",
            "country",
            "is_staff",
            "is_active",
            "is_superuser",
        ]
        read_only_fields = [
            "id",
            "date_joined",
        ]
