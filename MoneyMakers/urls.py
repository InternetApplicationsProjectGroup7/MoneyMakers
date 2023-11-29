from django.urls import path, include, path
from MoneyMakers import views
from .views import process_user_logout

app_name = 'MoneyMakers'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_user, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('send_forgotpassword/', views.send_forgotpassword_mail, name='send_forgotpassword_mail'),
    path('forgotpassword',views.forgot_password,name="forgotpassword"),
    path('changepassword',views.change_password,name="changepassword"),
    path('process_form/', views.handle_user_input, name='process_form'),
    path('coins/<str:cryptocurrency_name>/', views.generate_crypto_chart, name='dynamic_crypto'),
    path('userprofile/', views.handle_user_profile, name='profile'),
    path('userprofile/accountsecurity/', views.update_user_password, name='change password'),
    path('userprofile/delete_account/', views.remove_user_account, name='delete_account'),
    path('logout/', views.process_user_logout, name='logout'),
    path('add_to_wishlist/<str:cryptocurrency_name>/', views.include_in_wishlist, name='add-to-wishlist'),
    path('wishlist/', views.display_user_wishlist, name='wishlist'),
    path('userprofile/add_money/', views.process_add_money, name='add_money'),
    path('userprofile/purchase_currency/', views.execute_currency_purchase, name='purchase_currency'),
    path('userprofile/sell_currency/', views.execute_currency_sell, name='sell_currency'),
    path('userprofile/user_purchases/', views.user_purchaseses, name='user_purchases'),

    ]