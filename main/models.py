from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
import secrets
from datetime import timedelta
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
import os
from django.db import models

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, first_name, last_name, mobile, **extra_fields):
        if not email:
            raise ValueError('Email must be provided')
        if not password:
            raise ValueError('Password is not provided')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            mobile=mobile,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, first_name, last_name, mobile, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, first_name, last_name, mobile, **extra_fields)

    def create_superuser(self, email, password, first_name, last_name, mobile, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, first_name, last_name, mobile, **extra_fields)

class ParentUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(db_index=True, unique=True, max_length=254)
    first_name = models.CharField(max_length=240)
    last_name = models.CharField(max_length=240)
    mobile = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='profile_images', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)
    confirmation_token = models.CharField(max_length=100, blank=True, null=True)
    token_created_at = models.DateTimeField(blank=True, null=True)
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_token_created_at = models.DateTimeField(blank=True, null=True)

    PASSWORD_RESET_TIMEOUT = 3600

    def send_password_reset_email(self):
        token = secrets.token_urlsafe(16)
        self.password_reset_token = token
        self.password_token_created_at = timezone.now()
        self.save()
        subject = 'Сброс пароля'
        message = f'Для сброса пароля перейдите по ссылке: https://monekindergarten.com/reset-password/{token}/'
        send_mail(subject, message, 'email@monekindergarten.com', [self.email], fail_silently=False)

    def reset_password(self, new_password):
        self.set_password(new_password)
        self.password_reset_token = None
        self.password_token_created_at = None
        self.save()

    @classmethod
    def validate_password_reset_token(cls, token):
        try:
            user = cls.objects.get(password_reset_token=token)
            if user.password_token_created_at + timezone.timedelta(seconds=user.PASSWORD_RESET_TIMEOUT) >= timezone.now():
                return user
            else:
                return None
        except cls.DoesNotExist:
            return None


    def send_confirmation_email(self):
        token = secrets.token_urlsafe(16)
        self.confirmation_token = token
        self.token_created_at = timezone.now()
        self.save()
        subject = 'Подтверждение адреса электронной почты'
        message = f'Для подтверждения адреса электронной почты перейдите по ссылке: https://monekindergarten.com/confirm-email/{token}/'
        send_mail(subject, message, 'email@monekindergarten.com', [self.email], fail_silently=False)



    def resend_confirmation_email(self):
        self.send_confirmation_email()

    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return 'https://st3.depositphotos.com/15648834/17930/v/600/depositphotos_179308454-stock-illustration-unknown-person-silhouette-glasses-profile.jpg'

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'mobile']

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class ChildUser(models.Model):
    first_name = models.CharField(max_length=240)
    last_name = models.CharField(max_length=240)
    birth_date = models.DateField()
    parents = models.ManyToManyField(
        'ParentUser',
        related_name='children',
        blank=False
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.birth_date})'

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    age_range = models.CharField(max_length=50, help_text="Например, 3-4 года")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="teaching_groups",
        limit_choices_to={'is_staff': True}
    )

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        related_name="events",
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.title} - {self.date}"

class Menu(models.Model):
    date = models.DateField(unique=True, verbose_name="Дата")
    breakfast = models.TextField(blank=True, null=True, verbose_name="Завтрак")
    second_breakfast = models.TextField(blank=True, null=True, verbose_name="Второй завтрак")
    lunch = models.TextField(blank=True, null=True, verbose_name="Обед")
    afternoon_snack = models.TextField(blank=True, null=True, verbose_name="Полдник")
    dinner = models.TextField(blank=True, null=True, verbose_name="Ужин")

    class Meta:
        verbose_name = "Меню"
        verbose_name_plural = "Меню"

    def __str__(self):
        return f"Меню на {self.date}"

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        related_name="announcements",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title

class GalleryCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, null=True, verbose_name="Описание категории")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Категория медиа"
        verbose_name_plural = "Категории медиа"

    def __str__(self):
        return self.name

class GalleryMedia(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('image', 'Изображение'),
        ('video', 'Видео'),
    )

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default='image',
        verbose_name="Тип медиа"
    )
    image = models.ImageField(
        upload_to="gallery/images/",
        blank=True,
        null=True,
        verbose_name="Изображение"
    )
    video = models.FileField(
        upload_to="gallery/videos/",
        blank=True,
        null=True,
        verbose_name="Видео"
    )
    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="media",
        verbose_name="Категория"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    def save(self, *args, **kwargs):
        if self.video and self.media_type == 'video':
            ext = os.path.splitext(self.video.name)[1].lower()
            if ext == '.mov':
                base_name = os.path.splitext(self.video.name)[0]
                new_name = f"{base_name}.mp4"
                self.video.name = new_name

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Медиа"
        verbose_name_plural = "Медиа"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.media_type

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.image and not self.video:
            raise ValidationError("Необходимо загрузить изображение или видео.")
        if self.image and self.video:
            raise ValidationError("Можно загрузить только изображение или видео, но не оба.")

class Appointment(models.Model):
    parent_full_name = models.CharField(max_length=100, verbose_name="Имя и Фамилия родителя")
    phone_number = models.CharField(max_length=100, verbose_name="Номер телефона")
    child_full_name = models.CharField(max_length=100, verbose_name='Имя и Фамилия ребенка')
    child_birth_date = models.DateField()
    message = models.TextField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f'{self.parent_full_name} - {self.child_full_name}'