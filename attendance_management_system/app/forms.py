from django import forms
from .models import User, Team, Attendance
from django.contrib.auth.forms import UserCreationForm
class UserForm(UserCreationForm):
    # password = forms.CharField(
    #     label='Password',
    #     widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
    #     required=False  # Make this required if you want to enforce password on user creation
    # )
    
    class Meta:
        model = User
        fields = ('email','username','first_name','last_name','password','profile_photo','role', 'phone_number', 'address','joined_at','position', 'designation', 'team')

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     if self.cleaned_data['password']:  # Check if password is provided
    #         user.set_password(self.cleaned_data['password'])  # Hash the password
    #     if commit:
    #         user.save()
    #     return user
   
class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'room_number', 'total_strength']

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['user', 'date', 'status', 'check_in', 'check_out']
class LoginForm(forms.Form):
    email = forms.CharField(label='Email', max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'eg. johnfrans@gmail.com'
    }))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password'
    }))
class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254,widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'eg. johnfrans@gmail.com'
    }))
class SetNewPassword(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'New password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm password'
    }))