from django.conf.urls import include, url
from . import views

app_name = 'tracker'
urlpatterns = [
               # ex: /tracker/
               url(r'^$', views.index, name='index'),
               # ex: /tracker/gum%20ball/product_info
               url(r'^(?P<product_name>[\w\s]+)/product_inventory/$', views.product_inventory, name='product_inventory'),
               # ex: /tracker/add_product
               url(r'^add_product/$', views.add_product, name='add_product'),
               # ex: /tracker/new_product
               url(r'^new_product/$', views.new_product, name='new_product'),
               # ex: /tracker/delete_product
               url(r'^delete_product/$', views.delete_product, name='delete_product'),
               ]