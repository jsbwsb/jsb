# Create your models here.
import os
from django.conf import settings

FILENAME_FIELD = 'file_name'


def generate_file(req):

    filename = str(req.get(FILENAME_FIELD))

    if filename is None or len(filename) == 0:
        filename = 'workfile.txt'

    filepath = settings.MEDIA_ROOT + os.sep + filename



    f = open(filepath, 'w')
    f.write('This is a test\n' + str(req))
    f.close()


    return str(filename)

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