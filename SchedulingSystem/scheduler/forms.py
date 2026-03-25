from django import forms
from .models import Course,Vendor,CustomUser,CostSheet,Sale

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'course_description', 'exam', 'duration', 'price', 'is_active']
        widgets = {
            'course_code': forms.TextInput(attrs={'class': 'form-control'}),
            'course_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'exam': forms.TextInput(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'is_active']
        
class CustomPasswordResetForm(forms.Form):
    work_email = forms.EmailField()

    def clean_work_email(self):
        work_email = self.cleaned_data['work_email']
        if not CustomUser.objects.filter(work_email=work_email).exists():
            raise forms.ValidationError("No user found with that work_email address.")
        return work_email



class CostSheetForm(forms.ModelForm):
    class Meta:
        model = CostSheet
        exclude = ['is_approved', 'created_at', 'updated_at']

    def __init__(self, *args, allowed_fields=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically remove fields NOT allowed for this client type
        if allowed_fields is not None:
            for field_name in list(self.fields.keys()):
                if field_name not in allowed_fields:
                    self.fields.pop(field_name)

    def save(self, commit=True):
        instance = super().save(commit=False)

        # CRITICAL BUSINESS RULE
        instance.is_approved = False

        if commit:
            instance.save()
        return instance
    

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        exclude = ['date_of_application', 'status']
        widgets = {
            'proposed_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'proposed_date_alternative': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.DateInput):
                self.fields[field].widget.attrs.update({'class': 'form-control'})