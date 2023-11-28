from django.db import models


class AccountProfile(models.Model):
    user_name = models.CharField(max_length=256, unique=True)
    email_address = models.EmailField(max_length=256, unique=True)
    secure_password = models.CharField(max_length=256, null=True, blank=True)
    given_name = models.CharField(max_length=256, null=True, blank=True)
    family_name = models.CharField(max_length=256, null=True, blank=True)
    # birth_date = models.DateField(null=True, blank=True)
    identification_image = models.ImageField(upload_to='user_id_images/', null=True, blank=True)
    preferences = models.JSONField(default=list, blank=True)
    digital_assets = models.JSONField(default=dict)
#     # avatar = models.ImageField(blank=True, null=True)


    def __str__(self):
        return self.user_name
class CryptoCurrency(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    image = models.URLField()
    current_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_price_cad = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_price_eur = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    market_cap = models.IntegerField()
    market_cap_rank = models.PositiveIntegerField()
    fully_diluted_valuation = models.IntegerField(blank=True, null=True)
    total_volume = models.IntegerField(blank=True, null=True)
    high_24h = models.IntegerField(blank=True, null=True)
    low_24h = models.IntegerField(blank=True, null=True)
    price_change_24h = models.IntegerField(blank=True, null=True)
    price_change_percentage_24h = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    market_cap_change_24h = models.IntegerField(blank=True, null=True)
    market_cap_change_percentage_24h = models.IntegerField(blank=True, null=True)
    circulating_supply = models.IntegerField(blank=True, null=True)
    total_supply = models.IntegerField(blank=True, null=True)
    max_supply = models.IntegerField(blank=True, null=True)
    ath = models.IntegerField(blank=True, null=True)
    ath_change_percentage = models.IntegerField(blank=True, null=True)
    ath_date = models.DateTimeField(blank=True, null=True)
    atl = models.IntegerField(blank=True, null=True)
    atl_change_percentage = models.IntegerField(blank=True, null=True)
    atl_date = models.DateTimeField(blank=True, null=True)
    roi = models.FloatField(null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

class UserAccount(models.Model):
    user = models.OneToOneField('AccountProfile', on_delete=models.CASCADE)
    # Uncomment and use if currency choice is needed
    # currency_type = models.CharField(max_length=3, choices=CURRENCY_OPTIONS)
    account_balance = models.DecimalField(max_digits=12, decimal_places=3, default=0.00)

    def __str__(self):
        return f"Account Balance for {self.user.user_name}"

class AccountActivity(models.Model):
    user = models.ForeignKey('AccountProfile', on_delete=models.CASCADE)
    transaction_amount = models.DecimalField(max_digits=12, decimal_places=3)
    activity_timestamp = models.DateTimeField(auto_now_add=True)
    activity_type = models.CharField(max_length=12)  # Use 'funding', 'buying', etc.

    def __str__(self):
        return f"Activity Record for {self.user.user_name}"

class CryptoTransaction(models.Model):
    ACTION_CHOICES = (
        ('purchase', 'Purchase'),
        ('sell', 'Sell'),
    )
    user = models.ForeignKey(AccountProfile, on_delete=models.CASCADE)
    digital_currency = models.ForeignKey('CryptoCurrency', on_delete=models.CASCADE)
    volume = models.DecimalField(max_digits=12, decimal_places=3)
    total_value = models.DecimalField(max_digits=12, decimal_places=3)
    transaction_time = models.DateTimeField(auto_now_add=True)
    # New field to indicate the nature of the transaction
    action_type = models.CharField(
        max_length=8,
        choices=ACTION_CHOICES,
        default='purchase'
    )

    def __str__(self):
        return f"{self.user.user_name} - {self.action_type.title()} Transaction"
