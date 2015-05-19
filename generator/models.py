# -*- coding: utf-8 -*-

# Create your models here.
import os
import re
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

class PowSet(Model):
    nazwa = CharField(max_length=60, verbose_name="Nazwa powiatu")
    woj = ForeignKey(WojSet) #wojid

    @staticmethod
    def choose_pow(req):

        woj = req[1][0]

        if woj == u'Wszystkie':
            pow_set = PowSet.objects.values_list('nazwa', flat=True).distinct()
        else:

            wojs = list(req[1])
            woj_ids = WojSet.objects.filter(nazwa__in=wojs).values_list('id', flat=True)

            pow_set = PowSet.objects.filter(woj__in=woj_ids).values_list('nazwa', flat=True)

        return pow_set

class GmSet(Model):
    nazwa = CharField(max_length=60, verbose_name="Nazwa gminy")
    pow = ForeignKey(PowSet) #powid

    @staticmethod
    def choose_gm(req):

        pows = req[1][1]

        if pows[0] == u'Wszystkie':
            wojs = req[0][1]

            if wojs[0] == u'Wszystkie':
                gm_set = GmSet.objects.values_list('nazwa', flat=True).distinct()
            else:
                woj_ids = WojSet.objects.filter(nazwa__in=wojs).values_list('id', flat=True)
                pow_ids = PowSet.objects.filter(woj__in=woj_ids).values_list('id', flat=True)
                gm_set = GmSet.objects.filter(pow__in=pow_ids).values_list('nazwa', flat=True)
        else:
            pow_ids = PowSet.objects.filter(nazwa__in=pows).values_list('id', flat=True)
            gm_set = GmSet.objects.filter(pow__in=pow_ids).values_list('nazwa', flat=True)

        return gm_set

class MiejSet(Model):
    nazwa = CharField(max_length=60, verbose_name="Nazwa Miejscowosci")
    gm = ForeignKey(GmSet) #gmid

    @staticmethod
    def choose_miej(req):
        '''
        pows = req[1][1]

        if pows[0] == u'Wszystkie':
            wojs = req[0][1]

            if wojs[0] == u'Wszystkie':
                gm_set = GmSet.objects.values_list('nazwa', flat=True).distinct()
            else:
                woj_ids = WojSet.objects.filter(nazwa__in=wojs).values_list('id', flat=True)
                pow_ids = PowSet.objects.filter(woj__in=woj_ids).values_list('id', flat=True)
                gm_set = GmSet.objects.filter(pow__in=pow_ids).values_list('nazwa', flat=True)
        else:
            pow_ids = PowSet.objects.filter(nazwa__in=pows).values_list('id', flat=True)
            gm_set = GmSet.objects.filter(pow__in=pow_ids).values_list('nazwa', flat=True)
        '''
        return req


def convert_to_unicode(word):

    to_rem = []

    for i in range(len(word)):
        if word[i] == 'u' and i+4 < len(word):
            to_rem_pom = word[i: i+5]
            charcode = to_rem_pom[1:5]

            matchObj = re.match( r'[A-Fa-f0-9]{4}', charcode, re.M | re.I)

            if matchObj:
                to_rem.append(to_rem_pom)

    for rem in to_rem:
        word = word.replace(rem, unichr(int(rem[1:5], 16)))
    return word


def str_to_list(strlist):
    ret = []

    pom = []
    pom2 = []
    slist = strlist.replace('[','').replace(']','').replace(' ','').replace("\\","").split(',')

    for w in slist:
        if w.lstrip("-+").isdigit():
            if len(pom) > 0:
                pom.append(pom2)
                ret.append(pom)
                pom = []
                pom2 = []
            else:
                pom.append(int(w))
        else:
            nazwa = w[2:len(w)-1]
            pom2.append(convert_to_unicode(nazwa))

    if len(pom) > 0:
        pom.append(pom2)
        if len(ret) > 0:
            ret.append(pom)
        else:
            ret = pom

    return ret



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
                ret.append([u'Wszystkie'])
            else:
                ret.append(tmp)
        else:
            ret.append([u'Wszystkie'])

    elif step == 3:
        ret = [-1]

        #wojewodztwa
        if 'options' in req_dict:
            options_list = str_to_list(req_dict['options'][0])
        else:
            options_list = [-1, [u'Wszystkie']]

        data_list = [options_list]


        ppom=[-1]
        if req_dict.has_key('pow_on_off') and req_dict.has_key('pow_order'):
            if req_dict['pow_order'][0].isdigit():
                ppom = [int(req_dict['pow_order'][0])]

        if req_dict.has_key('pow'):
            tmp = req_dict['pow']

            if 'all' in tmp:
                ppom.append([u'Wszystkie'])
            else:
                ppom.append(tmp)
        else:
            ppom.append([u'Wszystkie'])

        data_list.append(ppom)


        ret = data_list

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

