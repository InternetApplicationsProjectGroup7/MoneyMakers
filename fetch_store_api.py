
import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "InternetAppProject.settings")

# Initialize Django
django.setup()

import requests
from django.db import transaction
# from django.db import transaction
from MoneyMakers.models import CryptoCurrency
def fetch_and_store_crypto_data():
    # API endpoint
    api_url = "https://api.coingecko.com/api/v3/coins/markets?x_cg_demo_api_key=CG-KoDWqDuHCWkxgES3WWTuZtBT&vs_currency=usd&order=market_cap_desc"

    try:
        # Make a GET request to the API
        response = requests.get(api_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            api_data = response.json()  # Assuming the API returns JSON data

            # Clear existing data from the CryptoCurrency model
            CryptoCurrency.objects.all().delete()

            # Iterate through the API data and save it to the model
            with transaction.atomic():  # Use a transaction to ensure data consistency
                for data in api_data:
                    crypto = CryptoCurrency(
                        id=data['id'],
                        symbol=data['symbol'],
                        name=data['name'],
                        image=data['image'],
                        current_price=data['current_price'],
                        current_price_cad=data['current_price'] * 1.39,
                        current_price_eur=data['current_price'] * 0.94,
                        market_cap=data['market_cap'],
                        market_cap_rank=data['market_cap_rank'],
                        fully_diluted_valuation=data['fully_diluted_valuation'],
                        total_volume=data['total_volume'],
                        high_24h=data['high_24h'],
                        low_24h=data['low_24h'],
                        price_change_24h=data['price_change_24h'],
                        price_change_percentage_24h=data['price_change_percentage_24h'],
                        market_cap_change_24h=data['market_cap_change_24h'],
                        market_cap_change_percentage_24h=data['market_cap_change_percentage_24h'],
                        circulating_supply=data['circulating_supply'],
                        total_supply=data['total_supply'],
                        max_supply=data['max_supply'],
                        ath=data['ath'],
                        ath_change_percentage=data['ath_change_percentage'],
                        ath_date=data['ath_date'],
                        atl=data['atl'],
                        atl_change_percentage=data['atl_change_percentage'],
                        atl_date=data['atl_date'],
                        last_updated=data['last_updated']
                    )
                    crypto.save()

            return "Data fetched and stored successfully."
        else:
            return f"Failed to fetch data from the API. Status code: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"An error occurred during the API request: {str(e)}"

result = fetch_and_store_crypto_data()
print(result)
