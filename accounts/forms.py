from django import forms
from .models import Accounts
from faculty.models import Form_faculty


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Accounts
        fields = ['username', 'role', 'password', "email"]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            # 🔥 CONDITION CHECK
            if user.role == "faculty":
                Form_faculty.objects.create(
                    username=user.username,
                    email=user.email,
                    password=user.password,  # hashed password
                    role=user.role,
                    is_active=user.is_active,
                    is_staff=user.is_staff,
                    is_superuser=user.is_superuser
                )

        return user