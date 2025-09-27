# accounts/views.py
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from accounts.models import Usuario
from accounts.serializers import LoginSerializer
from utils.auth import jwt_auth_required
import uuid

from .models import Permiso, Rol, RolPermiso, Usuario, Residente
from .serializers import PermisoSerializer, RolSerializer, RolPermisoSerializer, UsuarioSerializer, ResidenteSerializer


class RolListCreateAPIView(APIView):
    def get(self, request):
        roles = Rol.objects.all()
        serializer = RolSerializer(roles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RolDetailAPIView(APIView):
    def get(self, request, pk):
        rol = get_object_or_404(Rol, pk=pk)
        serializer = RolSerializer(rol)
        return Response(serializer.data)

    def patch(self, request, pk):
        rol = get_object_or_404(Rol, pk=pk)
        serializer = RolSerializer(rol, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        rol = get_object_or_404(Rol, pk=pk)
        rol.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class PermisoListCreateAPIView(APIView):
    def get(self, request):
        permisos = Permiso.objects.all()
        serializer = PermisoSerializer(permisos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PermisoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PermisoDetailAPIView(APIView):
    def get(self, request, pk):
        permiso = get_object_or_404(Permiso, pk=pk)
        serializer = PermisoSerializer(permiso)
        return Response(serializer.data)

    def patch(self, request, pk):
        permiso = get_object_or_404(Permiso, pk=pk)
        serializer = PermisoSerializer(permiso, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        permiso = get_object_or_404(Permiso, pk=pk)
        permiso.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class RolPermisoListCreateAPIView(APIView):
    def get(self, request):
        items = RolPermiso.objects.all()
        serializer = RolPermisoSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RolPermisoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RolPermisoDetailAPIView(APIView):
    def get(self, request, pk):
        item = get_object_or_404(RolPermiso, pk=pk)
        serializer = RolPermisoSerializer(item)
        return Response(serializer.data)

    def patch(self, request, pk):
        item = get_object_or_404(RolPermiso, pk=pk)
        serializer = RolPermisoSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = get_object_or_404(RolPermiso, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UsuarioDetailAPIView(APIView):
    def get(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)

    def patch(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioToggleActivoAPIView(APIView):
    def patch(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        usuario.esta_activo = not usuario.esta_activo
        usuario.save()
        return Response({
            "id": str(usuario.id),
            "correo": usuario.correo,
            "esta_activo": usuario.esta_activo
        })

import jwt
import datetime
from django.conf import settings

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ci = serializer.validated_data['ci']
        password = serializer.validated_data['password']

        try:
            usuario = Usuario.objects.get(ci=ci)
        except Usuario.DoesNotExist:
            return Response({"detail": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

        if not usuario.esta_activo:
            return Response({"detail": "Usuario deshabilitado"}, status=status.HTTP_403_FORBIDDEN)

        if not check_password(password, usuario.password):
            return Response({"detail": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

        # Creamos el JWT
        payload = {
            "user_id": str(usuario.id),
            "ci": usuario.ci,
            "rol": usuario.rol.nombre,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.JWT_EXP_DELTA_SECONDS)
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')

        return Response({
            "token": token,
            "id": str(usuario.id),
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "correo": usuario.correo,
            "rol": usuario.rol.nombre
        })

class UsuarioListCreateAPIView(APIView):

    @jwt_auth_required
    def get(self, request):
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    @jwt_auth_required
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#implementar @jwt_auth_required cuando el seeder este listo en todo


class ResidenteListCreateAPIView(APIView):
    def get(self, request):
        residentes = Residente.objects.all()
        serializer = ResidenteSerializer(residentes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ResidenteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResidenteDetailAPIView(APIView):
    def get(self, request, pk):
        residente = get_object_or_404(Residente, pk=pk)
        serializer = ResidenteSerializer(residente)
        return Response(serializer.data)

    def patch(self, request, pk):
        residente = get_object_or_404(Residente, pk=pk)
        serializer = ResidenteSerializer(residente, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)