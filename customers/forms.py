from django import forms
from .models import Customer, BusinessCategory, SellingProduct
from locations.models import Division, District, Thana, PostOffice


class CustomerForm(forms.ModelForm):
    division = forms.ModelChoiceField(queryset=Division.objects.all())
    district = forms.ModelChoiceField(queryset=District.objects.none(), required=False)
    thana = forms.ModelChoiceField(queryset=Thana.objects.none(), required=False)
    post_office = forms.ModelChoiceField(queryset=PostOffice.objects.none(), required=False)

    business_categories = forms.ModelMultipleChoiceField(
        queryset=BusinessCategory.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    selling_products = forms.ModelMultipleChoiceField(
        queryset=SellingProduct.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Customer
        fields = [
            'name', 'phone',
            'division', 'district', 'thana', 'post_office',
            'business_categories', 'selling_products'
        ]

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')
        super().__init__(*args, **kwargs)

        # ✅ Company isolation (CRITICAL)
        self.fields['business_categories'].queryset = \
            BusinessCategory.objects.filter(company=self.company)

        self.fields['selling_products'].queryset = \
            SellingProduct.objects.filter(company=self.company)

        # ---------- Cascading Address (Edit + Validation safe) ----------

        # District
        if self.data.get('division'):
            self.fields['district'].queryset = District.objects.filter(
                division_id=self.data.get('division')
            )
        elif self.instance.pk and self.instance.division:
            self.fields['district'].queryset = District.objects.filter(
                division=self.instance.division
            )

        # Thana
        if self.data.get('district'):
            self.fields['thana'].queryset = Thana.objects.filter(
                district_id=self.data.get('district')
            )
        elif self.instance.pk and self.instance.district:
            self.fields['thana'].queryset = Thana.objects.filter(
                district=self.instance.district
            )

        # Post Office
        if self.data.get('thana'):
            self.fields['post_office'].queryset = PostOffice.objects.filter(
                thana_id=self.data.get('thana')
            )
        elif self.instance.pk and self.instance.thana:
            self.fields['post_office'].queryset = PostOffice.objects.filter(
                thana=self.instance.thana
            )
