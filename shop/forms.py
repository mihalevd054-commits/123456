from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

# Форма регистрации
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Переводим метки полей
        self.fields['username'].label = 'Имя пользователя'
        self.fields['email'].label = 'Электронная почта'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'
        
        # Переводим сообщения помощи (подсказки)
        self.fields['username'].help_text = 'Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.'
        self.fields['password1'].help_text = (
            'Ваш пароль не должен быть слишком похож на другую вашу личную информацию.<br>'
            'Пароль должен содержать не менее 8 символов.<br>'
            'Пароль не может быть слишком простым и распространённым.<br>'
            'Пароль не может состоять только из цифр.'
        )
        self.fields['password2'].help_text = 'Введите тот же пароль, что и выше, для подтверждения.'

        # Изменяем сообщения об ошибках
        self.fields['username'].error_messages = {
            'unique': 'Пользователь с таким именем уже существует.',
            'required': 'Обязательное поле.',
        }

# Форма входа
class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password'].label = 'Пароль'