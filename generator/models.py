# -*- coding: utf-8 -*-

# Create your models here.
import os
import re
from django.conf import settings
from django.db.models import CharField, ForeignKey, PositiveIntegerField, Model

import mysql.connector
from mysql.connector import errorcode

from lxml import etree



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
    nazwa = CharField(max_length=60, verbose_name="Nazwa miejscowosci")
    gm = ForeignKey(GmSet) #gmid

    @staticmethod
    def choose_miej(req):


        gms = req[2][1]

        if gms[0] == u'Wszystkie':
            pow = req[1][1]

            if pow[0] == u'Wszystkie':
                woj = req[0][1]

                if woj[0] == u'Wszystkie':
                    m_set = MiejSet.objects.values_list('nazwa', flat=True).distinct()
                else:

                    woj_ids = WojSet.objects.filter(nazwa__in=woj).values_list('id', flat=True)
                    pow_ids = PowSet.objects.filter(woj__in=woj_ids).values_list('id', flat=True)
                    gm_ids = GmSet.objects.filter(pow__in=pow_ids).values_list('id', flat=True)
                    m_set = MiejSet.objects.filter(gm__in=gm_ids).values_list('nazwa', flat=True)

            else:

                pow_ids = PowSet.objects.filter(nazwa__in=pow).values_list('id', flat=True)
                gm_ids = GmSet.objects.filter(pow__in=pow_ids).values_list('id', flat=True)
                m_set = MiejSet.objects.filter(gm__in=gm_ids).values_list('nazwa', flat=True)

        else:

            gm_ids = GmSet.objects.filter(nazwa__in=gms).values_list('id', flat=True)
            m_set = MiejSet.objects.filter(gm__in=gm_ids).values_list('nazwa', flat=True)


        return m_set

class AdresSet(Model):
    ulica = CharField(max_length=100, verbose_name="Nazwa ulicy")
    kod = CharField(max_length=6, verbose_name="Kod pocztowy")
    miej = ForeignKey(MiejSet) #miejid

    @staticmethod
    def choose_adres(req):

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
                pom = [int(w)]
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
            if req_dict['woj_order'][0].lstrip("-+").isdigit():
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
            if req_dict['pow_order'][0].lstrip("-+").isdigit():
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

        #wojewodztwa i powiaty
        if 'options' in req_dict:

            data_list = str_to_list(req_dict['options'][0])

        else:
            data_list = [[-1, [u'Wszystkie']], [-1, [u'Wszystkie']]]

        gpom=[-1]
        if req_dict.has_key('gm_on_off') and req_dict.has_key('gm_order'):
            if req_dict['gm_order'][0].lstrip("-+").isdigit():
                gpom = [int(req_dict['gm_order'][0])]

        if req_dict.has_key('gm'):
            tmp = req_dict['gm']

            if 'all' in tmp:
                gpom.append([u'Wszystkie'])
            else:
                gpom.append(tmp)
        else:
            gpom.append([u'Wszystkie'])

        data_list.append(gpom)

        ret = data_list

    elif step == 5:

        #wojewodztwa, powiaty i gminy
        if 'options' in req_dict:

            data_list = str_to_list(req_dict['options'][0])

        else:
            data_list = [[-1, [u'Wszystkie']], [-1, [u'Wszystkie']], [-1, [u'Wszystkie']]]

        mpom=[-1]
        if req_dict.has_key('miej_on_off') and req_dict.has_key('miej_order'):
            if req_dict['miej_order'][0].lstrip("-+").isdigit():
                mpom = [int(req_dict['miej_order'][0])]

        if req_dict.has_key('miej'):
            tmp = req_dict['miej']

            if 'all' in tmp:
                mpom.append([u'Wszystkie'])
            else:
                mpom.append(tmp)
        else:
            mpom.append([u'Wszystkie'])

        data_list.append(mpom)

        ret = data_list


    return ret

def generate_text_file(filepath, data, number=100, separator='|'):

    f = open(filepath, 'w')
    count = 0
    for record in data:
        dlugosc = len(record)
        for i in range(dlugosc):
            d = unicode(record[i])
            f.write(d.encode("utf-8"))
            if i < dlugosc - 1:
                f.write(separator)

        count += 1

        f.write("\n")
        if count >= number:
            break

    f.close()

def generate_csv_file(filepath, data, number=100):

    #checking file name
    generate_text_file(filepath, data, number, ',')

def generate_xml_file(filepath, data, structure=[], number=100):

    f = open(filepath, 'w')

    if len(data) > 0:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        count = 0
        if len(structure) != len(data[0]):
            structure = []
            for i in range(len(data[0])):
                structure.append('field_%d' % i)

        for record in data:
            # create XML
            rec = etree.Element('record')
            i = 0
            for field in structure:
                d = etree.Element(field)
                d.text = unicode(record[i])

                rec.append(d)
                i += 1

            # pretty string
            s = etree.tostring(rec, pretty_print=True)
            f.write(s)

            count += 1

            if count >= number:
                break



    f.close()




def generate_file(req):

    req_dict = dict(req)
    #opcje
    if 'options' in req_dict:
        options_list = str_to_list(req_dict['options'][0])
    else:
        options_list = [[-1, [u'Wszystkie']], [-1, [u'Wszystkie']], [-1, [u'Wszystkie']], [-1, [u'Wszystkie']]]


    wojewodztwa = options_list[0]
    powiaty = options_list[1]
    gminy = options_list[2]
    miejscowosc = options_list[3]

    if 'ulica_on_off' in req_dict and 'ulica_order' in req_dict:
        ulica = int(req_dict['ulica_order'][0])
    else:
        ulica = -1

    if 'nrdomu_on_off' in req_dict and 'nrdomu_order' in req_dict:
        nrdomu = int(req_dict['nrdomu_order'][0])
    else:
        nrdomu = -1

    if 'kod_on_off' in req_dict and 'kod_order' in req_dict:
        kod = int(req_dict['kod_order'][0])
    else:
        kod = -1


    if 'ilosc' in req_dict and req_dict['ilosc'][0].lstrip("-+").isdigit():
        ilosc = int(req_dict['ilosc'][0])
    else:
        ilosc = 0

    if 'group1' in req_dict:
        filetype = req_dict['group1'][0]
    else:
        filetype = 'txt'


    try:
        db = mysql.connector.connect(host='mysql.server',
                                    port=3306,
                                    user='jsb',
                                    password='Testerki@1',
                                    database='jsb$ADRESY')


    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:

        # prepare a cursor object using cursor() method
        cursor = db.cursor()

        cursor.execute("SELECT id, nazwa from generator_wojset; ")

        result = cursor.fetchall()

    filename = str(req_dict[FILENAME_FIELD][0])
    if filename is None or len(filename) == 0:
        filename = 'output'

    if filetype == 'csv':
        filename += '.csv'
        filepath = settings.MEDIA_ROOT + os.sep + filename
        generate_csv_file(filepath, result, ilosc)

    elif filetype == 'xml':
        filename += '.xml'
        filepath = settings.MEDIA_ROOT + os.sep + filename
        generate_xml_file(filepath, result, [])

    else:
        filename += '.txt'
        filepath = settings.MEDIA_ROOT + os.sep + filename
        generate_text_file(filepath, result, ilosc)



    return str(filename)

