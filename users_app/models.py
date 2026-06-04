from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db import models

from core.utils import build_avatar_image
from users_app.constants import (
    MAX_ABOUT_LENGTH,
    MAX_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_SURNAME_LENGTH,
)
from users_app.managers import UserManager


class User(AbstractUser):
    username = None 

    email = models.EmailField(
        unique=True,
        verbose_name="Электронная почта",
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name="Имя",
    )
    surname = models.CharField(
        max_length=MAX_SURNAME_LENGTH,
        verbose_name="Фамилия",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        verbose_name="Аватар",
    )
    phone = models.CharField(
        max_length=MAX_PHONE_LENGTH,
        blank=True,
        verbose_name="Телефон",
    )
    github_url = models.URLField(
        blank=True,
        verbose_name="GitHub",
    )
    about = models.TextField(
        max_length=MAX_ABOUT_LENGTH,
        blank=True,
        verbose_name="О себе",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["id"]

    def __str__(self):
        return f"{self.surname} {self.name}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            first_letter = self.name[0] if self.name else "U"
            avatar_bytes = build_avatar_image(first_letter)
            username_part = self.email.split("@")[0]
            self.avatar.save(
                f"user_{username_part}.png",
                content=ContentFile(avatar_bytes),
                save=False,
            )
        super().save(*args, **kwargs)