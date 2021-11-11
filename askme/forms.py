from django import forms
from .validators import validate_file_extension


class LoginForm(forms.Form):
    login = forms.CharField(label='Логин', max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Логин'}))
    passw = forms.CharField(label='Пароль', max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class RegisterForm(forms.Form):
    login = forms.CharField(label='Логин', max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Логин'}))
    email = forms.CharField(label='Почтовый ящик', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Почтовый ящик'}))
    nick = forms.CharField(label='Ваше имя', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Ваше имя'}))
    passw = forms.CharField(label='Пароль', max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))
    passw_conf = forms.CharField(label='Подтверждение пароля', max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Подтверждение пароля'}))
    avatar = forms.FileField(
        label='Выберите файл',
        help_text='',
        required=False,
        validators=[validate_file_extension]
    )

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class AddQuestionForm(forms.Form):
    title = forms.CharField(label='Название', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Название'}))
    text = forms.CharField(label='Описание', max_length=500, widget=forms.Textarea(attrs={'placeholder': 'Описание'}))
    tags = forms.CharField(label='Теги', max_length=500, widget=forms.TextInput(attrs={'placeholder': 'Теги (через запятую)'}))

    def __init__(self, *args, **kwargs):
        super(AddQuestionForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    

class AddAnswerForm(forms.Form):
    text = forms.CharField(label='Описание', max_length=500, widget=forms.Textarea(attrs={'placeholder': 'Ваш ответ...'}))

    def __init__(self, *args, **kwargs):
        super(AddAnswerForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class SettingsForm(forms.Form):
    login = forms.CharField(label='Логин', max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Логин'}), required=False)
    email = forms.CharField(label='Почтовый ящик', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Почтовый ящик'}), required=False)
    nick = forms.CharField(label='Ваше имя', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Ваше имя'}), required=False)
    avatar = forms.FileField(
        label='Выберите фото профиля',
        help_text='',
        required=False,
        validators=[validate_file_extension]
    )

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'