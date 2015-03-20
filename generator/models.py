# Create your models here.
import os


def generate_file(reg):
    f = open('workfile', 'w')
    f.write('This is a test\n')
    f.close()
    return "DZIALA GENERATE"

'''
# -*- coding: utf-8 -*-
from django.db import models



class AddressData(models.Model):
    postal_code = models.CharField(max_length=6, verbose_name="Kod pocztowy")

    def __str__(self):
        return str(self.postal_code)

    def __unicode__(self):
        return str(self.postal_code)

    def generate_file(self, request):
        return "TEST"
'''