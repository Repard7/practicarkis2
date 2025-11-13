# forms.py
import re
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
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
    personal_data_agreement = forms.BooleanField(
        required=True,
        label='Я согласен на обработку персональных данных',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'Вы должны согласиться на обработку персональных данных'}
    )

    class Meta:
        model = AdvUser
        fields = (
        'last_name', 'first_name', 'patronymic', 'username', 'email', 'password1', 'password2', 'is_moderator',
        'personal_data_agreement')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_last_name(self):

        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[а-яА-ЯёЁ\s\-]+$', last_name):
            raise ValidationError('Фамилия должна содержать только кириллические буквы, пробелы и дефис')
        return last_name

    def clean_first_name(self):

        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[а-яА-ЯёЁ\s\-]+$', first_name):
            raise ValidationError('Имя должно содержать только кириллические буквы, пробелы и дефис')
        return first_name

    def clean_patronymic(self):

        patronymic = self.cleaned_data.get('patronymic')
        if not re.match(r'^[а-яА-ЯёЁ\s\-]+$', patronymic):
            raise ValidationError('Отчество должно содержать только кириллические буквы, пробелы и дефис')
        return patronymic

    def clean_username(self):

        username = self.cleaned_data.get('username')


        if not re.match(r'^[a-zA-Z\-]+$', username):
            raise ValidationError('Логин должен содержать только латинские буквы и дефис')


        if AdvUser.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует')

        return username

    def clean_email(self):
        """Валидация email - валидный формат и уникальность"""
        email = self.cleaned_data.get('email')


        if AdvUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def clean_personal_data_agreement(self):
        agreement = self.cleaned_data.get('personal_data_agreement')
        if not agreement:
            raise ValidationError('Вы должны согласиться на обработку персональных данных')
        return agreement

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