from django import forms

INPUT_CLASS = (
    "w-full rounded-lg border border-gray-300 px-3 py-2 "
    "focus:outline-none focus:ring-2 focus:ring-indigo-500"
)


class CheckoutForm(forms.Form):
    first_name = forms.CharField(
        max_length=80, label="First name", widget=forms.TextInput(attrs={"class": INPUT_CLASS})
    )
    last_name = forms.CharField(
        max_length=80, label="Last name", widget=forms.TextInput(attrs={"class": INPUT_CLASS})
    )
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": INPUT_CLASS})
    )
    phone = forms.CharField(
        max_length=30, required=False, label="Phone",
        widget=forms.TextInput(attrs={"class": INPUT_CLASS}),
    )
    address = forms.CharField(
        max_length=250, label="Address", widget=forms.TextInput(attrs={"class": INPUT_CLASS})
    )
    city = forms.CharField(
        max_length=100, label="City", widget=forms.TextInput(attrs={"class": INPUT_CLASS})
    )
    postal_code = forms.CharField(
        max_length=20, label="Postal code", widget=forms.TextInput(attrs={"class": INPUT_CLASS})
    )
