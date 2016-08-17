from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from tracker.models import Product, Inventory, Order, Pending_Stock
from django.core.urlresolvers import reverse, resolve
from django.utils import timezone
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.views import logout_then_login
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from django.core.mail import send_mail

def log_out(request):
    return logout_then_login(request,login_url='/tracker/login')

# List all inventory entries in system
@login_required
def index(request):
    order_by = request.GET.get('order_by', 'add_date')
    inventory_list = []
    for inventory in Inventory.objects.all():
        # do not include empty inventory in displayed list of current stock
        if not inventory.no_stock():
            inventory_list.append(inventory)
            # if inventory stock is critical send administrator an email alert and toggle alert switch
            if inventory.critical_stock() and inventory.alerts == 0:
                inventory.alert_sent(False)
                email_alerts('stock', inventory.lot_number)
            # if inventory stock is no longer critical reset alert status
            if not inventory.critical_stock() and inventory.alerts == 1:
                inventory.alert_sent(True)
    inventory_list = sorted(inventory_list, key=lambda inventory: getattr(inventory, order_by))
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

# View product calls the product_list.html view
@login_required
@permission_required('tracker.add_product', raise_exception=True)
def view_products(request):
    categories = getCategories()
    products = Product.objects.all()
    filter = ''
    # Filters list of products if a filter is found
    if request.method == 'POST':
        filter = str(request.POST['filtcategory'])
        if filter != '':
            products = products.filter(category=filter)
    return render(request, 'tracker/product_list.html', {'product_list': products, 'categories': categories, 'filter': filter,})


# Add product calls the add_product.html view
@login_required
@permission_required('tracker.add_product', raise_exception=True)
def add_product(request):
    categories = getCategories()
    products = Product.objects.all()
    return render(request, 'tracker/add_product.html', {'product_list': products, 'categories': categories,})

# Creates and store product based on values entered into the new_product form
@login_required
@permission_required('tracker.add_product', raise_exception=True)
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
        # Check if product with specified lot number already exists
        try:
            product = Product.objects.get(sm_lot_number=sm_lot_number)
        except Product.DoesNotExist:
            product = None
        if product != None:
            return render(request, 'tracker/add_product.html', {'product_list': Product.objects.all(), 'categories': categories, 'error_message': "Product with lot number " + sm_lot_number + " already exists. Please choose a different lot number.",})
        product = Product(product_name=product_name, sm_lot_number=sm_lot_number, weight=weight, pieces=pieces, category=category, popular=popular)
        product.save()
        product.photo.save(img.name, img)
    else:
        return render(request, 'tracker/add_product.html', {'product_list': Product.objects.all(), 'categories': categories, 'error_message': "Product name and lot number cannot be empty.",})
    messages.success(request, "Product successfully created.")
    return HttpResponseRedirect(reverse('tracker:add_product', args=()))

@login_required
@permission_required('tracker.add_product', raise_exception=True)
def product_details(request, sm_lot_number):
    product = Product.objects.get(sm_lot_number=sm_lot_number)
    return render(request, 'tracker/product_details.html', {'product': product,})

# Removes product from database
@login_required
@permission_required('tracker.delete_product', raise_exception=True)
def delete_product(request, sm_lot_number):
    product = Product.objects.get(sm_lot_number=sm_lot_number)
    inventory_list = Inventory.objects.filter(product=product)
    if (len(inventory_list) > 0):
        inventory_list.delete()
    product.delete()
    return HttpResponseRedirect(reverse('tracker:add_product', args=()))

# Add new inventory for an existing product
@login_required
@permission_required('tracker.add_inventory', raise_exception=True)
def add_inventory(request):
    return render(request, 'tracker/add_inventory.html', {'product_list': Product.objects.all()})

# Creates and stores inventory based on values entered into the new_inventory form
@login_required
@permission_required('tracker.add_inventory', raise_exception=True)
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
@permission_required('tracker.change_inventory', raise_exception=True)
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
    if inv.quantity != int(quantity):
        inv.quantity = quantity
        inv.save()
        response_message = "Quantity successfully updated for " + product.product_name + " in inventory " + lot_number + "."
    else:
        response_message = "Quantity set is the same as before, no change has been made. "
    return render(request, 'tracker/product_inventory.html', {'inventory_list': inventory_list, 'product_name': product.product_name, 'response': response_message})

# Opens product ordering webpage
@login_required
@permission_required('tracker.add_order', raise_exception=True)
def place_order(request):
    product_list = Product.objects.all()
    pending_stock = Pending_Stock.objects.all()
    return render(request, 'tracker/place_order.html', {'product_list': product_list, 'pending_stock': pending_stock})

@login_required
@permission_required('tracker.add_order', raise_exception=True)
def new_order(request):
    MAX_QUANTITY_ON_SKIT = 64
    order_number = None
    response_message = ''
    
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
            if not inventory.no_stock():
                inventory_list.append(inventory)
    inventory_list = sorted(inventory_list, key=lambda inventory: inventory.add_date)
    
    # scan all inventory for stock prioritizing full skits then date
    for inventory in inventory_list:
        skits_in_inventory = inventory.quantity/MAX_QUANTITY_ON_SKIT
        leftover_in_inventory = inventory.quantity%MAX_QUANTITY_ON_SKIT
        
        # check if inventory has enough stock to fill as many skits as required by order
        # inventory has enough to fullfill skit requirements of order
        if skits_in_order <= skits_in_inventory:
            if skits_in_order < skits_in_inventory:
                leftover_in_inventory = leftover_in_inventory + (skits_in_inventory - skits_in_order)*MAX_QUANTITY_ON_SKIT
            # inventory has enough to fullfill leftover requirements of order
            if leftover_in_order <= leftover_in_inventory:
                quantity_taken = skits_in_order*MAX_QUANTITY_ON_SKIT + leftover_in_order
                # checks to make sure stock is not held for another order
                if checkPendingStock(inventory, quantity_taken):
                    leftover_in_order = 0
                    pending_stock = Pending_Stock(order_number=order_number, inventory=inventory, quantity=quantity_taken)
                    pending_stock.save()
                    stock = stock + str(pending_stock.id) + ", "
                    skits_in_order = 0
                else:
                    response_message = "Pending stock already held for another order. "
            # inventory does not have enough to fullfill leftover requirements of order
            else:
                quantity_taken = skits_in_order*MAX_QUANTITY_ON_SKIT + leftover_in_inventory
                if checkPendingStock(inventory, quantity_taken):
                    leftover_in_order = leftover_in_order - leftover_in_inventory
                    pending_stock = Pending_Stock(order_number=order_number, inventory=inventory, quantity=quantity_taken)
                    pending_stock.save()
                    stock = stock + str(pending_stock.id) + ", "
                    skits_in_order = 0
                else:
                    response_message = "Pending stock already held for another order. "
        # inventory does not have enough to fullfill skit requirements of order
        else:
            # checks if skit amount of inventory is 0
            if skits_in_inventory != 0:
                skits_taken = skits_in_inventory
            else:
                skits_taken = 0
            if leftover_in_order <= leftover_in_inventory:
                quantity_taken = skits_taken*MAX_QUANTITY_ON_SKIT + leftover_in_order
                if checkPendingStock(inventory, quantity_taken):
                    leftover_in_order = 0
                    pending_stock = Pending_Stock(order_number=order_number, inventory=inventory, quantity=quantity_taken)
                    pending_stock.save()
                    stock = stock + str(pending_stock.id) + ", "
                    skits_in_order = skits_in_order - skits_taken
                else:
                    response_message = "Pending stock already held for another order. "
            else:
                if leftover_in_inventory != 0:
                    quantity_taken = skits_taken*MAX_QUANTITY_ON_SKIT + leftover_in_inventory
                    if checkPendingStock(inventory, quantity_taken):
                        leftover_in_order = leftover_in_order - leftover_in_inventory
                        pending_stock = Pending_Stock(order_number=order_number, inventory=inventory, quantity=quantity_taken)
                        pending_stock.save()
                        stock = stock + str(pending_stock.id) + ", "
                        skits_in_order = skits_in_order - skits_taken
                    else:
                        response_message = "Pending stock already held for another order. "
    
        # if order quantity has been satisfied stop scanning inventory for stock
        if skits_in_order == 0 and leftover_in_order == 0:
            break

    if skits_in_order != 0 or leftover_in_order != 0:
        response_message = response_message + 'Insufficient inventory to place order!'
        return render(request, 'tracker/place_order.html', {'product_list': Product.objects.all(), 'response': response_message})
    else:
        order = Order(order_number=order_number, product=product, date=date, quantity=quantity, stock=stock, client=client, notes=notes)
        order.save()
        response_message = 'Order has been placed'
        email_alerts('order', order.get_stock)  # send email alert to administrator about new order
        return render(request, 'tracker/place_order.html', {'product_list': Product.objects.all(), 'response': response_message})

@login_required
def view_orders(request):
    # retrieves and displays all current orders in system and renders orders_list.html
    order_by = request.GET.get('order_by', 'date')
    orders_all = Order.objects.all().order_by(order_by)
    return render(request, 'tracker/orders_list.html', {'orders': orders_all})

@login_required
@permission_required('tracker.change_order', raise_exception=True)
def approve_order(request, order_number):
    order_number = int(order_number)
    # change status of pending orders selected in orders_list.html
    order = Order.objects.get(order_number=order_number)
    response = order.update_status()
    if response:
        response = 'Order ' + str(order_number) + ' has been successfully approved. Stock has been removed from inventory.'
        order.save()
        # remove quantity for pending_stock from inventory
        for stock in Pending_Stock.objects.all():
            if stock.order_number == order_number:
                inventory = stock.inventory
                inventory.quantity = inventory.quantity - stock.quantity
                inventory.save()
    else:
        response = 'Error: Order ' + str(order_number) + ' is already approved.'
    order_by = request.GET.get('order_by', 'date')
    orders_all = Order.objects.all().order_by(order_by)
    return render(request, 'tracker/orders_list.html', {'orders': orders_all, 'response': response})

@login_required
@permission_required('tracker.delete_order', raise_exception=True)
def delete_order(request, order_number):
    order_number = int(order_number)
    # delete pending_stock from associated orders
    for pending_stock in Pending_Stock.objects.all():
        if pending_stock.inventory.no_stock():
            lot = str(pending_stock.inventory.lot_number)
            Inventory.objects.get(lot_number=lot).delete()
        if pending_stock.order_number == order_number:
            pending_stock.delete()
    # delete orders from system based on order_number selected in orders_list.html
    order = Order.objects.get(order_number=order_number)
    order.delete()
    response = 'Order deleted'
    return render(request, 'tracker/orders_list.html', {'orders': Order.objects.all(), 'response': response})

# custom view for permission denied exception
def custom_permission_denied_view(request):
    return render(request, 'tracker/403.html', {}, status=403)

### METHODS ###

# Get an array of all existing categories
def getCategories():
    categories = {'dex':'Pressed Dextose', 'gum':'Bubble Gum', 'psg':'Panned Sugar', 'jaw':'Jawbreaker'}
    return categories

# Check pending stock to ensure there is room to place order
def checkPendingStock(inventory, order_quantity):
    quantity = int(inventory.quantity)
    for order in Pending_Stock.objects.all():
        # No need to check for conflicts if order has been approved
        if order.status != 'Approved':
            if order.inventory.lot_number == inventory.lot_number:
                quantity = quantity - order.quantity
    # if inventory has sufficient quantities then order can proceed
    if quantity >= order_quantity:
        return True
    else:
        return False

# Send mail
def email_alerts(alert, content):
    subject = ""
    body = ""
    if alert == 'stock':
        subject = "Low stock"
        body = "Stock for " + content + " is running low."
    else:
        subject = "A new order has been placed"
        body = "Order " + content + " requires your approval."

    send_mail(
              subject,
              body,
              'alert@inventorytracker.com',
              ['it@yfs.ca'],
              fail_silently=False,)
