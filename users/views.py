from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from packaging.utils import _
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CustomPasswordChangeSerializer,
    CustomUserSerializer,
    UserRegisterSerializer,
    UserLoginSerializer,
)

User = get_user_model()


class UserRegisterAPIView(generics.CreateAPIView):
    """
    Представление регистрации нового пользователя
    """

    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        serializer.save()


class EmailVerificationView(APIView):
    def get(self, request, token):
        user = get_object_or_404(User, token=token)
        user.is_active = True
        user.token = None
        user.save()

        return Response(
            {"success": {"is_active": user.is_active}},
            status=status.HTTP_200_OK,
        )


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "user": {
                    "username": serializer.validated_data["user"].username,
                    "email": serializer.validated_data["user"].email,
                },
                "refresh": serializer.validated_data["refresh"],
                "access": serializer.validated_data["access"],
            },
            status=status.HTTP_200_OK,
        )


class CustomPasswordChange(APIView):
    """Кастомный класс для изменения пароля пользователя."""

    permission_classes = (IsAuthenticated,)
    serializer_class = CustomPasswordChangeSerializer

    def post(self, request, format=None):
        """Обрабатывает POST-запрос для изменения пароля пользователя."""
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user = request.user

            new_password = serializer.data["new_password"]
            user.set_password(new_password)
            user.save()

            content = {"success": _("Пароль успешно изменен.")}
            return Response(content, status=status.HTTP_200_OK)

        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class UserMe(APIView):
    """Профиль юзера"""

    permission_classes = (IsAuthenticated,)
    serializer_class = CustomUserSerializer

    def get(self, request, format=None):
        return Response(self.serializer_class(request.user).data)
