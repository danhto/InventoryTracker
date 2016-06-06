from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from tracker.models import Product, Inventory
from django.core.urlresolvers import reverse

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
        p_name = ''
        # Search for matching product_name
        for itm in inventory_all:
            if itm.product.product_name.lower() == product_name:
                inventory_list.append(itm)
                # Save original letter casing of name, passed product_name value is lowercased
                p_name = itm.product.product_name
    except Inventory.DoesNotExist:
        raise Http404("No inventory in system")
    return render(request, 'tracker/product_inventory.html', {'inventory_list': inventory_list, 'product_name': p_name})

# Add product calls the add_product.html view
def add_product(request):
    return render(request, 'tracker/add_product.html', {'product_list': Product.objects.all()})

# Creates and store product based on values entered into the new_product form
def new_product(request):
    product_name = request.POST['product_name']
    sm_lot_number = request.POST['sm_lot_number']
    weight = request.POST['weight']
    pieces = request.POST['pieces']
    category = request.POST['category']
    # Proceed with product creation only if both fields are not empty
    if product_name.strip() != '' and sm_lot_number.strip() != '' and weight.strip() != '' and pieces.strip() != '':
        product = Product(product_name=product_name, sm_lot_number=sm_lot_number, weight=weight, pieces=pieces, category=category)
        print(product)
        product.save()
    else:
        return render(request, 'tracker/add_product.html', {'product_list': Product.objects.all(), 'error_message': "Product name and lot number cannot be empty.",})
    return HttpResponseRedirect(reverse('tracker:add_product', args=()))

# Removes product from database
def delete_product(request):
    product_name = request.POST['product_name']
    for product in Product.objects.all():
        if str(product.product_name) == product_name:
            product.delete()
    return HttpResponseRedirect(reverse('tracker:add_product', args=()))