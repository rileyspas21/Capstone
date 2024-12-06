from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CraigslistSearchForm(forms.Form):
    search_item = forms.CharField(label='Search Item', max_length=100)
    max_price = forms.FloatField(label='Max Price')

class AuthForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, label="Remember Me")

