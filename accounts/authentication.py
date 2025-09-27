# accounts/authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings
import jwt

from accounts.models import Usuario

class JWTAuthentication(BaseAuthentication):
    """
    Lee Authorization: Bearer <token>, lo decodifica con tu JWT_SECRET_KEY,
    y pone el Usuario en request.user.
    """
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        token = parts[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token expirado")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Token inválido")

        user_id = payload.get("user_id")
        if not user_id:
            raise exceptions.AuthenticationFailed("Token sin user_id")

        try:
            usuario = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            raise exceptions.AuthenticationFailed("Usuario no encontrado")

        # DRF espera (user, auth); auth puede ser None
        return (usuario, None)
