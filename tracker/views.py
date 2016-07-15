from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from tracker.models import Product, Inventory, Order, Pending_Stock
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.views import logout_then_login
from django.core.exceptions import ObjectDoesNotExist

def log_out(request):
    return logout_then_login(request,login_url='/tracker/login')

# List all inventory entries in system
@login_required
def index(request):
    order_by = request.GET.get('order_by', 'add_date')
    for inventory in Inventory.objects.all():
        if inventory.quantity < 1:
            inventory.delete()
    inventory_list = Inventory.objects.all().order_by(order_by)
    context = {'inventory_list': inventory_list}
    return render(request, 'tracker/index.html', context)

# Iterate through all inventory objects and display only listings that match chosen product_name
@login_required
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
    categories = {'dex':'Pressed Dextose', 'gum':'Bubble Gum', 'psg':'Panned Sugar', 'jaw':'Jawbreaker'}
    return categories

# Add product calls the add_product.html view
@login_required
def add_product(request):
    categories = getCategories()
    products = Product.objects.all()
    filter = ''
    # Filters list of products if a filter is found
    if request.method == 'POST':
        filter = str(request.POST['filtcategory'])
        if filter != '':
            products = products.filter(category=filter)
    return render(request, 'tracker/add_product.html', {'product_list': products, 'categories': categories, 'filter': filter,})

# Creates and store product based on values entered into the new_product form
@login_required
def new_product(request):
    product_name = request.POST['product_name']
    sm_lot_number = request.POST['sm_lot_number']
    weight = request.POST['weight']
    pieces = request.POST['pieces']
    category = request.POST['category']
    popular = request.POST.get('popular', 'No')
    img = request.FILES.get('photo', '')
    categories = getCategories();
    # Proceed with product creation only if both fields are not empty
    if product_name.strip() != '' and sm_lot_number.strip() != '' and weight.strip() != '' and pieces.strip() != '':
        product = Product(product_name=product_name, sm_lot_number=sm_lot_number, weight=weight, pieces=pieces, category=category, popular=popular)
        product.save()
        product.photo.save(img.name, img)
    else:
        return render(request, 'tracker/add_product.html', {'product_list': Product.objects.all(), 'categories': categories, 'error_message': "Product name and lot number cannot be empty.",})
    return HttpResponseRedirect(reverse('tracker:add_product', args=()))

@login_required
def product_details(request, sm_lot_number):
    product = Product.objects.get(sm_lot_number=sm_lot_number)
    return render(request, 'tracker/product_details.html', {'product': product,})

# Removes product from database
@login_required
def delete_product(request):
    sm_lot_number = request.POST['sm_lot_number']
    product = Product.objects.get(sm_lot_number=sm_lot_number)
    inventory_list = Inventory.objects.filter(product=product)
    if (len(inventory_list) > 0):
        inventory_list.delete()
    product.delete()
    return HttpResponseRedirect(reverse('tracker:add_product', args=()))

# Add new inventory for an existing product
@login_required
def add_inventory(request):
    return render(request, 'tracker/add_inventory.html', {'product_list': Product.objects.all()})

# Creates and stores inventory based on values entered into the new_inventory form
@login_required
def new_inventory(request):
    sm_lot_number = str(request.POST['sm_lot_number'])
    lot_number = str(request.POST['lot_number'])
    quantity = request.POST['quantity']
    location = str(request.POST['location'])
    label = request.POST['label']
    standard = str(request.POST['standard'])
    dessicate = str(request.POST['dessicate'])
    notes = str(request.POST['notes'])
    product = ''
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
@login_required
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

# Opens product ordering webpage
@login_required
def place_order(request):
    product_list = Product.objects.all()
    pending_stock = Pending_Stock.objects.all()
    return render(request, 'tracker/place_order.html', {'product_list': product_list, 'pending_stock': pending_stock})

@login_required
def new_order(request):
    MAX_QUANTITY_ON_SKIT = 64
    order_number = None
    
    # gets the last used order_number and increment by 1, if no orders exist start at 1
    try:
        index = Order.objects.count() - 1
        if index >= 0:
            order_number = Order.objects.all()[index].order_number + 1
        else:
            order_number = 1
    except ObjectDoesNotExist:
        order_number = 1

    sm_lot_number = request.POST['sm_lot_number']
    quantity = int(request.POST['quantity'])
    date = request.POST['date']
    client = request.POST['client']
    notes = request.POST['notes']
    product = Product.objects.get(sm_lot_number=sm_lot_number)
    stock = ''
    # check number of skits filled by order quantity
    skits_in_order = quantity/MAX_QUANTITY_ON_SKIT
    leftover_in_order = quantity%MAX_QUANTITY_ON_SKIT
    inventory_list = []
    # make a list of all inventory that contain product in order and order by date
    for inventory in Inventory.objects.all():
        if inventory.product.__cmp__(product):
            inventory_list.append(inventory)
    inventory_list = sorted(inventory_list, key=lambda inventory: inventory.add_date)
    # inventory_list = inventory_list.order_by('add_date')
    
    # scan all inventory for stock prioritizing full skits then date
    for inventory in inventory_list:
        skits_in_inventory = inventory.quantity/MAX_QUANTITY_ON_SKIT
        leftover_in_inventory = inventory.quantity%MAX_QUANTITY_ON_SKIT
        # check if inventory has enough stock to fill as many skits as required by order
        # inventory has enough to fullfill skit requirements of order
        if skits_in_order <= skits_in_inventory:
            # inventory has enough to fullfill leftover requirements of order
            if leftover_in_order <= leftover_in_inventory:
                quantity_taken = skits_in_order*MAX_QUANTITY_ON_SKIT + leftover_in_order
                leftover_in_order = 0
                pending_stock = Pending_Stock(order_number=order_number, inventory=inventory, quantity=quantity_taken)
                pending_stock.save()
                stock = stock + str(pending_stock.id) + ", "
            # inventory does not have enough to fullfill leftover requirements of order
            else:
                quantity_taken = skits_in_order*MAX_QUANTITY_ON_SKIT + leftover_in_inventory
                leftover_in_order = leftover_in_order - leftover_in_inventory
                pending_stock = Pending_Stock(order_number=order_number, inventory=inventory, quantity=quantity_taken)
                pending_stock.save()
                stock = stock + str(pending_stock.id) + ", "
            skits_in_order = 0
        # inventory does not have enough to fullfill skit requirements of order
        else:
            # checks if skit amount of inventory is 0
            if skits_in_inventory != 0:
                skits_taken = skits_in_inventory*MAX_QUANTITY_ON_SKIT
            else:
                skits_taken = 0
            if leftover_in_order <= leftover_in_inventory:
                quantity_taken = skits_taken + leftover_in_order
                leftover_in_order = 0
                pending_stock = Pending_Stock(order_number=order_number, inventory=inventory, quantity=quantity_taken)
                pending_stock.save()
                stock = stock + str(pending_stock.id) + ", "
            else:
                quantity_taken = skits_taken + leftover_in_inventory
                leftover_in_order = leftover_in_order - leftover_in_inventory
                pending_stock = Pending_Stock(order_number=order_number, inventory=inventory, quantity=quantity_taken)
                pending_stock.save()
                stock = stock + str(pending_stock.id) + ", "
        # if order quantity has been satisfied stop scanning inventory for stock
        if skits_in_order == 0 and leftover_in_inventory == 0:
            break
                
    order = Order(order_number=order_number, product=product, date=date, quantity=quantity, stock=stock, client=client, notes=notes)
    order.save()
    response_message = 'Order has been placed'
    #return HttpResponseRedirect(reverse('tracker:place_order', {'product_list': Product.objects.all(), 'error': "Order has been placed"}, args=()))
    return render(request, 'tracker/place_order.html', {'product_list': Product.objects.all(), 'response': response_message})

@login_required
def view_orders(request):
    order_by = request.GET.get('order_by', 'date')
    orders_all = Order.objects.all().order_by(order_by)
    return render(request, 'tracker/orders_list.html', {'orders': orders_all})

@login_required
def approve_order(request, order_number):
    order = Order.objects.get(order_number=order_number)
    response = order.update_status()
    order_by = request.GET.get('order_by', 'date')
    orders_all = Order.objects.all().order_by(order_by)
    return render(request, 'tracker/orders_list.html', {'orders': orders_all, 'response': response})

@login_required
def delete_order(request, order_number_:
    for pending_stock in Pending_Stock.objects.all():
        if pending_stock.order_number == order_number:
            pending_stock.delete()
    order = Order.objects.get(order_number=order_number)
    order.delete()
    