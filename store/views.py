from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
from store.forms import ImproveForm
from store.models import Improve, Order
from django.contrib.auth import get_user_model
from Account.models import Account
user= get_user_model()
def store(request, *args, **kwargs):
    user_id = request.user.id
    data = cartData(request)
    cartItems = data['cartItems']
    context = {'cartItems':cartItems}
    try:
        account = Account.objects.get(pk=user_id)
        if account:
            context['profile_image'] = account.ImageURL
    except:
        pass
    if request.POST:
        form = ImproveForm(request.POST)
        if form.is_valid():
            form.save()
            field1 = form.cleaned_data.get('field1')
    return render(request, 'store/store.html', context)
def order(request):
    user_id = request.user.id
    data = cartData(request)
    cartItems = data['cartItems']
    context = {'cartItems':cartItems}
    try:
        account = Account.objects.get(pk=user_id)
        if account:
            context['profile_image'] = account.ImageURL
    except:
        pass
    return render(request, 'store/order.html', context)
 
def store1(request, category=None):
    user_id = request.user.id
    data = cartData(request)
    cartItems = data['cartItems']
    if category:
        products = Product.objects.filter(category = category)
    else:
        products = Product.objects.all()
    context = {'products': products,'cartItems':cartItems}
    try:
        account = Account.objects.get(pk=user_id)
        if account:
            context['profile_image'] = account.ImageURL
    except:
        pass
    return render(request, 'store/store1.html', context)
def cart(request):
    user_id = request.user.id
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items  =data['items']
    context = {'items':items, 'order':order, 'cartItems':cartItems, 'shipping':False}
    try:
        account = Account.objects.get(pk=user_id)
        if account:
            context['profile_image'] = account.ImageURL
    except:
        pass
    return render(request, 'store/cart.html', context)
def checkout(request):
    user_id = request.user.id
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items  =data['items']
    context = {'items':items, 'order':order, 'cartItems':cartItems, 'shipping':False}
    try:
        account = Account.objects.get(pk=user_id)
        if account:
            context['profile_image'] = account.ImageURL
    except:
        pass
    return render(request, 'store/checkout.html', context)
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete = 'c')
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added',safe=False)
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete = 'c')
    else:
        customer, order = guestOrder(request, data)
    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    if total == order.get_cart_total:
        order.complete = 'p'
    order.save()
    if order.shipping == True:
        ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode'],
            )
    return JsonResponse('Customer details submitted',safe=False)

