from __future__ import unicode_literals

from django.db import models

class Product(models.Model):
    DEXTROSE = 'DEX'
    GUM = 'GUM'
    CATEGORIES = (
                  (DEXTROSE, 'Dextrose'),
                  (GUM, 'Gum'),)
    product_name = models.CharField(max_length=200)
    sm_lot_number = models.CharField(max_length=200)
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    pieces = models.IntegerField()
    category = models.CharField(max_length=3,choices=CATEGORIES,default=DEXTROSE)
    def __str__(self):
        return self.product_name + " - " + self.sm_lot_number

class Inventory(models.Model):
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
    standard = models.CharField(max_length=3)
    dessicate = models.CharField(max_length=3)
    notes = models.CharField(max_length=200)
    def __str__(self):
        return self.product.product_name + " - " + str(self.lot_number) + " -quantity: " + str(self.quantity) + " -location: " + self.location

