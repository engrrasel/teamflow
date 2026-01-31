from django import forms
from .models import Company

class CompanyCreateForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'phone']
