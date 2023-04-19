from django import forms

class UserForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length=20)