from django import forms

class CheckoutForm(forms.Form):
    payment_method = forms.ChoiceField(choices=[
        ('cod', 'Cash on Delivery'),
        ('razorpay', 'Razorpay'),
        ('credit_card', 'Credit Card (Stripe)')
    ])

    use_different_shipping = forms.BooleanField(required=False)

    # Alternate Address Fields
    alt_full_name = forms.CharField(required=False)
    alt_phone = forms.CharField(required=False)
    alt_address = forms.CharField(required=False)
    alt_city = forms.CharField(required=False)
    alt_state = forms.CharField(required=False)
    alt_zip_code = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        use_different = cleaned_data.get("use_different_shipping")

        if use_different:
            required_fields = [
                'alt_full_name',
                'alt_phone',
                'alt_address',
                'alt_city',
                'alt_state',
                'alt_zip_code'
            ]
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required.")
