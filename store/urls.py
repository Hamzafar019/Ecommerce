from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('signin/', views.signin, name="signin"),
    path('signup/', views.signup, name="signup"),
    path('signout/', views.signout, name="signout"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/',views.updateItem,name="update_item"),
    path('process_order/',views.processOrder,name="process_order"),
    path('dashboard/',views.dashboard,name="dashboard"),   
    path('calculate_profit/',views.calculate_profit,name="calculate_profit"),
    path('profit_result/',views.calculate_profit,name="profit_result"),
    path('access-denied/', views.unauthorized_access_handler, name='access-denied'),
     
]
