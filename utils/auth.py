import jwt
from functools import wraps
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Usuario

def jwt_auth_required(view_func):
    @wraps(view_func)
    def wrapped_view(self, request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"detail": "Token no proporcionado"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            usuario = Usuario.objects.get(id=payload["user_id"])
            if not usuario.esta_activo:
                return Response({"detail": "Usuario deshabilitado"}, status=status.HTTP_403_FORBIDDEN)
            request.usuario_actual = usuario  # si querés usarlo en la view
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Token expirado"}, status=status.HTTP_401_UNAUTHORIZED)
        except (jwt.InvalidTokenError, Usuario.DoesNotExist):
            return Response({"detail": "Token inválido"}, status=status.HTTP_401_UNAUTHORIZED)

        return view_func(self, request, *args, **kwargs)
    return wrapped_view
