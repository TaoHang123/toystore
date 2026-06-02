from django import forms
from .models import Addresses

class AddressForm(forms.ModelForm):
    class Meta:
        model = Addresses
        fields = ['receiver', 'phone', 'province', 'city', 'district', 'detail', 'is_default']
        widgets = {
            'receiver': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'detail': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }