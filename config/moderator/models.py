from django.db import models
from django.contrib.auth.models import AbstractUser




class User(AbstractUser):
    image = models.ImageField(upload_to='images/avatar', null=True, blank=True, verbose_name="Avatar")

    is_manager = models.BooleanField(default=False, verbose_name="Nazoratchilik huquqi")

    def __str__(self):
        if not (self.first_name and self.last_name):
            return self.username
        return f'{self.last_name} {self.first_name}'

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "1. Foydalanuvchilar"