from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from django.conf import settings
from .models import Customer, Restaurant, Item, Cart, CartItem, Order, OrderItem
import razorpay

ADMIN_USERNAMES = ['admin', 'kodelicious']


def get_user_context(request):
    """Helper to get user info from session."""
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = Customer.objects.get(id=user_id)
            return {'logged_in': True, 'username': user.username, 'is_admin': user.is_admin}
        except Customer.DoesNotExist:
            request.session.flush()
    return {'logged_in': False}


def require_login(request):
    """Check if user is logged in, redirect to signin if not."""
    if not request.session.get('user_id'):
        return redirect('open_signin')
    return None


def require_admin(request):
    """Check if user is admin, redirect to customer_home if not."""
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('open_signin')
    try:
        user = Customer.objects.get(id=user_id)
        if not user.is_admin:
            return redirect('customer_home')
    except Customer.DoesNotExist:
        request.session.flush()
        return redirect('open_signin')
    return None


def index(request):
    return render(request, 'delivery/index.html', get_user_context(request))


def open_signin(request):
    if request.session.get('user_id'):
        try:
            user = Customer.objects.get(id=request.session['user_id'])
            if user.is_admin:
                return redirect('admin_home')
            return redirect('customer_home')
        except Customer.DoesNotExist:
            request.session.flush()
    return render(request, 'delivery/signin.html')


def open_signup(request):
    if request.session.get('user_id'):
        try:
            user = Customer.objects.get(id=request.session['user_id'])
            if user.is_admin:
                return redirect('admin_home')
            return redirect('customer_home')
        except Customer.DoesNotExist:
            request.session.flush()
    return render(request, 'delivery/signup.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        if username.lower() in [name.lower() for name in ADMIN_USERNAMES]:
            return render(request, 'delivery/signup.html', {'error': 'This username is not allowed.'})

        if len(password) < 4:
            return render(request, 'delivery/signup.html', {'error': 'Password must be at least 4 characters.'})

        if Customer.objects.filter(username__iexact=username).exists():
            return render(request, 'delivery/signup.html', {'error': 'Username already taken.'})

        user = Customer.objects.create(
            username=username,
            password=password,
            email=email,
            mobile=mobile,
            address=address,
            is_admin=False,
        )
        request.session['user_id'] = user.id
        request.session['username'] = user.username
        return redirect('customer_home')
    return render(request, 'delivery/signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        try:
            user = Customer.objects.get(username__iexact=username, password=password)
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            if user.is_admin:
                return redirect('admin_home')
            return redirect('customer_home')
        except Customer.DoesNotExist:
            return render(request, 'delivery/signin.html', {'error': 'Invalid username or password'})
    return render(request, 'delivery/signin.html')


def logout(request):
    request.session.flush()
    return redirect('index')


def admin_home(request):
    redirect_resp = require_admin(request)
    if redirect_resp:
        return redirect_resp
    return render(request, 'delivery/admin_home.html', get_user_context(request))


def customer_home(request):
    redirect_resp = require_login(request)
    if redirect_resp:
        return redirect_resp
    ctx = get_user_context(request)
    ctx['restaurants'] = Restaurant.objects.all()
    return render(request, 'delivery/customer_home.html', ctx)


def open_add_restaurant(request):
    redirect_resp = require_admin(request)
    if redirect_resp:
        return redirect_resp
    return render(request, 'delivery/add_restaurant.html', get_user_context(request))


def add_restaurant(request):
    redirect_resp = require_admin(request)
    if redirect_resp:
        return redirect_resp

    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')

        if Restaurant.objects.filter(name__iexact=name).exists():
            ctx = get_user_context(request)
            ctx['error'] = 'Restaurant with this name already exists.'
            return render(request, 'delivery/add_restaurant.html', ctx)

        data = {'name': name, 'cuisine': cuisine, 'rating': rating}
        if picture:
            data['picture'] = picture
        Restaurant.objects.create(**data)
    return redirect('admin_home')


def open_show_restaurant(request):
    redirect_resp = require_admin(request)
    if redirect_resp:
        return redirect_resp
    ctx = get_user_context(request)
    ctx['restaurantList'] = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html', ctx)


def open_update_restaurant(request, restaurant_id):
    redirect_resp = require_admin(request)
    if redirect_resp:
        return redirect_resp
    ctx = get_user_context(request)
    ctx['restaurant'] = Restaurant.objects.get(id=restaurant_id)
    return render(request, 'delivery/update_restaurant.html', ctx)


def update_restaurant(request, restaurant_id):
    redirect_resp = require_admin(request)
    if redirect_resp:
        return redirect_resp

    restaurant = Restaurant.objects.get(id=restaurant_id)
    if request.method == 'POST':
        restaurant.name = request.POST.get('name')
        restaurant.picture = request.POST.get('picture')
        restaurant.cuisine = request.POST.get('cuisine')
        restaurant.rating = request.POST.get('rating')
        restaurant.save()
    return redirect('open_show_restaurant')


def delete_restaurant(request, restaurant_id):
    redirect_resp = require_admin(request)
    if redirect_resp:
        return redirect_resp
    Restaurant.objects.get(id=restaurant_id).delete()
    return redirect('open_show_restaurant')


def open_update_menu(request, restaurant_id):
    redirect_resp = require_admin(request)
    if redirect_resp:
        return redirect_resp
    restaurant = Restaurant.objects.get(id=restaurant_id)
    ctx = get_user_context(request)
    ctx['itemList'] = restaurant.items.all()
    ctx['restaurant'] = restaurant
    return render(request, 'delivery/update_menu.html', ctx)


def update_menu(request, restaurant_id):
    redirect_resp = require_admin(request)
    if redirect_resp:
        return redirect_resp

    restaurant = Restaurant.objects.get(id=restaurant_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        vegeterian = request.POST.get('vegeterian') == 'on'
        picture = request.POST.get('picture')

        if Item.objects.filter(name__iexact=name, restaurant=restaurant).exists():
            ctx = get_user_context(request)
            ctx['itemList'] = restaurant.items.all()
            ctx['restaurant'] = restaurant
            ctx['error'] = 'Item with this name already exists in this menu.'
            return render(request, 'delivery/update_menu.html', ctx)

        Item.objects.create(
            restaurant=restaurant,
            name=name,
            description=description,
            price=price,
            vegeterian=vegeterian,
            picture=picture,
        )
    return redirect('open_update_menu', restaurant_id=restaurant_id)


def customer_menu(request, restaurant_id):
    redirect_resp = require_login(request)
    if redirect_resp:
        return redirect_resp
    restaurant = Restaurant.objects.get(id=restaurant_id)
    menu_items = restaurant.items.all()
    ctx = get_user_context(request)
    ctx['restaurant'] = restaurant
    ctx['menu_items'] = menu_items
    return render(request, 'delivery/customer_menu.html', ctx)


def add_to_cart(request, item_id):
    redirect_resp = require_login(request)
    if redirect_resp:
        return redirect_resp
    if request.method == 'POST':
        user = Customer.objects.get(id=request.session['user_id'])
        menu_item = Item.objects.get(id=item_id)
        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        return redirect(f'/customer_menu/{menu_item.restaurant.id}?added={menu_item.name}')
    return redirect('customer_home')


def view_cart(request):
    redirect_resp = require_login(request)
    if redirect_resp:
        return redirect_resp
    user = Customer.objects.get(id=request.session['user_id'])
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = cart.items.all()
    total_price = cart.get_total_price()
    ctx = get_user_context(request)
    ctx['cart_items'] = cart_items
    ctx['total_price'] = total_price
    return render(request, 'delivery/view_cart.html', ctx)


def remove_cart_item(request, cart_item_id):
    redirect_resp = require_login(request)
    if redirect_resp:
        return redirect_resp
    user = Customer.objects.get(id=request.session['user_id'])
    cart = Cart.objects.get(user=user)
    cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
    cart_item.delete()
    return redirect('view_cart')


def update_cart_item(request, cart_item_id):
    redirect_resp = require_login(request)
    if redirect_resp:
        return redirect_resp
    if request.method == 'POST':
        user = Customer.objects.get(id=request.session['user_id'])
        cart = Cart.objects.get(user=user)
        cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
    return redirect('view_cart')


def checkout(request, username):
    redirect_resp = require_login(request)
    if redirect_resp:
        return redirect_resp
    user = Customer.objects.get(id=request.session['user_id'])
    if username != user.username:
        return redirect('checkout', username=user.username)
    if request.method != 'GET':
        return redirect('checkout', username=user.username)

    cart, created = Cart.objects.get_or_create(user=user)
    if not cart.items.exists():
        return redirect('view_cart')

    return render(request, 'delivery/checkout.html', _checkout_context(request, cart))


def orders(request):
    redirect_resp = require_login(request)
    if redirect_resp:
        return redirect_resp
    user = Customer.objects.get(id=request.session['user_id'])
    order = Order.objects.filter(user=user).order_by('-created_at').first()
    ctx = get_user_context(request)
    ctx['order'] = order
    ctx['username'] = user.username
    return render(request, 'delivery/orders.html', ctx)

def _razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def _checkout_context(request, cart, error=None):
    """Shared context for the checkout page."""
    ctx = get_user_context(request)
    ctx['cart_items'] = cart.items.all()
    ctx['total_price'] = cart.get_total_price()
    if error:
        ctx['error'] = error
    return ctx


def razorpay_create_order(request):
    """Create a Razorpay order for the logged-in user's cart. Returns JSON."""
    redirect_resp = require_login(request)
    if redirect_resp:
        return JsonResponse({'error': 'Please sign in to continue.'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required.'}, status=405)

    user = Customer.objects.get(id=request.session['user_id'])
    cart, _ = Cart.objects.get_or_create(user=user)
    if not cart.items.exists():
        return JsonResponse({'error': 'Your cart is empty.'}, status=400)

    amount = max(int(round(cart.get_total_price() * 100)), 100)
    try:
        rzp_order = _razorpay_client().order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1,
        })
    except Exception:
        return JsonResponse(
            {'error': 'Could not start the payment. Please try again.'},
            status=502,
        )

    return JsonResponse({
        'order_id': rzp_order['id'],
        'amount': amount,
        'currency': 'INR',
        'key_id': settings.RAZORPAY_KEY_ID,
    })


def payment_success(request, username):
    """Verify the Razorpay payment signature, then convert the cart into an order."""
    redirect_resp = require_login(request)
    if redirect_resp:
        return redirect_resp
    user = Customer.objects.get(id=request.session['user_id'])
    if username != user.username:
        return redirect('payment_success', username=user.username)
    if request.method != 'POST':
        return redirect('checkout', username=user.username)

    cart, _ = Cart.objects.get_or_create(user=user)
    if not cart.items.exists():
        return redirect('orders')

    params = {
        key: request.POST.get(key, '')
        for key in ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
    }
    if not all(params.values()):
        return render(
            request,
            'delivery/checkout.html',
            _checkout_context(request, cart, error='Payment was not completed. Please try again.'),
        )

    try:
        _razorpay_client().utility.verify_payment_signature(params)
    except Exception:
        return render(
            request,
            'delivery/checkout.html',
            _checkout_context(
                request,
                cart,
                error='Payment verification failed. You have not been charged.',
            ),
        )

    order = Order.objects.create(
        user=user,
        address=user.address,
        total_price=cart.get_total_price(),
        status='confirmed',
    )
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            menu_item=cart_item.menu_item,
            quantity=cart_item.quantity,
            price=cart_item.menu_item.price,
        )
    cart.items.all().delete()
    request.session['last_order_id'] = order.id
    return redirect('orders')