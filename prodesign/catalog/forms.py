
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import os
from catalog.models import AdvUser, Request, Category


class CustomUserCreationForm(UserCreationForm):
    last_name = forms.CharField(
        max_length=200,
        required=True,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=200,
        required=True,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    patronymic = forms.CharField(
        max_length=200,
        required=True,
        label='Отчество',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    is_moderator = forms.BooleanField(
        required=False,
        label='Пользователь - модератор?',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = AdvUser
        fields = (
        'last_name', 'first_name', 'patronymic', 'username', 'email', 'password1', 'password2', 'is_moderator')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if AdvUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email


class RequestCreationForm(forms.ModelForm):
    description = forms.CharField(
        max_length=1000,
        required=True,
        label='Описание заявки',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    title = forms.CharField(
        max_length=200,
        required=True,
        label='Заголовок заявки',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        label='Категории',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    image = forms.ImageField(
        required=True,
        label='Изображение дизайна',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        help_text='Допустимые форматы: JPG, JPEG, PNG, BMP. Максимальный размер: 2MB'
    )

    class Meta:
        model = Request
        fields = ['title', 'description', 'image', 'category']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        self.validate_image_file(image)
        return image

    def validate_image_file(self, file):
        max_size = 2 * 1024 * 1024
        if file.size > max_size:
            raise ValidationError("Размер файла не должен превышать 2MB")

        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in valid_extensions:
            raise ValidationError("Недопустимый формат файла. Разрешены: JPG, JPEG, PNG, BMP")


class RequestEditForm(forms.ModelForm):
    worker_comment = forms.CharField(
        max_length=200,
        required=False,
        label='Комментарий к обновленному дизайну',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    completed_image = forms.ImageField(
        required=False,
        label='Изображение обновленного дизайна',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        help_text='Допустимые форматы: JPG, JPEG, PNG, BMP. Максимальный размер: 2MB'
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        label='Категория',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Request
        fields = ['worker_comment', 'completed_image', 'category']

    def clean_completed_image(self):
        completed_image = self.cleaned_data.get('completed_image')
        if completed_image:
            self.validate_image_file(completed_image)
        return completed_image

    def validate_image_file(self, file):
        max_size = 2 * 1024 * 1024
        if file.size > max_size:
            raise ValidationError("Размер файла не должен превышать 2MB")

        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in valid_extensions:
            raise ValidationError("Недопустимый формат файла. Разрешены: JPG, JPEG, PNG, BMP")


class CategoryCreationForm(forms.ModelForm):
    name = forms.CharField(
        max_length=200,
        required=True,
        label='Название категории',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Category
        fields = ['name']