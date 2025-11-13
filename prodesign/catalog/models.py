from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models

class AdvUser(AbstractUser):
    email = models.EmailField(unique=True, null=False, verbose_name='Email адрес')
    patronymic = models.CharField(max_length=200)
    def __str__(self):
        return self.get_full_name()
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        permissions = (("moderator_access", "Доступ модератора"),)

class Category(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Request(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='designs/', blank=False, null=False, verbose_name='Изначальный дизайн')
    completed_image = models.ImageField(upload_to='completed/', blank=True, null=True, verbose_name='Выполненный дизайн')
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE)
    pub_date = models.DateField('date published', default=timezone.now)
    worker_comment = models.CharField(max_length=200, null=True, blank=True, verbose_name="Комментарий дизайнеров")

    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'