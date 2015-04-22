# -*- coding: utf-8 -*-

# Create your models here.
import os
from django.conf import settings
from django.db.models import CharField, Model



FILENAME_FIELD = 'file_name'
WOJ_FIELD = 'woj'

#Tabela wojewodztwa
class AdresySet(Model):
    name = CharField(max_length=60, verbose_name="Województwo")

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)

    @staticmethod
    def choose_woj():

        woj_set=[ 'Lodzkie' , 'Podkarpackie', 'Malopolskie']

        return woj_set

    @staticmethod
    def choose_pow(req):

        woj = req[1][0]
        if woj == 'Wszystkie':
            return [ 'piotrkowski' , 'lodzki', 'rzeszowski' , 'lancucki', 'jaroslawski', 'gorlicki']
        pow_set= {'Lodzkie': [ 'piotrkowski' , 'lodzki'],
                  'Podkarpackie': [ 'rzeszowski' , 'lancucki', 'jaroslawski'],
                  'Malopolskie': ['gorlicki']
                  }


        return pow_set[woj]

    @staticmethod
    def choose_gm(req):

        gm_set=[ 'rzeszowski' , 'gorlicki', 'piotrkowski']

        return gm_set

def get_option_value(req, step):

    req_dict = dict(req)

    ret = []

    if step == 2:
        #wojewodzctwo ON/OFF
        ret = [-1]

        if req_dict.has_key('woj_on_off') and req_dict.has_key('woj_order'):
            if req_dict['woj_order'][0].isdigit():
                ret = [int(req_dict['woj_order'][0])]

        if req_dict.has_key('woj'):
            tmp = req_dict['woj']

            if 'all' in tmp:
                ret.append(['Wszystkie'])
            else:
                ret.append(tmp)
        else:
            ret.append(['Wszystkie'])

    elif step == 3:
        ret = req

    return ret


def generate_file(req):

    filename = str(req.get(FILENAME_FIELD))

    if filename is None or len(filename) == 0:
        filename = 'workfile.txt'

    filepath = settings.MEDIA_ROOT + os.sep + filename



    f = open(filepath, 'w')
    f.write('This is a test\n' + str(req))
    f.close()


    return str(filename)
