
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from .permissions import *
from .utils import cartData
from django.shortcuts import render, redirect
from .forms import DisplayCalculationForm
from .models import ProductionRun, Sell, Purchase, ManufacturedProduct, DiscountCode, CommissionCode
from .models import *
from django.http import JsonResponse,HttpResponse
import json
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from decimal import Decimal
# Create your views here.

# def main(request):
#     context={}
#     return render(request, 'store/main.html', context)


def unauthorized_access_handler(request):
    # You can render an access denied page or return a response with an error message
    return render(request, 'store/access_denied.html', {'message': 'Access Denied'})


@user_passes_test(is_seller, login_url='/access-denied/')
def calculate_profit(request):
    if request.method == 'POST':
        # Get form inputs
        product_id = request.POST['product']
        quantity = Decimal(request.POST['quantity'])
        price = Decimal(request.POST['price'])
        discount_code = request.POST['discount_code']
        commission_code = request.POST['commission_code']
        
        # Query the database to get product details
        product = ManufacturedProduct.objects.get(pk=product_id)
        
        # Calculate total price based on quantity and unit price
        total_price = product.unit_cost_after_all_expenses * quantity
        
        # Get discount and commission values based on selected codes
        discount_value = DiscountCode.objects.get(code=discount_code).discount_value
        commission_value = CommissionCode.objects.get(code=commission_code).commission_value
        
        # Calculate the cost price using the calculate_cost property
        
        # Calculate profit
        after_discount=price-(price*(discount_value/100))
        after_commission=after_discount-(after_discount*(commission_value/100))
        profit = (after_commission - total_price) 
        
        return render(request, 'store/profit_result.html', {'profit': profit})
    else:
        products = ManufacturedProduct.objects.all()
        discount_codes = DiscountCode.objects.all()
        commission_codes = CommissionCode.objects.all()
        return render(request, 'store/calculate_profit.html', {'products': products, 'discount_codes': discount_codes, 'commission_codes': commission_codes})





def calculate_total_investment():
    production_runs = ProductionRun.objects.all()
    costs = [production_run.calculate_cost for production_run in production_runs]
    total_investment = sum(costs)
    return total_investment or 0

def calculate_total_sales():
    total_sales = Sell.objects.aggregate(total_sales=models.Sum('price_after_commission'))['total_sales']
    return total_sales or 0

def calculate_total_material_cost_from_purchases():
    # Retrieve all Purchase instances and calculate the total material cost
    purchases = Purchase.objects.all()
    total_material_cost = sum(purchase.price for purchase in purchases)
    return total_material_cost or 0


@user_passes_test(is_admin, login_url='/access-denied/')
def dashboard(request):
    total_investment = calculate_total_investment()
    total_sales = calculate_total_sales()
    total_material_cost_from_purchases = calculate_total_material_cost_from_purchases()  # Calculate the total material cost from purchases

    if request.method == 'POST':
        form = DisplayCalculationForm(request.POST)
        if form.is_valid():
            show_calculations = form.cleaned_data.get('show_calculations')
    else:
        form = DisplayCalculationForm()
        show_calculations = False  # Initially, hide the calculations

    context = {
        'total_investment': total_investment,
        'total_sales': total_sales,
        'total_material_cost_from_purchases': total_material_cost_from_purchases,  # Include the total material cost from purchases in the context
        'form': form,
        'show_calculations': show_calculations,
    }

    return render(request, 'store/dashboard.html', context)





def signin(request):
    context={"message":""}
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user)
            return redirect('store')
        else:
            context["message"]="Username or Password is not correct!!!"

    return render (request,'store/signin.html',context)

def signout(request):
    logout(request)
    return redirect('signin')

def signup(request):
    
    context={"message":""}
    if request.method=='POST':
        uname=request.POST.get('username')
        fname=request.POST.get('fname')
        lname=request.POST.get('lname')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')
        if pass1!=pass2:
            context["message"]="Passwords are not Same!!"
        else:

            my_user=User.objects.create_user(uname,email,pass1)
            customer,created=Customer.objects.get_or_create(user=my_user,name=uname)
            my_user.first_name=fname
            my_user.last_name=lname
            my_user.save()
            return redirect('signin')
        



    return render (request,'store/signup.html',context)

def store(request):
    data=cartData(request)
    cartItems=data['cartItems']
    products=Product.objects.all()
    context={'products':products,'cartItems':cartItems, 'shipping':False}
    return render(request, 'store/store.html', context)
    
@login_required(login_url='signin')
def cart(request):
    data=cartData(request)
    items=data['items']
    order=data['order']
    cartItems=data['cartItems']
    context={
        'items':items,
        'order':order,
        'cartItems':cartItems,
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='signin')
def checkout(request):
    data=cartData(request)
    items=data['items']
    order=data['order']
    cartItems=data['cartItems'] 
        
    context={
        'items':items,
        'order':order,
        'cartItems':cartItems,
    }
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data=json.loads(request.body)
    productId=data['productId']
    action=data['action']
    # print('ACtion',action)
    # print('productId',productId)

    customer=request.user.customer
    product=Product.objects.get(id=productId)
    order,created=Order.objects.get_or_create(customer=customer, complete=False)
    orderItem,createrd=OrderItem.objects.get_or_create(order=order,product=product)

    if(action=='add'):
        orderItem.quantity=(orderItem.quantity+1)
    elif(action=='remove'):
        orderItem.quantity=(orderItem.quantity-1)
    orderItem.save()
    if orderItem.quantity<=0:
        orderItem.delete()
    return JsonResponse('Item is added',safe=False)

def processOrder(request):
    transaction_id=datetime.datetime.now().timestamp()
    data=json.loads(request.body)

    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer, complete=False)
        print(order)
        


    # else:
        # customer, order=guestOrder(request, data)
        
    total=float(data['form']['total'])
    order.transaction_id=transaction_id
    if total==float(order.get_cart_total):
        order.complete=True
    order.save()
    if order.shipping==True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )
    return JsonResponse("Payment Done!!!",safe=False)
