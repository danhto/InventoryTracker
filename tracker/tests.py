from django.test import TestCase
from django.utils import timezone
from tracker.models import Product, Inventory, Order, Pending_Stock

def createProductA():
    product_name = 'Test'
    sm_lot_number = '100'
    weight = 100
    pieces = 10
    category = 'DEX'
    popular = 'Yes'
    photo = None
    return Product(product_name=product_name,
                        sm_lot_number=sm_lot_number,
                        weight=weight,
                        pieces=pieces,
                        category=category,
                        popular=popular)

def createProductB():
    product_name = 'Test2'
    sm_lot_number = '101'
    weight = 50
    pieces = 20
    category = 'Gum'
    popular = 'No'
    photo = None
    return Product(product_name=product_name,
                   sm_lot_number=sm_lot_number,
                   weight=weight,
                   pieces=pieces,
                   category=category,
                   popular=popular)

def createInventory(product, lot, in_qty):
    global add_date
    add_date = timezone.now()
    lot_number = '123' + lot
    quantity = in_qty
    location = 'warehouse'
    label = '0'
    standard = 'Yes'
    dessicate = 'No'
    return Inventory(product=product,
                    add_date=add_date,
                    lot_number=lot_number,
                    quantity=quantity,
                    location=location,
                    label=label,
                    standard=standard,
                    dessicate=dessicate,)

# Check pending stock to ensure there is room to place order
def checkPendingStock(inventory):
    quantity = int(inventory.quantity)
    for p_stock in Pending_Stock.objects.all():
        # No need to check for conflicts if order has been approved
        order_number = p_stock.order_number
        if p_stock.status != 'Approved':
            if p_stock.inventory.lot_number == inventory.lot_number:
                quantity = quantity - p_stock.quantity
    # if inventory has sufficient quantities then order can proceed
    return quantity

def delete_order(order, order_number):
    order_number = int(order_number)
    # delete pending_stock from associated orders
    for pending_stock in Pending_Stock.objects.all():
        if pending_stock.inventory == 0:
            lot = str(pending_stock.inventory.lot_number)
            Inventory.objects.get(lot_number=lot).delete()
        if pending_stock.order_number == order_number:
            pending_stock.delete()
    order.delete()

def createOrder(product, quantity):
    global order_date
    MAX_QUANTITY_ON_SKIT = 64
    order_date = timezone.now()
    client = 'Starwars'
    order_number = 1
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

    pending_flag = False
    # scan all inventory for stock prioritizing full skits then date
    for inventory in inventory_list:
        actual_inv_qty = checkPendingStock(inventory)
        if actual_inv_qty < int(inventory.quantity):
            pending_flag = True
        skits_in_inventory = actual_inv_qty/MAX_QUANTITY_ON_SKIT
        leftover_in_inventory = actual_inv_qty%MAX_QUANTITY_ON_SKIT
        
        print ("Quantity ordered: "+str(quantity))
        print ("Skits in inventory: "+str(skits_in_inventory))
        print ("Leftover in inventory: "+str(leftover_in_inventory))
        print ("Skits in order: "+str(skits_in_order))
        print ("Leftover in order: "+str(leftover_in_order))

        # check if inventory has enough stock to fill as many skits as required by order
        # inventory has enough to fullfill skit requirements of order
        if skits_in_order <= skits_in_inventory:
            if skits_in_order < skits_in_inventory:
                leftover_in_inventory = leftover_in_inventory + (skits_in_inventory - skits_in_order)*MAX_QUANTITY_ON_SKIT
            # inventory has enough to fullfill leftover requirements of order
            if leftover_in_order <= leftover_in_inventory:
                quantity_taken = skits_in_order*MAX_QUANTITY_ON_SKIT + leftover_in_order
                leftover_in_order = 0
                pending_stock = Pending_Stock(order_number=order_number, inventory=inventory, quantity=quantity_taken)
                pending_stock.save()
                stock = stock + str(pending_stock.id) + ", "
                skits_in_order = 0
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
                skits_taken = skits_in_inventory
            else:
                skits_taken = 0
            if leftover_in_order <= leftover_in_inventory:
                quantity_taken = skits_taken*MAX_QUANTITY_ON_SKIT + leftover_in_order
                leftover_in_order = 0
                pending_stock = Pending_Stock(order_number=order_number, inventory=inventory, quantity=quantity_taken)
                pending_stock.save()
                stock = stock + str(pending_stock.id) + ", "
                skits_in_order = skits_in_order - skits_taken
            else:
                if leftover_in_inventory != 0:
                    quantity_taken = skits_taken*MAX_QUANTITY_ON_SKIT + leftover_in_inventory
                    leftover_in_order = leftover_in_order - leftover_in_inventory
                    pending_stock = Pending_Stock(order_number=order_number, inventory=inventory, quantity=quantity_taken)
                    pending_stock.save()
                    stock = stock + str(pending_stock.id) + ", "
                    skits_in_order = skits_in_order - skits_taken

        # if order quantity has been satisfied stop scanning inventory for stock
        if skits_in_order == 0 and leftover_in_order == 0:
            break

    if skits_in_order != 0 or leftover_in_order != 0:
        response = "Insufficient stock. "
        if pending_flag:
            response = response + "Stock held. "
        return response
    else:
        return Order(order_number=1, product=product, date=order_date, quantity=quantity, stock=stock, client=client)

class ProductMethodTests(TestCase):

    def test_product_creation(self):
        product = createProductA()
        self.assertEqual(product.__str__(), product.product_name)
        self.assertEqual(product.product_name, 'Test')
        self.assertEqual(product.sm_lot_number, '100')
        self.assertEqual(product.weight, 100)
        self.assertEqual(product.pieces, 10)
        self.assertEqual(product.category, 'DEX')
        self.assertEqual(product.popular, 'Yes')

class InventoryMethodTests(TestCase):

    def test_inventory_creation(self):
        inventory = createInventory(createProductA(), 'AA', 100)
        self.assertEqual(inventory.__str__(), "Test - 123AA -quantity: 100 -location: warehouse")
        self.assertEqual(inventory.add_date, add_date)
        self.assertEqual(inventory.get_label_display(), 'No Label')
        self.assertEqual(inventory.standard, 'Yes')
        self.assertEqual(inventory.dessicate, 'No')

class OrderMethodTests(TestCase):

    # Tests to make sure orders are created with pending status as default
    def test_order_creation(self):
        print("+++Start test_order_creation+++")
        product = createProductA()
        product.save()
        inventory = createInventory(product, 'AA', 100)
        inventory.save()
        
        self.assertEqual(inventory.quantity, 100)
        
        order = createOrder(product, 50)
        self.assertEqual(order.is_approved(), False)
        self.assertEqual(order.get_status_display(), 'Pending')

        # status changes to approved after method update_status is called
        order.update_status()
        self.assertEqual(order.is_approved(), True)
        print("+++End test_order_creation+++")

class ObjectCreationTests(TestCase):

    # Check created objects exist in database
    def test_objects_successfully_added(self):
        print("++++Start test_objects_successfully_added+++")
        # Create product Test and Test2
        productA = createProductA()
        productB = createProductB()
        productA.save()
        productB.save()
        # Create inventory using products Test and Test2
        inventoryA = createInventory(productA, 'AA', 100)
        inventoryB = createInventory(productB, 'BB', 100)
        inventoryA.save()
        inventoryB.save()
        # Create order with productA
        orderA = createOrder(productA, 100)
        orderA.save()
        
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Inventory.objects.count(), 2)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.get(pk=1).get_status_display(), 'Pending')
        self.assertEqual(Pending_Stock.objects.count(), 1)
        self.assertEqual(Pending_Stock.objects.get(pk=1).quantity, 100)
        print("+++End test_objects_successfully_added++++")
    
    # Check created objects exist in database
    def test_objects_successfully_deleted(self):
        print("++++Start test_objects_successfully_deleted+++")
        # Create product Test and Test2
        productA = createProductA()
        productB = createProductB()
        productA.save()
        productB.save()
        # Create inventory using products Test and Test2
        inventoryA = createInventory(productA, 'AA', 100)
        inventoryA2 = createInventory(productA, 'AA2', 100)
        inventoryB = createInventory(productB, 'BB', 100)
        inventoryA.save()
        inventoryB.save()
        # Create order with productA
        orderA = createOrder(productA, 100)
        orderA.save()
        
        self.assertEqual(Pending_Stock.objects.count(), 1)
        
        delete_order(orderA, orderA.order_number)
        
        self.assertEqual(Pending_Stock.objects.count(), 0)
        
        # Create order with productA, delete then order again
        orderA = createOrder(productA, 50)
        orderA.save()

        self.assertEqual(Pending_Stock.objects.count(), 1)
        
        delete_order(orderA, orderA.order_number)
        
        self.assertEqual(Pending_Stock.objects.count(), 0)
        
        orderA = createOrder(productA, 100)
        orderA.save()
        
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Pending_Stock.objects.count(), 1)
        self.assertEqual(Pending_Stock.objects.get(order_number=orderA.order_number).quantity, 100)
        print("+++End test_objects_successfully_deleted++++")
    
    def test_order_insufficient_quantity(self):
        
        print("+++Start test_order_insufficient_quantity+++")
        # Create product Test and Test2
        productA = createProductA()
        productB = createProductB()
        productA.save()
        productB.save()
        # Create inventory using products Test and Test2
        inventoryA = createInventory(productA, 'AA', 100)
        inventoryB = createInventory(productB, 'BB', 100)
        inventoryA.save()
        inventoryB.save()
        # Create order with productA
        orderA = createOrder(productA, 150)
        if orderA != "Insufficient stock. " and orderA != "Insufficient stock. Stock held. ":
            orderA.save()
        
        self.assertEqual(orderA, "Insufficient stock. ")
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Inventory.objects.count(), 2)
        self.assertEqual(Order.objects.count(), 0)
        print("+++End test_order_insufficient_quantity+++")

    def test_order_insufficient_quantity_stock_held(self):
    
        print("+++Start test_order_insufficient_quantity+++")
        # Create product Test and Test2
        productA = createProductA()
        productB = createProductB()
        productA.save()
        productB.save()
        # Create inventory using products Test and Test2
        inventoryA = createInventory(productA, 'AA', 100)
        inventoryB = createInventory(productB, 'BB', 100)
        inventoryA.save()
        inventoryB.save()
        # Create order with productA
        orderA = createOrder(productA, 50)
        if orderA != "Insufficient stock. " and orderA != "Insufficient stock. Stock held. ":
            orderA.save()
        # Create order 2 with productA
        orderB = createOrder(productA, 100)
        if orderB != "Insufficient stock. " and orderB != "Insufficient stock. Stock held. ":
            orderB.save()

        self.assertEqual(orderB, "Insufficient stock. Stock held. ")
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Inventory.objects.count(), 2)
        self.assertEqual(Order.objects.count(), 1)
        print("+++End test_order_insufficient_quantity+++")

    def test_multi_inventory_order(self):
        
        print("+++Start test_multi_inventory_order+++")
        # Clear objects
        Product.objects.all().delete()
        Inventory.objects.all().delete()
        Order.objects.all().delete()
        Pending_Stock.objects.all().delete()
        
        # Create product Test and Test2
        productA = createProductA()
        productB = createProductB()
        productA.save()
        productB.save()
        # Create inventory using products Test and Test2
        inventoryA = createInventory(productA, 'AA', 100)
        inventoryA2 = createInventory(productA, 'AA2', 100)
        inventoryB = createInventory(productB, 'BB', 100)
        inventoryA.save()
        inventoryA2.save()
        inventoryB.save()
        # Create order with productA
        orderA = createOrder(productA, 150)
        orderA.save()

        self.assertEqual(Pending_Stock.objects.count(), 2)
        self.assertEqual(orderA.stock, "1, 2, ")
        
        p_stock1 = Pending_Stock.objects.get(id=1)
        p_stock2 = Pending_Stock.objects.get(id=2)
        
        self.assertEqual(p_stock1.quantity, 86)
        self.assertEqual(p_stock2.quantity, 64)
        print("+++End test_multi_inventory_order+++")

    def test_multi_inventory_order_with_pending_stock(self):
    
        print("++++Start test_multi_inventory_order_with_pending_stock++++")
        # Clear objects
        Product.objects.all().delete()
        Inventory.objects.all().delete()
        Order.objects.all().delete()
        Pending_Stock.objects.all().delete()
        
        # Create product Test and Test2
        productA = createProductA()
        productB = createProductB()
        productA.save()
        productB.save()
        # Create inventory using products Test and Test2
        inventoryA = createInventory(productA, 'AA', 100)
        inventoryA2 = createInventory(productA, 'AA2', 100)
        inventoryB = createInventory(productB, 'BB', 100)
        inventoryA.save()
        inventoryA2.save()
        inventoryB.save()
        # Create order with productA
        orderA = createOrder(productA, 150)
        orderA.save()
        
        self.assertEqual(Pending_Stock.objects.count(), 2)
        self.assertEqual(orderA.stock, "1, 2, ")
        
        p_stock1 = Pending_Stock.objects.get(id=1)
        p_stock2 = Pending_Stock.objects.get(id=2)
        
        self.assertEqual(p_stock1.quantity, 86)
        self.assertEqual(p_stock2.quantity, 64)
        self.assertEqual(Order.objects.count(), 1)
        
        # Create another order for productA while there is pending stock held
        orderB = createOrder(productA, 10)
        orderB.save()
        
        self.assertEqual(Pending_Stock.objects.get(id=3).quantity, 10)
        self.assertEqual(Pending_Stock.objects.get(id=3).inventory.lot_number, '123AA')
        self.assertEqual(Order.objects.count(), 2)
        
        # Create another order for productA with multiple pending stock held
        orderC = createOrder(productA, 20)
        orderC.save()

        self.assertEqual(Pending_Stock.objects.get(id=4).quantity, 4)
        self.assertEqual(Pending_Stock.objects.get(id=4).inventory.lot_number, '123AA')
        self.assertEqual(Pending_Stock.objects.get(id=5).quantity, 16)
        self.assertEqual(Pending_Stock.objects.get(id=5).inventory.lot_number, '123AA2')
        self.assertEqual(Order.objects.count(), 3)
        
        print("+++End test_multi_inventory_order_with_pending_stock+++")