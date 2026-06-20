from django import forms
from .models import FacultyApplication, FacultyProfile, FacultyContact, CourseMaterial
from accounts.models import Profile

class FacultyApplicationForm(forms.ModelForm):
    class Meta:
        model = FacultyApplication
        fields = [
            'name', 'email', 'phone', 'experience', 
            'qualification', 'expertise', 'bio',
            'document', 'resume', 'online_mode', 'terms_accepted'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'terms_accepted': forms.CheckboxInput(),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number should contain only digits")
        return phone

class FacultyProfileForm(forms.ModelForm):
    class Meta:
        model = FacultyProfile
        fields = ['phone', 'qualification', 'expertise', 'bio', 'experience']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

class FacultyContactForm(forms.ModelForm):
    class Meta:
        model = FacultyContact
        fields = ['email', 'phone', 'alternative_phone', 'office_address', 'available_from', 'available_to']
        widgets = {
            'available_from': forms.TimeInput(attrs={'type': 'time'}),
            'available_to': forms.TimeInput(attrs={'type': 'time'}),
        }

class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['title', 'material_type', 'file', 'link', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        material_type = cleaned_data.get('material_type')
        file = cleaned_data.get('file')
        link = cleaned_data.get('link')
        
        if material_type == 'link' and not link:
            raise forms.ValidationError("Please provide a link for external link material")
        elif material_type != 'link' and not file:
            raise forms.ValidationError("Please upload a file")
        
        return cleaned_data