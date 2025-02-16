from django import forms


class ContractForm(forms.Form):
    signer_name = forms.CharField(
        max_length=100,
        label="Signer's Full Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter signer's full name"})
    )
    signer_email = forms.EmailField(
        label="Signer's Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Enter signer's email address"})
    )
    cc_name = forms.CharField(
        max_length=100,
        label="CC's Full Name (Optional)",
        required=False,  # Allowing this field to be optional
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter CC's full name (if applicable)"})
    )
    cc_email = forms.EmailField(
        label="CC's Email Address (Optional)",
        required=False,  # Allowing this field to be optional
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Enter CC's email address (if applicable)"})
    )
