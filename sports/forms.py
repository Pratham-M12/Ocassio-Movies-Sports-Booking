from django import forms

class BookingForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)