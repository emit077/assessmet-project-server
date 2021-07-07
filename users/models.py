from django.contrib import auth
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.exceptions import PermissionDenied
from django.db import models

import choice
from Assessment_2112_server import settings

User = settings.AUTH_USER_MODEL


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, mobile, password, **extra_fields):
        if not mobile:
            raise ValueError("Email must be set")
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password, **extra_fields):
        user = self.create_user(
            mobile=mobile,
            password=password,
            **extra_fields
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    mobile = models.CharField(unique=True, max_length=10)
    email = models.EmailField(blank=True, verbose_name='email', null=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    is_otp_verified = models.BooleanField(default=False)
    otp_token = models.CharField(max_length=16, blank=True)
    is_account_active = models.BooleanField(default=False)
    account_type = models.CharField(max_length=20, verbose_name='Account Type',
                                    choices=choice.ACCOUNT_TYPE_CHOICES, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.mobile)

    def has_perm(self, perm, obj=None):
        for backend in auth.get_backends():
            if not hasattr(backend, 'has_perm'):
                continue
            try:
                if backend.has_perm(self, perm, obj):
                    return True
            except PermissionDenied:
                return False
        return False

    def has_module_perms(self, app_label):
        return True

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class UserData(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='profile_user', null=True, blank=True)
    name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=250, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=choice.GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    # auto managing
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "#%s-%s" % (self.id, self.name)
