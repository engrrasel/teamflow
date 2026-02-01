from django import forms
from .models import Customer
from locations.models import Division, District, Thana, PostOffice


class CustomerForm(forms.ModelForm):
    division = forms.ModelChoiceField(queryset=Division.objects.all())
    district = forms.ModelChoiceField(queryset=District.objects.none())
    thana = forms.ModelChoiceField(queryset=Thana.objects.none())
    post_office = forms.ModelChoiceField(queryset=PostOffice.objects.none())

    class Meta:
        model = Customer
        fields = [
            'name', 'phone',
            'division', 'district', 'thana', 'post_office',
            'business_categories', 'selling_products'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🟢 Edit mode হলে initial অনুযায়ী queryset বসবে
        if self.instance.pk:
            self.fields['district'].queryset = District.objects.filter(
                division=self.instance.division
            )
            self.fields['thana'].queryset = Thana.objects.filter(
                district=self.instance.district
            )
            self.fields['post_office'].queryset = PostOffice.objects.filter(
                thana=self.instance.thana
            )

        # 🟢 POST request হলে dynamic queryset বসবে
        if 'division' in self.data:
            try:
                division_id = int(self.data.get('division'))
                self.fields['district'].queryset = District.objects.filter(
                    division_id=division_id
                )
            except (ValueError, TypeError):
                pass

        if 'district' in self.data:
            try:
                district_id = int(self.data.get('district'))
                self.fields['thana'].queryset = Thana.objects.filter(
                    district_id=district_id
                )
            except (ValueError, TypeError):
                pass

        if 'thana' in self.data:
            try:
                thana_id = int(self.data.get('thana'))
                self.fields['post_office'].queryset = PostOffice.objects.filter(
                    thana_id=thana_id
                )
            except (ValueError, TypeError):
                pass
