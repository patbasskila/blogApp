from django import forms
from .models import Comments, Subscribe
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = {'content', 'email', 'name', 'website'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['placeholder'] = 'Type your comment...'  # here, we specify the field we want, self.fields['content'], in this case content field
        self.fields['name'].widget.attrs['placeholder'] = 'Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['website'].widget.attrs['placeholder'] = 'Website - Optional'


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscribe
        fields = '__all__'
        labels = {'email':_('')}   # here we assign empty to the 'email' label, so it wont show 'email' on the home page

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Your Email'


class NewUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = {'username', 'email', 'password1', 'password2'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Enter Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter Your Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Your Password'

    def clean_username(self):
        username = self.cleaned_data['username'].lower()   # here we convert the username to lower case, if user type in Upper case
        new = User.objects.filter(username = username)  # here we check if the username already exist in the DB
        if new.count():   # here we count if the username already been used, if it is, it will evaluated to true
            raise forms.ValidationError('User already exist')
        return username
        

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        new = User.objects.filter(email = email)
        if new.count():
            raise forms.ValidationError('Email already exist')
        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        
        if password1 and password2 and password1 != password2:  # we first checking if password1 has value, then if password2 has value, then we check if they match
            raise forms.ValidationError('Password does not match')
        return password2





