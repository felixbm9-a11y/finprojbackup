import re

from django import forms
from django.contrib.auth import get_user_model

from core.utils import normalize_phone

User = get_user_model()

GITHUB_DOMAIN = "github.com"
PHONE_PATTERN = re.compile(r"^8\d{10}$")


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Пароль",
    )

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Электронная почта")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]

    def clean_phone(self):
        raw_phone = self.cleaned_data.get("phone", "").strip()
        if not raw_phone:
            return raw_phone

        normalized = normalize_phone(raw_phone)

        if not PHONE_PATTERN.match(normalized):
            raise forms.ValidationError(
                "Номер должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
            )

        duplicates = User.objects.filter(phone=normalized)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("Такой номер телефона уже зарегистрирован")

        return normalized

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if url and GITHUB_DOMAIN not in url:
            raise forms.ValidationError(
                "Ссылка должна указывать на репозиторий github.com"
            )
        return url