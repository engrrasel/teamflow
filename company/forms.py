from django import forms
from .models import Company, Designation, DesignationGroup


# ---------- Company ----------
class CompanyCreateForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'phone']


# ---------- Designation Group ----------
class DesignationGroupForm(forms.ModelForm):
    class Meta:
        model = DesignationGroup
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Group name',
                'style': 'padding:10px; border-radius:8px; width:100%;'
            })
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']

        if DesignationGroup.objects.filter(
            company=self.company,
            name__iexact=name
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This group already exists.")

        return name


# ---------- Designation ----------
class DesignationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        groups = DesignationGroup.objects.filter(
            company=self.company
        )
        self.fields['group'].queryset = groups

        # ✅ শুধু group name দেখাবে (company ছাড়া)
        self.fields['group'].label_from_instance = lambda obj: obj.name

        # 🔽 UI styling
        self.fields['group'].widget.attrs.update({
            'style': 'padding:10px; border-radius:8px;',
        })

        self.fields['name'].widget.attrs.update({
            'placeholder': 'Designation name',
            'style': 'padding:10px; border-radius:8px;',
        })

    def clean_name(self):
        name = self.cleaned_data['name']
        group = self.cleaned_data.get('group')

        if Designation.objects.filter(
            group=group,
            name__iexact=name
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "This designation already exists in this group."
            )

        return name

    class Meta:
        model = Designation
        fields = ['group', 'name']
