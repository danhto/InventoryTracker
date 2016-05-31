from django.shortcuts import render
from django.http import HttpResponse, Http404
from tracker.models import Product, Inventory

# List all inventory entries in system
def index(request):
    inventory_list = Inventory.objects.order_by('add_date')[:10]
    context = {'inventory_list': inventory_list}
    return render(request, 'tracker/index.html', context)

# Iterate through all inventory objects and display only listings that match chosen product_name
def product_inventory(request, product_name):
    try:
        inventory_all = Inventory.objects.all()
        inventory_list = []
        p_name = ""
        # Search for matching product_name
        for itm in inventory_all:
            if itm.product.product_name.lower() == product_name:
                inventory_list.append(itm)
                # Save original letter casing of name, passed product_name value is lowercased
                p_name = itm.product.product_name
    except Inventory.DoesNotExist:
        raise Http404("No inventory in system")
    return render(request, 'tracker/product_inventory.html', {'inventory_list': inventory_list, 'product_name': p_name})

def add_product(request):
    return render(request, 'tracker/add_product.html')