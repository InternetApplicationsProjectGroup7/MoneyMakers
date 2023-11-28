from django.contrib import admin
from .models import AccountProfile, CryptoCurrency, UserAccount, CryptoTransaction, AccountActivity

admin.site.register(AccountProfile)
admin.site.register(CryptoCurrency)
admin.site.register(UserAccount)
admin.site.register(CryptoTransaction)
admin.site.register(AccountActivity)
# admin.site.register(News)

# Register your models here.
