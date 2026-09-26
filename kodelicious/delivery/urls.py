from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('open_signin', views.open_signin, name='open_signin'),
    path('open_signup', views.open_signup, name='open_signup'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),

    path('admin_home', views.admin_home, name='admin_home'),
    path('customer_home', views.customer_home, name='customer_home'),

    path('open_add_restaurant', views.open_add_restaurant, name='open_add_restaurant'),
    path('add_restaurant', views.add_restaurant, name='add_restaurant'),

    path('open_show_restaurant', views.open_show_restaurant, name='open_show_restaurant'),

    path('open_update_restaurant/<int:restaurant_id>', views.open_update_restaurant, name='open_update_restaurant'),
    path('update_restaurant/<int:restaurant_id>', views.update_restaurant, name='update_restaurant'),

    path('delete_restaurant/<int:restaurant_id>', views.delete_restaurant, name='delete_restaurant'),

    path('open_update_menu/<int:restaurant_id>', views.open_update_menu, name='open_update_menu'),
    path('update_menu/<int:restaurant_id>', views.update_menu, name='update_menu'),

    path('customer_menu/<int:restaurant_id>', views.customer_menu, name='customer_menu'),

    path('add_to_cart/<int:item_id>', views.add_to_cart, name='add_to_cart'),
    path('view_cart', views.view_cart, name='view_cart'),
    path('remove_cart_item/<int:cart_item_id>', views.remove_cart_item, name='remove_cart_item'),
    path('update_cart_item/<int:cart_item_id>', views.update_cart_item, name='update_cart_item'),

    path('checkout/<str:username>/', views.checkout, name='checkout'),
    path('checkout/<str:username>/payment_success/', views.payment_success, name='payment_success'),
    path('razorpay/create_order', views.razorpay_create_order, name='razorpay_create_order'),
    path('orders', views.orders, name='orders'),
]
