import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserLoginForm, AccountRegistrationForm,UserProfileForm,AssetSellForm, PasswordResetForm, AssetExchangeForm, FundsAdditionForm,UpdatePasswordForm
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import AccountProfile, CryptoCurrency, UserAccount, CryptoTransaction, AccountActivity
import matplotlib as mpl
import random
mpl.use('Agg')  # Use the 'Agg' backend, which is non-interactive and works well in various environments
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import logout
from django.shortcuts import redirect

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
def index(request):
    user_wishlist = []
    current_user = None
    user_logged_in = False
    # my_var = request.session.get('user_session_id')
    user_id = request.session.get('user_session_id')
    if user_id:
        user_logged_in = True
        current_user = AccountProfile.objects.get(id=user_id)
        user_wishlist = current_user.preferences
    else:
        user_logged_in = False

    top_cryptocurrencies = CryptoCurrency.objects.all().order_by('market_cap_rank')[:20]

    # print(coin_list)
    

    
    context = {
        'user': current_user,
        'coins': top_cryptocurrencies,
        'user_log': user_logged_in,
        'wish_list': user_wishlist
    }
    return render(request, 'FrontEnd/index.html',context)

def login_user(request):
    if request.session.get('user_session_id'):
        return HttpResponseRedirect(reverse('MoneyMakers:index'))

    if request.method == 'POST':
        login_form = UserLoginForm(request.POST)
        if login_form.is_valid():
            user_email = login_form.cleaned_data['email_address']
            user_password = login_form.cleaned_data['secure_password']

            try:
                found_user = AccountProfile.objects.get(email_address=user_email)
                print("User password details:", found_user.secure_password)

                if found_user and found_user.secure_password:
                    if check_password(user_password, found_user.secure_password):
                        request.session['user_session_id'] = found_user.id
                        return HttpResponseRedirect(reverse('MoneyMakers:index'))
                    else:
                        messages.error(request, "The userid or password do not match.")
                        empty_form = UserLoginForm()
                        context ={'form': empty_form}
                        return render(request, 'FrontEnd/login.html', context)
                else:
                    messages.error(request, "The userid or password do not match.")
                    empty_form = UserLoginForm()
                    context ={'form': empty_form}
                    return render(request, 'FrontEnd/login.html', context)

            except AccountProfile.DoesNotExist:
                messages.error(request, "Please create an account.")
                empty_form = UserLoginForm()
                context ={'form': empty_form}
                return render(request, 'FrontEnd/login.html', context)

    else:
        empty_form = UserLoginForm()
        context ={'form': empty_form}
        return render(request, 'FrontEnd/login.html', context)

def process_form(request):
    print("inside process form")
    if request.method == 'POST':
        # Get form data from request.POST
        print("all data", request.POST)
        name = request.POST.get('given_name')
        email = request.POST.get('email_address')
        # Redirect to a success page or another appropriate URL
        return redirect('MoneyMakers:index')
    else:
        # Handle GET requests or other HTTP methods if needed
        return render(request, 'FrontEnd/login.html')

def handle_user_input(request):
    print("Entering form handling routine.")
    if request.method == 'POST':
        
        user_name = request.POST.get('given_name', '')
        user_email = request.POST.get('email_address', '')
        print(f"Received data - Name: {user_name}, Email: {user_email}")
        return HttpResponseRedirect(reverse('MoneyMakers:index'))
    else:

        return render(request, 'FrontEnd/login.html')

def user_signup(request):
    if request.session.get('user_session_id'):
        return HttpResponseRedirect(reverse('MoneyMakers:index'))
    if request.method == 'POST':
        form = AccountRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.secure_password = make_password(form.cleaned_data['secure_password'])
            if 'identification_image' in request.FILES:
                user.identification_image = request.FILES['identification_image']
            user.save()
            return redirect('/login/')
    else:
        form = AccountRegistrationForm()
    return render(request, 'FrontEnd/signup.html', {'form': form})



def send_forgotpassword_mail(request):

    # print("user: ",request.session.get('user_session_id'))
    if request.session.get('user_session_id'):
        return HttpResponseRedirect(reverse('MoneyMakers:index'))
    print("forgot pass clicked")

    return HttpResponseRedirect(reverse('MoneyMakers:forgotpassword'))

def forgot_password(request):
    if request.session.get('user_session_id'):
        return HttpResponseRedirect(reverse('MoneyMakers:index'))
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email_address']
            print("email entered is: ",email)
            try:

                email_user = AccountProfile.objects.get(email_address=email)
                if email_user.secure_password is None:
                    form.add_error(None, 'Google Auth Sign In Required')
                else:
                    otp = random.randint(100000, 999999)
                    request.session['otp'] = otp
                    message = "This is the " + str(otp) + "."
                    send_mail(
                        "One-Time Password",
                        message,
                        settings.EMAIL_HOST,
                        [email],
                        fail_silently=False,
                    )
                    return HttpResponseRedirect(reverse('MoneyMakers:changepassword'))
            except AccountProfile.DoesNotExist:
                form.add_error(None, 'Enter correct email id')

    else:
        form = PasswordResetForm()
    return render(request, 'FrontEnd/forgotpassword.html', {"form": form})




def change_password(request):
    if request.method == 'POST':
        form = UpdatePasswordForm(request.POST, request.FILES)
        # print("details: ",request.POST.get('email_address'))

        print("forgot password")
        if form.is_valid():
            email_address = form.cleaned_data['email_address']
            secure_password = form.cleaned_data['secure_password']
            confirm_password = form.cleaned_data['confirm_new_password']
            otp = form.cleaned_data['verification_code']
            try:
                user = AccountProfile.objects.get(email_address=email_address)
                print("user details are:", user.secure_password)

                if user.secure_password is None:
                    form.add_error(None, 'google Auth Sign In Required')
                else:
                    if request.session.get('otp') and otp == request.session.get('otp'):

                        if secure_password == confirm_password:
                            print("pass match")
                            user.secure_password = make_password(secure_password)
                            user.save()
                            # print("new pass: ",user.password)
                            return redirect('/login/')
                        else:
                            print("pass not match")
                            form.add_error(None, 'Password does not match')
                    else:
                        form.add_error(None, 'OTP does not match')
            except AccountProfile.DoesNotExist:
                form.add_error(None, 'User does not exist')


    else:
        form = UpdatePasswordForm()
    return render(request, 'FrontEnd/changepassword.html',{"form":form})






def dynamic_Crypto(request, coin_name):

    coin = get_object_or_404(CryptoCurrency, name=coin_name)
    plt.switch_backend('Agg')
    if coin.current_price < 1:
        coin.current_price = 10 + coin.current_price
    base_value = int(coin.current_price)

    # Generate 12 monthly values that depend on the base value, for example, fluctuate by up to 15%
    monthly_changes = np.random.uniform(-0.15, 0.15, 12)
    monthly_values = base_value * (1 + monthly_changes)

    # Generate a date range of the last 12 months
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, periods=12, freq='MS')  # 'MS' stands for month start frequency

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, monthly_values, color='darkorange', marker='o', linewidth=2)

    # Format the dates on the x-axis
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    plt.xticks(rotation=45)

    # Set y-axis range to ±15% from the base value
    y_min = base_value * (1 - 0.2)
    y_max = base_value * (1 + 0.2)
    ax.set_ylim([y_min, y_max])

   
    ax.get_yaxis().set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    
    percentage_change = .15 * 100
    # Use ax.text() to add annotations to the plot
    ax.text(0.03, 0.97, f'USD${coin.current_price:,.2f}',
            transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.3))

    ax.text(0.03, 0.92, f'↗USD${15:,.2f} ({percentage_change:.2f}%)',
            transform=ax.transAxes, fontsize=12,
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.3))

    # Remaining plot code...

    # Convert plot to PNG image
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)  # Close the figure to free memory
    buf.seek(0)  # Rewind the buffer

    # Encode the image in base64 and close the buffer
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Construct the image src data URI
    image_url = f"data:image/png;base64,{image_base64}"
    context = {
        "coin": coin,
        "data_uri": image_url
    }

    return render(request, 'FrontEnd/dynamicCrypto.html', context)

def handle_user_profile(request):
    # Retrieve the user's session ID
    session_id = request.session.get('user_session_id')
    user = AccountProfile.objects.get(id=session_id)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        # print("---------------    --------------------------------------",form)
        if form.is_valid():
        # Extracting user input from POST request
            current_user = AccountProfile.objects.get(id=session_id)
           
            
            current_user.email_address = form.cleaned_data['email_address']
            print(request.FILES['identification_image'])
            if 'identification_image' in request.FILES:
                current_user.identification_image = request.FILES['identification_image']
            current_user.save()

            # Render the profile template with updated user details
            return render(request, 'FrontEnd/profile.html', {'user': current_user})
        else:
            # Handle the invalid form case
            return HttpResponse("Operation not allowed.")


    else:
        # Fetch user information for a GET request
        current_user = AccountProfile.objects.get(id=session_id)
        user_wishlist = current_user.preferences

        # Render the profile template with user details and wishlist
        return render(request, 'FrontEnd/profile.html', {'user': current_user, 'wish_list': user_wishlist, 'id': "profile-details"})


def update_user_password(request):
    # Retrieve user's session ID
    session_id = request.session.get('user_session_id')
    # Fetch the user object based on session ID
    current_user = AccountProfile.objects.get(id=session_id)

    # Process only if it's a POST request
    if request.method == 'POST':
        input_current_password = request.POST.get('current-password')
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')

        # Verify current password
        if check_password(input_current_password, current_user.secure_password):
            # Check if new password and confirm password match
            if new_password == confirm_password:
                # Update and save the new password
                current_user.secure_password = make_password(new_password)
                current_user.save()
                messages.success(request, "Password updated successfully.")
            else:
                messages.error(request, "The new passwords do not match.")
        else:
            messages.error(request, "The current password entered is incorrect.")

        # Redirect to the user profile page
        return redirect('/userprofile')


def remove_user_account(request):
    if request.method != 'POST':
        return HttpResponse("Operation not allowed.", status=405)
    session_user_id = request.session.get('user_session_id')

    target_user = AccountProfile.objects.get(id=session_user_id)

    target_user.delete()
    request.session.flush()

    # Redirect to the homepage after successful deletion
    return redirect('/')



def process_user_logout(request):
    request.session.flush()
    logout(request)
    return redirect('/')


def display_user_wishlist(request):
    user_session_id = request.session.get('user_session_id')
    if not user_session_id:
        messages.info(request, "Please log in to view your wishlist.")
        return redirect('/login/')
    current_user = AccountProfile.objects.get(id=user_session_id)
    user_wishlist = current_user.preferences
    print("User Wishlist:", user_wishlist)

    return render(request, 'FrontEnd/profile.html', {
        "user": current_user,
        'wish_list': user_wishlist,
        'id': "wishlist"
    })


def include_in_wishlist(request, cryptocurrency_name):
    
    session_user_id = request.session.get('user_session_id')
    if not session_user_id:
        messages.info(request, "Please log in to add items to your wishlist.")
        return redirect('/login/')
    current_user = AccountProfile.objects.get(id=session_user_id)
    selected_crypto = get_object_or_404(CryptoCurrency, name=cryptocurrency_name)
    if cryptocurrency_name not in current_user.preferences:
        current_user.preferences.append(selected_crypto.name)
        current_user.save()
        messages.success(request, f"{cryptocurrency_name} added to your wishlist.")
    else:
        current_user.preferences.remove(selected_crypto.name)
        current_user.save()
        messages.info(request, f"{cryptocurrency_name} is already in your wishlist.")
    print("Wishlist Updated:", current_user)
    return redirect('MoneyMakers:index')



def process_add_money(request):
    # Check user authentication
    session_user_id = request.session.get('user_session_id')
    if not session_user_id:
        messages.info(request, "Please log in to add funds.")
        return redirect('/login/')

    # Retrieve or create a wallet for the user
    user_wallet, _ = UserAccount.objects.get_or_create(user_id=session_user_id)

    # Handle POST request for adding funds
    if request.method == 'POST':
        money_addition_form = FundsAdditionForm(request.POST)
        if money_addition_form.is_valid():
            deposit_amount = money_addition_form.cleaned_data['transaction_amount']

            # Update wallet balance
            user_wallet.account_balance += deposit_amount
            user_wallet.save()

            # Record the transaction
            AccountActivity.objects.create(
                user_id=session_user_id,
                # currency=deposit_currency,
                transaction_amount=deposit_amount,
                activity_type='deposit',
            )
# Inform user of successful addition
            messages.success(request, "Funds added successfully.")
        else:
            # Handle form errors
            messages.error(request, "Error in form submission.")

        # Redirect back to the same page
        return redirect(request.path)
    # Handle non-POST requests and display the form
    else:
        money_addition_form = FundsAdditionForm()

    # Get the current balance to display
    current_balance = user_wallet.account_balance
    return render(request, 'FrontEnd/profile.html', {
        'form': money_addition_form, 
        'balance': current_balance, 
        'id': "process_add_money"
    })

def execute_currency_purchase(request):
    # Authenticate user
    current_user_id = request.session.get('user_session_id')
    if not current_user_id:
        messages.info(request, "Please log in to purchase cryptocurrency.")
        return redirect('/login/')

    # Retrieve or create a wallet for the user
    user_wallet, _ = UserAccount.objects.get_or_create(user_id=current_user_id)

    # Process the purchase if it's a POST request
    if request.method == 'POST':
        purchase_form = AssetExchangeForm(current_user_id, request.POST)

        # Validate the form
        if purchase_form.is_valid():
            chosen_crypto = purchase_form.cleaned_data['digital_currency']
            purchase_quantity = purchase_form.cleaned_data['volume']
            transaction_type = purchase_form.cleaned_data['action_type']
            total_cost = chosen_crypto.current_price_cad * purchase_quantity
            print(transaction_type)
            
            # Check if the user has enough balance
            if user_wallet.account_balance >= total_cost:
                # Deduct the amount from the wallet
                user_wallet.account_balance -= total_cost

                # Record the purchase
                CryptoTransaction.objects.create(
                    user_id=current_user_id,
                    digital_currency=chosen_crypto,
                    action_type=transaction_type,
                    volume=purchase_quantity,
                    total_value=total_cost,
                )

                # Update user's cryptocurrency holdings
                user_profile = AccountProfile.objects.get(id=current_user_id)
                user_crypto_holdings = user_profile.digital_assets

                # Add or update the quantity of purchased cryptocurrency
                user_crypto_holdings[chosen_crypto.name] = user_crypto_holdings.get(chosen_crypto.name, 0) + int(purchase_quantity)

                # Save updates to user profile and wallet
                user_profile.digital_assets = user_crypto_holdings
                user_wallet.save()
                user_profile.save()

    
                messages.success(request, "Funds added successfully.")
            else:
            # Handle form errors
                messages.error(request, "Error in form submission.")
        else:
            # Handle form errors
            messages.error(request, 'Invalid form data')

        # Redirect back to the same page
        return redirect(request.path)

    else:
        # Handle GET request
        purchase_form = AssetExchangeForm(current_user_id)

        # Prepare cryptocurrency choices for the template
        crypto_options = [{'id': crypto.id, 'name': crypto.name, 'price': str(crypto.current_price_cad)} 
                          for crypto in CryptoCurrency.objects.all()]
        crypto_options_json = json.dumps(crypto_options, cls=DjangoJSONEncoder)

        # Render the purchase page
        return render(request, 'FrontEnd/profile.html', {
            'form': purchase_form, 
            'balance': user_wallet.account_balance, 
            'crypto_choices_json': crypto_options_json,
            'type':'buy',
            'id': "purchase-currency"
        })


def execute_currency_sell(request):
    # Authenticate user
    current_user_id = request.session.get('user_session_id')
    if not current_user_id:
        messages.info(request, "Please log in to purchase cryptocurrency.")
        return redirect('/login/')

    # Retrieve or create a wallet for the user
    user_wallet, _ = UserAccount.objects.get_or_create(user_id=current_user_id)

    # Process the purchase if it's a POST request
    if request.method == 'POST':
        purchase_form = AssetSellForm(current_user_id, request.POST)

        # Validate the form
        if purchase_form.is_valid():
            chosen_crypto = purchase_form.cleaned_data['digital_currency']
            purchase_quantity = purchase_form.cleaned_data['volume']
            transaction_type = purchase_form.cleaned_data['action_type']
            total_cost = chosen_crypto.current_price_cad * purchase_quantity

            user_profile = AccountProfile.objects.get(id=current_user_id)
            user_crypto_holdings = user_profile.digital_assets
            print(user_crypto_holdings[chosen_crypto.name])
            # Check if the user has enough balance
            if int(user_crypto_holdings[chosen_crypto.name]) >= int(purchase_quantity):
                # Deduct the amount from the wallet
                user_wallet.account_balance += total_cost
                user_crypto_holdings[chosen_crypto.name] = user_crypto_holdings.get(chosen_crypto.name, 0) - int(purchase_quantity)

                # Record the purchase
                CryptoTransaction.objects.create(
                    user_id=current_user_id,
                    digital_currency=chosen_crypto,
                    action_type=transaction_type,
                    volume=purchase_quantity,
                    total_value=total_cost,
                )
                if int(user_crypto_holdings[chosen_crypto.name]) <=0:
                    del user_crypto_holdings[chosen_crypto.name]
                # Update user's cryptocurrency holdings
               
                # Save updates to user profile and wallet
                user_profile.digital_assets = user_crypto_holdings
                user_wallet.save()
                user_profile.save()

    
                messages.success(request, "Funds added successfully.")
            else:
            # Handle form errors
                messages.error(request, "Error in form submission.")
        else:
            # Handle form errors
            messages.error(request, 'Invalid form data')

        # Redirect back to the same page
        return redirect(request.path)

    else:
        # Handle GET request
        purchase_form = AssetSellForm(current_user_id)
        user_profile = AccountProfile.objects.get(id=current_user_id)
        user_crypto_holdings = user_profile.digital_assets
        crypto_ids = list(user_crypto_holdings.keys())
        crypto_options = [{'id': crypto.id, 'name': crypto.name, 'price': str(crypto.current_price_cad)} 
                          for crypto in CryptoCurrency.objects.filter(name__in=crypto_ids)]
        crypto_options_json = json.dumps(crypto_options, cls=DjangoJSONEncoder)
        crypto_holdings_json = json.dumps(user_crypto_holdings, cls=DjangoJSONEncoder)
        return render(request, 'FrontEnd/profile.html', {
            'form': purchase_form, 
            'balance': user_wallet.account_balance, 
            'crypto_chs_json': crypto_options_json,
            'crypto_holdings': crypto_holdings_json,
            'id': "sell-currency"
        })
   
def user_purchaseses(request):
    user_id = request.session.get('user_session_id')
    if not user_id:
        messages.info(request, "Please log in to purchase cryptocurrency.")
        return redirect('/login/')
    user_purchases = CryptoTransaction.objects.filter(user=user_id)
    print("user purchases", user_purchases)
    return render(request, 'FrontEnd/profile.html', {
            'user_purchases': user_purchases, 
            
            'id': "user_purchases"
        })
