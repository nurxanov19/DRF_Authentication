from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
#from django.contrib.auth.base_user import BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):       # Manager modellar uchun qo'shimcha funksiyalar yozishga yordam beradi, masalan default Manager da get, filter, create kabi funksiyalar mavjud bo'ladi
    def create_user(self, phone, password=None, is_active=True, is_staff=False, is_superuser=False, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required")
        user = self.model(phone=phone, password=password, is_active=is_active, is_staff=is_staff, is_superuser=is_superuser)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        return self.create_user(phone=phone, password=password, is_active=True, is_staff=True, is_superuser=True)


class CustomUser(AbstractBaseUser, PermissionsMixin):       #   PermissionsMixin --> has_perm() funsiyasini o'z ichiga oladi; is_superuser, user_permission atributlarni tekshiradi, permissionlar mavjudligini tekshiradi
    phone = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'

    def format(self):       #  serializer o'rnida yozilgan (postman da datani dict ko'rinishida chiqaradi)
        return {
            'phone': self.phone,
            'name': self.name,
            'is_staff': self.is_staff,
            'is_active': self.is_active,
            'is_superuser': self.is_superuser,
        }


class OneTimePasswordModel(models.Model):
    phone = models.CharField(max_length=100)
    key = models.CharField(max_length=200)

    is_expired = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    tried = models.PositiveBigIntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.tried > 3:
            self.is_expired = True
        super(OneTimePasswordModel, self).save(*args, **kwargs)

