from django import forms

class CraigslistSearchForm(forms.Form):
    search_item = forms.CharField(label='Search Item', max_length=100)
    max_price = forms.FloatField(label='Max Price')
