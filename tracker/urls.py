from django.conf.urls import include, url
from . import views
from django.contrib.auth import views as auth_views

app_name = 'tracker'
urlpatterns = [
               # ex: /tracker/
               url(r'^$', views.index, name='index'),
               
               # ex: /tracker/gum%20ball/product_inventory
               url(r'^(?P<product_name>[\w\s]+)/product_inventory/$', views.product_inventory, name='product_inventory'),
               # ex: /tracker/view_products lists current products
               url(r'^view_products/$', views.view_products, name='view_products'),
               # ex: /tracker/add_product brings up add new product form view
               url(r'^add_product/$', views.add_product, name='add_product'),
               # ex: /tracker/new_product accessible only through form submission from add_product.html
               url(r'^new_product/$', views.new_product, name='new_product'),
               # ex: /tracker/product_details/104 add product form, displays all details about existing products
               url(r'^product_details/(?P<sm_lot_number>\d+)$', views.product_details, name='product_details'),
               # ex: /tracker/delete_product accessible only through form submission from add_product.html
               url(r'^delete_product/(?P<sm_lot_number>\d+)$', views.delete_product, name='delete_product'),
               
               # ex: /tracker/add_inventory
               url(r'^add_inventory/$', views.add_inventory, name='add_inventory'),
               # ex: /tracker/new_inventory accessible only through form submission from add_inventory.html
               url(r'^new_inventory/$', views.new_inventory, name='new_inventory'),
               # ex: /tracker/update_inventory accessible only through form submission from product_inventory.html
               url(r'^update_inventory/(?P<counter>\d+)$', views.update_inventory, name='update_inventory'),
               # ex: /login login form for tracker application
               
               url(r'^login/$', auth_views.login, {'template_name': 'tracker/login.html'}),
               # ex: /logout clears current user session
               url(r'^log_out/$', views.log_out, name='log_out'),
               
               # ex: /place_order webpage for placing new orders
               url(r'^place_order/$', views.place_order, name='place_order'),
               # ex: /new_order accessible only from place_order.html creates a new order
               url(r'^new_order/$', views.new_order, name='new_order'),
               # ex: /view_orders renders orders_list.html and displays all current orders in system
               url(r'^view_orders/$', views.view_orders, name='view_orders'),
               # ex: /delete_order/1 deletes indicated order based on order number
               url(r'^delete_order/(?P<order_number>\d+)$', views.delete_order, name='delete_order'),
               # ex: /view_orders renders orders_list.html and displays all current orders in system
               url(r'^approve_order/(?P<order_number>\d+)$', views.approve_order, name='approve_order'),
               
               # ex: /app_settings/ renders app_settings.html and displays editable settings for application
               url(r'^app_settings/$', views.app_settings, name='app_settings'),
               # ex: /delete_email/exampleatex.com removes email from list of app alert recipients
               url(r'^delete_email/$', views.delete_email, name='delete_email'),
               # ex: /add_email adds indicated email to list of app alert recipients
               url(r'^add_email/$', views.add_email, name='add_email'),
               ]