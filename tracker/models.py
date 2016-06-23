from __future__ import unicode_literals
import os
from django.db import models

def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)

class Product(models.Model):
    DEXTROSE = 'dex'
    GUM = 'gum'
    PANNED_SUGAR = 'psg'
    JAWBREAKER = 'jaw'
    CATEGORIES = (
                  (DEXTROSE, 'Pressed Dextrose'),
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
    def __str__(self):
        return self.product_name + " - " + self.sm_lot_number

class Inventory(models.Model):
    INVENTORY_THRESHOLD = 50
    NO_LABEL = 0
    HAS_LABEL = 1
    SOME_LABELS = 2
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField('date')
    quantity = models.IntegerField(default=0)
    client = models.CharField(max_length=100)
    notes = models.CharField(max_length=200)
    status = models.CharField(max_length=1, choices=STATUS, default=PENDING)
    def __str__(self):
        return quantity + " of " + self.product + " ordered by " + self.client + " on " + date + ". Additional Notes: " + notes
