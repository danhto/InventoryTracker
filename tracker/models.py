from __future__ import unicode_literals
import os, datetime
from django.db import models
from django.utils import timezone

def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)

class Product(models.Model):
    KG_TO_LBS_CONVERSION = 2.20462
    DEXTROSE = 'dex'
    GUM = 'gum'
    PANNED_SUGAR = 'psg'
    JAWBREAKER = 'jaw'
    CATEGORIES = ((DEXTROSE, 'Pressed Dextrose'),
                  (GUM, 'Bubble Gum'),
                  (PANNED_SUGAR, 'Panned Sugar'),
                  (JAWBREAKER, 'Jawbreaker'),)
    product_name = models.CharField(max_length=200)
    sm_lot_number = models.CharField(max_length=200)
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    pieces = models.IntegerField()
    category = models.CharField(max_length=3,choices=CATEGORIES,default=DEXTROSE)
    popular = models.CharField(max_length=3,default='No')
    photo = models.FileField(upload_to=get_image_path, blank=True, null=True)
    def get_pounds(self):
        return "{0:.2f}".format(Product.KG_TO_LBS_CONVERSION * float(self.weight))
    def __str__(self):
        return self.product_name
    # compares two product objects for equality based on product_name and sm_lot_number
    def __cmp__(self, other):
        return str(self.product_name) == str(other.product_name) and str(self.sm_lot_number) == str(other.sm_lot_number)

class Inventory(models.Model):
    INVENTORY_THRESHOLD = 50
    NO_LABEL = '0'
    HAS_LABEL = '1'
    SOME_LABELS = '2'
    LABEL_INFO = ((NO_LABEL, 'No Label'),
                  (HAS_LABEL, 'Has labels'),
                  (SOME_LABELS, 'Partially labelled'),)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    add_date = models.DateTimeField('date added')
    lot_number = models.CharField(max_length=200)
    quantity = models.IntegerField(default=0)
    location = models.CharField(max_length=100)
    label = models.CharField(max_length=1,choices=LABEL_INFO, default=NO_LABEL)
    standard = models.CharField(max_length=3, default='Yes')
    dessicate = models.CharField(max_length=3, default='No')
    notes = models.CharField(max_length=200)
    def __str__(self):
        return self.product.product_name + " - " + str(self.lot_number) + " -quantity: " + str(self.quantity) + " -location: " + self.location
    # checks if inventory is empty
    def no_stock(self):
        if (self.quantity < 1):
            return True
        else:
            return False
    # checks quantity of inventory if less than 50 return critical is true, if product is popular threshold is 100
    def critical_stock(self):
        if (self.product.popular == 'Yes'):
            self.INVENTORY_THRESHOLD = 100
        if (self.quantity < self.INVENTORY_THRESHOLD):
            return True
        else:
            return False

class Order(models.Model):
    PENDING = '0'
    APPROVED = '1'
    STATUS = ((PENDING, 'Pending'),
                  (APPROVED, 'Approved'),)
    order_number = models.IntegerField(default=1)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField('date')
    quantity = models.IntegerField(default=0)
    stock = models.CharField(max_length=100, default='')
    client = models.CharField(max_length=100)
    notes = models.CharField(max_length=200)
    status = models.CharField(max_length=1, choices=STATUS, default=PENDING)
    def __str__(self):
        return str(self.quantity) + " of " + self.product.product_name + " ordered by " + self.client + " on " + self.date.strftime("%D") + ". Additional Notes: " + self.notes
    # checks current status of order
    def is_approved(self):
        if self.status == Order.APPROVED:
            return True
        else:
            return False
    # alter the specified order from pending to approved and for associated pending stock objects
    def update_status(self):
        if self.status == Order.PENDING:
            self.status = Order.APPROVED
            for pstock in Pending_Stock.objects.all():
                if pstock.order_number == self.order_number:
                    pstock.status = self.status
            return True
        else:
            return False
    # returns a string based view of the stock field
    def get_stock(self):
        stocks = Pending_Stock.objects.all()
        inventories = []
        for stock in stocks:
            if stock.order_number == self.order_number:
                inventories.append("Lot Number: " + stock.inventory.lot_number + ", Quantity: " + str(stock.quantity))
        return inventories
    # checks order date to see if it's older than 7 days
    def order_age(self):
        date_order = self.date.strftime("%D").split("/")
        date_today = timezone.now().strftime("%D").split("/")
        date_difference = (int(date_today[0])*30 + int(date_today[1])) - (int(date_order[0])*30 + int(date_order[1]))
        if date_difference > 7 and self.get_status_display() == 'Pending':
            return True
        else:
            return False

class Pending_Stock(models.Model):
    order_number = models.IntegerField(default=1)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=10, default='Pending')
    def __str__(self):
        return self.quantity + " from " + self.inventory.lot_number