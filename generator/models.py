# -*- coding: utf-8 -*-

# Create your models here.
import os
from django.conf import settings
from django.db.models import CharField, ForeignKey, PositiveIntegerField, Model



FILENAME_FIELD = 'file_name'
WOJ_FIELD = 'woj'

#Tabela wojewodztwa
class WojSet(Model):
    nazwa = CharField(max_length=60, verbose_name="Nazwa województwa")

    @staticmethod
    def choose_woj():

        woj_set = WojSet.objects.values_list('nazwa', flat=True).distinct()
        return woj_set

    @staticmethod
    def choose_gm(req):

        gm_set=[ 'rzeszowski' , 'gorlicki', 'piotrkowski']

        return gm_set

class PowSet(Model):
    nazwa = CharField(max_length=60, verbose_name="Nazwa powiatu")
    woj = ForeignKey(WojSet) #wojid

    @staticmethod
    def choose_pow(req):

        woj = req[1][0]
        pow_set = ["test"]
        if woj == 'Wszystkie':
            pow_set = PowSet.objects.values_list('nazwa', flat=True).distinct()
        else:

            wojs = list(req[1])
            woj_ids = WojSet.objects.filter(nazwa__in=wojs).values_list('id', flat=True)

            pow_set = PowSet.objects.filter(woj__in=woj_ids).values_list('nazwa', flat=True)

        return pow_set



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
        ret = [-1]

        #wojewodztwa
        if req_dict.has_key('options'):
            options_list = list(req_dict['options'])
        else:
            options_list = [[-1, ['Wszystkie']]]

        ppom=[-1]
        if req_dict.has_key('pow_on_off') and req_dict.has_key('pow_order'):
            if req_dict['pow_order'][0].isdigit():
                ppom = [int(req_dict['pow_order'][0])]

        if req_dict.has_key('pow'):
            tmp = req_dict['pow']

            if 'all' in tmp:
                ppom.append('Wszystkie')
            else:
                ppom.append(tmp)
        else:
            ppom.append('Wszystkie')


        ret = ppom

    elif step == 4:
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
