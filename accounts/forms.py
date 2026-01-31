from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password

from .models import User, Membership
from company.models import Designation


# ------------------ Signup ------------------

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


# ------------------ Login ------------------

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


# ------------------ Employee Invite ------------------

class EmployeeInviteForm(forms.Form):
    email = forms.EmailField()
    designation = forms.ModelChoiceField(
        queryset=Designation.objects.none(),
        empty_label="Select designation"
    )

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        if self.company:
            # ✅ Correct SaaS filter
            self.fields['designation'].queryset = Designation.objects.filter(
                group__company=self.company
            )
        else:
            self.fields['designation'].queryset = Designation.objects.none()

    def clean_email(self):
        email = self.cleaned_data['email']

        if Membership.objects.filter(
            user__email=email,
            company=self.company
        ).exists():
            raise forms.ValidationError(
                "This employee is already added to your company."
            )

        return email


# ------------------ Force Password Change ------------------

class ForcePasswordChangeForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()

        password = cleaned.get('new_password')
        confirm = cleaned.get('confirm_password')

        if password != confirm:
            raise forms.ValidationError("Passwords do not match")

        validate_password(password)
        return cleaned
