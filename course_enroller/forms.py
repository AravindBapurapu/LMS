from django import forms
from django.contrib.auth import authenticate
from accounts.models import Accounts, Enrollment
from .models import EnrollerProfile, PaymentMethod, EnrollerReview


class EnrollerRegistrationForm(forms.ModelForm):
    """Form for new enroller registration"""
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = Accounts
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match!")
        
        if Accounts.objects.filter(username=cleaned_data.get('username')).exists():
            raise forms.ValidationError("Username already exists!")
        
        if Accounts.objects.filter(email=cleaned_data.get('email')).exists():
            raise forms.ValidationError("Email already exists!")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'course_enroller'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class EnrollerLoginForm(forms.Form):
    """Form for enroller login"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            try:
                user = Accounts.objects.get(username=username, role='course_enroller')
                if not user.check_password(password):
                    raise forms.ValidationError("Invalid credentials!")
            except Accounts.DoesNotExist:
                raise forms.ValidationError("User not found!")
        
        return cleaned_data


class EnrollerProfileForm(forms.ModelForm):
    """Form to edit enroller profile"""
    class Meta:
        model = EnrollerProfile
        fields = ['phone', 'bio', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about yourself',
                'rows': 4
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }


class PaymentMethodForm(forms.ModelForm):
    """Form to add/edit payment method"""
    class Meta:
        model = PaymentMethod
        fields = ['payment_type', 'card_number', 'card_holder_name', 'expiry_month', 'expiry_year', 'is_default']
        widgets = {
            'payment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Card Number',
                'maxlength': '16'
            }),
            'card_holder_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cardholder Name'
            }),
            'expiry_month': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'MM',
                'min': '1',
                'max': '12'
            }),
            'expiry_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY',
                'min': '2024'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class EnrollmentForm(forms.ModelForm):
    """Form to enroll in a course"""
    class Meta:
        model = Enrollment
        fields = []
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        enrollment = super().save(commit=False)
        enrollment.user = self.user
        enrollment.course = self.course
        enrollment.is_paid = False
        if commit:
            enrollment.save()
        return enrollment


class EnrollerReviewForm(forms.ModelForm):
    """Form to add/edit course review"""
    class Meta:
        model = EnrollerReview
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience with this course',
                'rows': 5
            }),
        }


class CourseSearchForm(forms.Form):
    """Form to search courses"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search courses...'
        })
    )
    price_filter = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Prices'),
            ('0-500', 'Below ₹500'),
            ('500-1000', '₹500 - ₹1000'),
            ('1000-5000', '₹1000 - ₹5000'),
            ('5000+', 'Above ₹5000'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('-created_at', 'Newest'),
            ('price', 'Price: Low to High'),
            ('-price', 'Price: High to Low'),
            ('title', 'Title: A to Z'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
