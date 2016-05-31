from __future__ import unicode_literals

from django.db import models

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    sm_lot_number = models.CharField(max_length=200)
    def __str__(self):
        return self.product_name + " - " + self.sm_lot_number

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    add_date = models.DateTimeField('date added')
    lot_number = models.CharField(max_length=200)
    quantity = models.IntegerField(default=0)
    location = models.CharField(max_length=100)
    pieces = models.IntegerField(default = 0)
    notes = models.CharField(max_length=200)
    def __str__(self):
        return self.product.product_name + " - " + str(self.lot_number) + " -quantity: " + str(self.quantity) + " -location: " + self.location

