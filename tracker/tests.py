from django.test import TestCase
from django.utils import timezone
from tracker.models import Product, Inventory

class ProductMethodTests(TestCase):

    def test_product_creation(self):
        product_name = 'Test'
        sm_lot_number = '100'
        weight = 100
        pieces = 10
        category = 'DEX'
        popular = 'Yes'
        product = Product(product_name=product_name,
                          sm_lot_number=sm_lot_number,
                          weight=weight,
                          pieces=pieces,
                          category=category,
                          popular=popular)
        self.assertEqual(product.__str__(), product_name + ' - ' + sm_lot_number)
        self.assertEqual(product.category, category)
        self.assertEqual(product.popular, popular)

class InventoryMethodTests(TestCase):

    def test_inventory_creation(self):
        product_name = 'Test'
        sm_lot_number = '100'
        weight = 100
        pieces = 10
        category = 'DEX'
        popular = 'Yes'
        product = Product(product_name=product_name,
                          sm_lot_number=sm_lot_number,
                          weight=weight,
                          pieces=pieces,
                          category=category,
                          popular=popular)
        add_date = timezone.now()
        lot_number = '123ab'
        quantity = 100
        location = 'warehouse'
        label = 0
        standard = 'Yes'
        dessicate = 'No'
        inventory = Inventory(product=product,
                              add_date=add_date,
                              lot_number=lot_number,
                              quantity=quantity,
                              location=location,
                              label=label,
                              standard=standard,
                              dessicate=dessicate,)
        self.assertEqual(inventory.__str__(), product.product_name + " - " + str(lot_number) + " -quantity: " + str(quantity) + " -location: " + location)
        self.assertEqual(inventory.add_date, add_date)
        self.assertEqual(inventory.get_label_display(), 'No Label')
        self.assertEqual(inventory.standard, 'Yes')
        self.assertEqual(inventory.dessicate, 'No')

class ObjectCreationTests(TestCase):

    # Check created objects exist in database
    def test_objects_successfully_added(self):

        # Create product Test and Test2
        product_name = 'Test'
        sm_lot_number = '100'
        weight = 100
        pieces = 10
        category = 'DEX'
        popular = 'Yes'
        Product.objects.create(product_name=product_name,
                               sm_lot_number=sm_lot_number,
                               weight=weight,
                               pieces=pieces,
                               category=category,
                               popular=popular)
        product_name = 'Test2'
        sm_lot_number = '101'
        weight = 50
        pieces = 20
        category = 'GUM'
        popular = 'No'
        Product.objects.create(product_name=product_name,
                               sm_lot_number=sm_lot_number,
                               weight=weight,
                               pieces=pieces,
                               category=category,
                               popular=popular)
        product = Product.objects.get(product_name='Test')
        add_date = timezone.now()
        lot_number = '123ab'
        quantity = 100
        location = 'warehouse'
        label = 0
        standard = 'Yes'
        dessicate = 'No'
        # Create inventory using products Test and Test2
        Inventory.objects.create(product=product,
                                 add_date=add_date,
                                 lot_number=lot_number,
                                 quantity=quantity,
                                 location=location,
                                 label=label,
                                 standard=standard,
                                 dessicate=dessicate,)
        product = Product.objects.get(product_name='Test2')
        add_date = timezone.now()
        lot_number = '321ab'
        quantity = 50
        location = 'warehouse2'
        label = 1
        standard = 'No'
        dessicate = 'Yes'
        Inventory.objects.create(product=product,
                                 add_date=add_date,
                                 lot_number=lot_number,
                                 quantity=quantity,
                                 location=location,
                                 label=label,
                                 standard=standard,
                                 dessicate=dessicate,)
        
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Inventory.objects.count(), 2)

