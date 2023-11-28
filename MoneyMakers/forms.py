from django import forms
from .models import AccountProfile, UserAccount, CryptoCurrency, CryptoTransaction, AccountActivity
class AccountRegistrationForm(forms.ModelForm):
    secure_password = forms.CharField(widget=forms.PasswordInput(), required=True)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(), label='Confirm New Password', required=True)

    class Meta:
        model = AccountProfile
        fields = ['given_name', 'family_name', 'user_name', 'email_address', 'secure_password']

    def clean(self):
        cleaned_data = super().clean()
        secure_password = cleaned_data.get('secure_password')
        confirm_new_password = cleaned_data.get('secure_password')

        if secure_password and confirm_new_password and secure_password != confirm_new_password:
            self.add_error('confirm_new_password', 'Passwords do not match')
class UserLoginForm(forms.Form):
    email_address = forms.CharField(required=True)
    secure_password = forms.CharField(widget=forms.PasswordInput(), required=True)
class UpdatePasswordForm(forms.Form):
    email_address = forms.CharField(required=True)
    verification_code = forms.IntegerField(
        label='Enter a 6-digit number',
        min_value=100000,
        max_value=999999,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter a 6-digit number'})
    )
    secure_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your new password', 'autocomplete': 'new-password'})
    )
    confirm_new_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
class PasswordResetForm(forms.Form):
    email_address = forms.EmailField(required=True)
def __init__(self, *args, **kwargs):
    super(AccountRegistrationForm, self).__init__(*args, **kwargs)
    self.fields['given_name'].required = True
    self.fields['family_name'].required = True
    self.fields['email_address'].required = True
    self.fields['user_name'].required = True


class FundsAdditionForm(forms.ModelForm):
    class Meta:
        model = AccountActivity
        fields = ['transaction_amount']



class AssetExchangeForm(forms.ModelForm):
    volume = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'id': 'volume_input',
            'step': '1',  # Ensuring only whole number inputs
        })
    )
    EXCHANGE_ACTIONS = (
        ('purchase', 'Purchase'),
        # ('dispose', 'Sell'),
    )

    # New field for specifying exchange action
    action_type = forms.ChoiceField(
        choices=EXCHANGE_ACTIONS,
        widget=forms.RadioSelect,
        initial='purchase',  # Default action set to 'purchase'
    )
    class Meta:
        model = CryptoTransaction
        fields = ['digital_currency', 'volume']
        widgets = {
            'digital_currency': forms.Select(attrs={'id': 'asset_type_selector'}),
        }

    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['digital_currency'].queryset = CryptoCurrency.objects.all()
        self.user_id = user_id
    def clean(self):
        cleaned_data = super().clean()
        digital_currency = cleaned_data.get('digital_currency')
        volume = cleaned_data.get('volume')

        # Check for asset_type and volume validity
        if digital_currency and volume is not None:
            total_price = digital_currency.current_price_cad * volume
            cleaned_data['total_value'] = total_price

        return cleaned_data
class AssetSellForm(forms.ModelForm):
    volume = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'id': 'volume_input',
            'step': '1',  # Ensuring only whole number inputs
        })
    )
    EXCHANGE_ACTIONS = (
        # ('purchase', 'Purchase'),
        ('sell', 'Sell'),
    )
   

   
    # New field for specifying exchange action
    action_type = forms.ChoiceField(
        choices=EXCHANGE_ACTIONS,
        widget=forms.RadioSelect,
        initial='sell',  # Default action set to 'purchase'
    )
    class Meta:
        model = CryptoTransaction
        fields = ['digital_currency', 'volume']
        widgets = {
            'digital_currency': forms.Select(attrs={'id': 'asset_type_selector'}),
        }

    def __init__(self, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_profile = AccountProfile.objects.get(id=user_id)
        user_crypto_holdings = user_profile.digital_assets
        crypto_ids = list(user_crypto_holdings.keys())
        self.fields['digital_currency'].queryset = CryptoCurrency.objects.filter(name__in=crypto_ids)
        # Set initial value for user holdings field
       
        self.user_id = user_id
        
        
    def clean(self):
        cleaned_data = super().clean()
        digital_currency = cleaned_data.get('digital_currency')
        volume = cleaned_data.get('volume')

        # Check for asset_type and volume validity
        if digital_currency and volume is not None:
            total_price = digital_currency.current_price_cad * volume
            cleaned_data['total_value'] = total_price

        return cleaned_data