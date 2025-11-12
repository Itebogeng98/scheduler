from django import forms
from .models import Course,Vendor

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'course_description', 'exam', 'duration', 'price', 'is_active']


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'is_active']
