from django import forms
from .models import ParentUser, ChildUser, Appointment
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from datetime import date

class ParentUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Электронная почта", required=True)
    first_name = forms.CharField(label="Имя", max_length=240)
    last_name = forms.CharField(label="Фамилия", max_length=240)
    mobile = forms.CharField(label="Мобильный телефон", max_length=50, required=False)

    class Meta:
        model = ParentUser
        fields = ['email', 'first_name', 'last_name', 'mobile', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if ParentUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Эта электронная почта уже используется.")
        return email

from django.utils import translation

class UserEditForm(forms.ModelForm):
    class Meta:
        model = ParentUser
        fields = ['email', 'first_name', 'last_name', 'mobile', 'address', 'image']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        current_language = translation.get_language() or 'ru'

        if current_language == 'uz':
            self.fields['email'].label = 'Elektron pochta manzili'
            self.fields['first_name'].label = 'Ism'
            self.fields['last_name'].label = 'Familiya'
            self.fields['mobile'].label = 'Telefon raqami'
            self.fields['address'].label = 'Manzil'
            self.fields['image'].label = 'Rasm'

        else:
            self.fields['email'].label = 'Почта'
            self.fields['first_name'].label = 'Имя'
            self.fields['last_name'].label = 'Фамилия'
            self.fields['mobile'].label = 'Номер телефона'
            self.fields['address'].label = 'Адрес'
            self.fields['image'].label = 'Фото профиля'

class ChildUserForm(forms.ModelForm):
    class Meta:
        model = ChildUser
        fields = ['first_name', 'last_name', 'birth_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['birth_date'].widget = forms.SelectDateWidget(years=range(2015, 2024))

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['parent_full_name', 'phone_number', 'child_full_name', 'child_birth_date', 'message']
        widgets = {
            'parent_full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя и фамилию родителя',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите номер телефона',
            }),
            'child_full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя и фамилию ребенка',
            }),
            'child_birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Сообщение',
                'rows': 4,
            }),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise ValidationError("Номер телефона должен содержать только цифры.")
        if len(phone_number) < 9:
            raise ValidationError("Номер телефона должен быть не менее 9 цифр.")
        if len(phone_number) > 12:
            raise ValidationError("Номер телефона должен быть не более 12 цифр.")
        return phone_number

    def clean_child_birth_date(self):
        child_birth_date = self.cleaned_data.get('child_birth_date')

        if child_birth_date > date.today():
            raise ValidationError("Дата рождения ребенка не может быть в будущем.")

        age = date.today().year - child_birth_date.year
        if date.today().month < child_birth_date.month or (
                date.today().month == child_birth_date.month and date.today().day < child_birth_date.day):
            age -= 1

        if age > 6:
            raise ValidationError("Возраст ребенка не должен превышать 6 лет.")

        if age < 0:
            raise ValidationError("Дата рождения не может быть в будущем.")

        return child_birth_date
