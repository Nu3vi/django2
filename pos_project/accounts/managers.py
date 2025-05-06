from django.contrib.auth.models import BaseUserManager, User
from . import constants as user_constants

class UserManager(BaseUserManager):
    def create_user(self, email, perfil, mobile, password=None, **extra_fields):
        if not perfil:
            raise ValueError('Se requiere el perfil del usuario')

        # Generar contraseña aleatoria si no se proporciona
        if password is None:
            password = User.objects.make_random_password(
                length=8,
                allowed_chars="abcdefghjkmnpqrstuvwxyz0123456789"
            )

        user = self.model(
            email=self.normalize_email(email),
            perfil=perfil,
            mobile=mobile,
            **extra_fields
        )
        user.set_password(password)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, perfil, mobile, password=None, **extra_fields):
        if not perfil:
            raise ValueError('Se requiere el perfil del usuario')

        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('perfil', user_constants.ADMINISTRADOR)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, perfil, mobile, password, **extra_fields)

    def update_user(self, data_user):
        iduser = data_user.get('username')
        usuario = self.filter(pk=iduser).update(
            full_name=data_user.get('full_name'),
            email=self.normalize_email(data_user.get('email')),
            perfil=data_user.get('perfil_id'),
            mobile=data_user.get('mobile')
        )
        return usuario
