from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . import models

class StudentUserForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class StudentExtraForm(forms.ModelForm):
    phone_number = forms.CharField(required=True, max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = models.StudentExtra
        fields = ['enrollment', 'branch', 'phone_number']

class AdminSignupForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class BookForm(forms.ModelForm):
    class Meta:
        model = models.Book
        fields = ['name', 'isbn', 'author', 'category']

class IssuedBookForm(forms.Form):
    isbn2 = forms.ModelChoiceField(
        queryset=models.Book.objects.all(), 
        empty_label="Select Book", 
        to_field_name="isbn",
        label='Book (Name & ISBN)'
    )
    enrollment2 = forms.ModelChoiceField(
        queryset=models.StudentExtra.objects.all(), 
        empty_label="Select Student",
        to_field_name='enrollment',
        label='Student (Name & Enrollment)'
    )