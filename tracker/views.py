from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from tracker.models import Product, Inventory
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# List all inventory entries in system
@login_required(login_url='/tracker/login/',redirect_field_name='/tracker/index')
def index(request):
    inventory_list = Inventory.objects.order_by('add_date')[:]
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

# Get an array of all existing categories
def getCategories():
    categories = []
    for product in Product.objects.all():
        if product.category not in categories:
            categories.append(product.category)
    return categories

# Add product calls the add_product.html view
def add_product(request):
    categories = getCategories()
    products = Product.objects.all()
    # Filters list of products if a filter is found
    if request.method == 'POST':
        filter = str(request.POST.get('filtcategory', 'Gum'))
        products = products.filter(category=filter)
    return render(request, 'tracker/add_product.html', {'product_list': products, 'categories': categories,})

# Creates and store product based on values entered into the new_product form
def new_product(request):
    product_name = request.POST['product_name']
    sm_lot_number = request.POST['sm_lot_number']
    weight = request.POST['weight']
    pieces = request.POST['pieces']
    category = request.POST['category']
    popular = str(request.POST['popular'])
    categories = getCategories();
    # Proceed with product creation only if both fields are not empty
    if product_name.strip() != '' and sm_lot_number.strip() != '' and weight.strip() != '' and pieces.strip() != '':
        product = Product(product_name=product_name, sm_lot_number=sm_lot_number, weight=weight, pieces=pieces, category=category, popular=popular)
        product.save()
    else:
        return render(request, 'tracker/add_product.html', {'product_list': Product.objects.all(), 'categories': categories, 'error_message': "Product name and lot number cannot be empty.",})
    return HttpResponseRedirect(reverse('tracker:add_product', args=()))

# Removes product from database
def delete_product(request):
    product_name = request.POST['product_name']
    for product in Product.objects.all():
        if str(product.product_name) == product_name:
            inventory_list = Inventory.objects.filter(product=product)
            if (len(inventory_list) > 0):
                inventory_list.delete()
            product.delete()
    return HttpResponseRedirect(reverse('tracker:add_product', args=()))

# Add new inventory for an existing product
def add_inventory(request):
    return render(request, 'tracker/add_inventory.html', {'product_list': Product.objects.all()})

# Creates and stores inventory based on values entered into the new_inventory form
def new_inventory(request):
    sm_lot_number = str(request.POST['sm_lot_number'])
    lot_number = str(request.POST['lot_number'])
    quantity = str(request.POST['quantity'])
    location = str(request.POST['location'])
    label = str(request.POST['label'])
    standard = str(request.POST['standard'])
    dessicate = str(request.POST['dessicate'])
    notes = str(request.POST['notes'])
    product = ''
    print ("Dessicate = "+dessicate)
    # Guards against blank fields
    if sm_lot_number == '' or lot_number == '' or quantity == '' or location == '':
        return render(request, 'tracker/add_inventory.html', {'product_list': Product.objects.all(), 'error_message': "Missing information, only notes can be empty.",})
    # Searches for product in database and creates inventory with indicated values if found
    for prod in Product.objects.all():
        if str(prod.sm_lot_number) == sm_lot_number:
            product = prod
    # Guards against duplicate lot numbers when entering new inventory
    for inventory in Inventory.objects.all():
        if str(inventory.lot_number) == lot_number:
            return render(request, 'tracker/add_inventory.html', {'product_list': Product.objects.all(), 'error_message': "Indicated lot number already exists. Please check existing inventory for duplicates.",})
    if product == '':
        return render(request, 'tracker/add_inventory.html', {'product_list': Product.objects.all(), 'error_message': "Product error: Product cannot be found.",})
    else:
        inventory = Inventory(product=product,
                              add_date=timezone.now(),
                              lot_number=lot_number,
                              quantity=quantity,
                              location=location,
                              label=label,
                              standard=standard,
                              dessicate=dessicate,
                              notes=notes)
        inventory.save()
        return render(request, 'tracker/add_inventory.html', {'product_list': Product.objects.all(), 'added': "1",})
        #return HttpResponseRedirect(reverse('tracker:add_inventory', {'added': "true"}, args=()))

# Updates the quantity of an existing inventory
def update_inventory(request, counter):
    lot_number = str(request.POST['lot_number'+counter])
    quantity = str(request.POST['quantity'+counter])
    sm_lot_number = str(request.POST['sm_lot_number'+counter])
    product = Product.objects.get(sm_lot_number=sm_lot_number)
    inv = ''
    inventory_list = Inventory.objects.filter(product=product)
    for inventory in Inventory.objects.all():
        if inventory.lot_number == lot_number:
            inv = inventory
    inv.quantity = quantity
    inv.save()
    return render(request, 'tracker/product_inventory.html', {'inventory_list': inventory_list, 'product_name': product.product_name,})