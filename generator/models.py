# -*- coding: utf-8 -*-

# Create your models here.
import os
import re
from django.conf import settings
from django.db.models import CharField, ForeignKey, PositiveIntegerField, Model

import mysql.connector
from mysql.connector import errorcode

import sqlite3
import json
import random
from lxml import etree

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

        root = etree.Element('data')

        for record in data:
            # create XML
            rec = etree.Element('record')
            i = 0
            for field in structure:

                dat = etree.Element(field)
                dat.text = unicode(record[i])

                rec.append(dat)

                i += 1
            root.append(rec)


            count += 1

            if count >= number:
                break

        # pretty string
        s = etree.tostring(root, pretty_print=True)
        f.write(s)

    f.close()

def generate_sql_file(filepath, data, structure=[], number=100):

    if os.path.isfile(filepath):
        os.remove(filepath)
    try:
        conn = sqlite3.connect(filepath)
        c = conn.cursor()

    except sqlite3.Error as e:
        print "Connection to database could not be established"

    if len(data) > 0:

        count = 0
        if len(structure) != len(data[0]):
            structure = []
            for i in range(len(data[0])):
                structure.append('field_%d' % i)

        # Create table
        st = []
        ch = []

        for field in structure:
            st.append('%s VARCHAR(60)' % field)
            ch.append('?')
        st_res = ", ".join(st)
        ch_res = ", ".join(ch)

        create_str = 'CREATE TABLE ADRESY (%s)' % st_res

        c.execute(create_str)

        for record in data:
            # Insert a row of data
            c.execute("INSERT INTO ADRESY VALUES (%s)" %ch_res, tuple(record))

            # Save (commit) the changes
            conn.commit()

            count += 1

            if count >= number:
                break

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

def generate_json_file(filepath, data, structure=[], number=100):

    f = open(filepath, 'w')

    if len(data) > 0:

        count = 0
        if len(structure) != len(data[0]):
            structure = []
            for i in range(len(data[0])):
                structure.append('field_%d' % i)

        records = []

        for rec in data:
            d = {}
            for i in range(len(rec)):
                d[structure[i]] = rec[i]

            records.append(d)
            count += 1

            if count >= number:
                break

        f.write(json.dumps(records))

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
    miejscowosci = options_list[3]

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

    #wygenerowanie struktury wyjsciowej
    struktura_pom = {}
    pola_mysql_pom = {}
    where_mysql_txt = []

    if wojewodztwa[0] >= 0:
        struktura_pom[wojewodztwa[0]] = 'wojewodztwo'
        pola_mysql_pom[wojewodztwa[0]] = 'w.nazwa as wojewodztwo'

    #wojewodzctwa
    where_mysql_txt_pom = ''
    if len(wojewodztwa) == 2 and len(wojewodztwa[1]) > 0 and wojewodztwa[1][0] not in unicode('Wszystkie'):
        where_mysql_txt_pom += 'w.nazwa in ('
        for i in range(len(wojewodztwa[1])):
            if i < len(wojewodztwa[1])-1:
                where_mysql_txt_pom += '"%s", ' % unicode(wojewodztwa[1][i]).encode('utf-8')
            else:
                where_mysql_txt_pom += '"%s"' % unicode(wojewodztwa[1][i]).encode('utf-8')

        where_mysql_txt_pom += ')'

    if len(where_mysql_txt_pom) > 0:
        where_mysql_txt.append(where_mysql_txt_pom)
    #powiaty
    where_mysql_txt_pom = ''
    if len(powiaty) == 2 and len(powiaty[1]) > 0 and powiaty[1][0] not in unicode('Wszystkie'):
        where_mysql_txt_pom += 'p.nazwa in ('
        for i in range(len(powiaty[1])):
            if i < len(powiaty[1])-1:
                where_mysql_txt_pom += '"%s", ' % unicode(powiaty[1][i]).encode('utf-8')
            else:
                where_mysql_txt_pom += '"%s"' % unicode(powiaty[1][i]).encode('utf-8')

        where_mysql_txt_pom += ')'


    if len(where_mysql_txt_pom) > 0:
        where_mysql_txt.append(where_mysql_txt_pom)

    #gminy
    where_mysql_txt_pom = ''
    if len(gminy) == 2 and len(gminy[1]) > 0 and gminy[1][0] not in unicode('Wszystkie'):
        where_mysql_txt_pom += 'g.nazwa in ('
        for i in range(len(gminy[1])):
            if i < len(gminy[1])-1:
                where_mysql_txt_pom += '"%s", ' % unicode(gminy[1][i]).encode('utf-8')
            else:
                where_mysql_txt_pom += '"%s"' % unicode(gminy[1][i]).encode('utf-8')

        where_mysql_txt_pom += ')'

    if len(where_mysql_txt_pom) > 0:
        where_mysql_txt.append(where_mysql_txt_pom)

    #miejscowosci
    where_mysql_txt_pom = ''
    if len(miejscowosci) == 2 and len(miejscowosci[1]) > 0 and miejscowosci[1][0] not in unicode('Wszystkie'):
        where_mysql_txt_pom += 'miej.nazwa in ('
        for i in range(len(miejscowosci[1])):
            if i < len(miejscowosci[1])-1:
                where_mysql_txt_pom += '"%s", ' % unicode(miejscowosci[1][i]).encode('utf-8')
            else:
                where_mysql_txt_pom += '"%s"' % unicode(miejscowosci[1][i]).encode('utf-8')

        where_mysql_txt_pom += ')'

    if len(where_mysql_txt_pom) > 0:
        where_mysql_txt.append(where_mysql_txt_pom)

    where_mysql = ''
    if len(where_mysql_txt) > 0:
        where_mysql ='WHERE ' + '\nAND '.join(where_mysql_txt)

    if powiaty[0] >= 0:
        struktura_pom[powiaty[0]] = 'powiat'
        pola_mysql_pom[powiaty[0]] = 'p.nazwa as powiat'

    if gminy[0] >= 0:
        struktura_pom[gminy[0]] = 'gmina'
        pola_mysql_pom[gminy[0]] = 'g.nazwa as gmina'

    if miejscowosci[0] >= 0:
        struktura_pom[miejscowosci[0]] = 'miejscowosc'
        pola_mysql_pom[miejscowosci[0]] = 'miej.nazwa as miejscowosc'

    if kod >= 0:
        struktura_pom[kod] = 'kod_pocztowy'
        pola_mysql_pom[kod] = 'kod as kod_pocztowy'

    if nrdomu >= 0:
        struktura_pom[nrdomu] = 'nr_domu'

    if ulica >= 0:
        struktura_pom[ulica] = 'ulica'
        pola_mysql_pom[ulica] = 'ulica'

    rek_struktura = []
    pola_mysql = []
    for key in sorted(struktura_pom):
        rek_struktura.append(struktura_pom[key])
        if key in pola_mysql_pom:
            pola_mysql.append(pola_mysql_pom[key])

    pola_mysql_txt = ', '.join(pola_mysql)

    zapytanie_mysql = 'SELECT %s from generator_adresset a ' \
                      '\nJOIN generator_miejset miej on miej.id = a.miej_id ' \
                      '\nJOIN generator_gmset g on g.id = miej.gm_id ' \
                      '\nJOIN generator_powset p on p.id = g.pow_id ' \
                      '\nJOIN generator_wojset w on w.id = p.woj_id' \
                      '\n%s LIMIT %d;' % (pola_mysql_txt, where_mysql, ilosc)

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

        cursor.execute(zapytanie_mysql)

        result = cursor.fetchall()

    if 'nr_domu' in rek_struktura:

        count = 0
        result_nr_domu = []
        index_nr_domu = int(rek_struktura.index('nr_domu'))

        for r in result:
            max_nr_domu = random.randint(1, 1000)
            delta_nr_domu = random.randint(1, 4) + 1
            i = delta_nr_domu
            while i < max_nr_domu:
                rr = list(r)
                rr.insert(index_nr_domu, i)
                result_nr_domu.append(rr)
                i += delta_nr_domu

        result = result_nr_domu

    filename = str(req_dict['file_name'][0])
    if filename is None or len(filename) == 0:
        filename = 'output'

    if filetype == 'csv':
        filename += '.csv'
        filepath = settings.MEDIA_ROOT + os.sep + filename
        generate_csv_file(filepath, result, ilosc)

    elif filetype == 'xml':
        filename += '.xml'
        filepath = settings.MEDIA_ROOT + os.sep + filename
        generate_xml_file(filepath, result, rek_struktura, ilosc)

    elif filetype == 'sql':
        filename += '.sqlite3'
        filepath = settings.MEDIA_ROOT + os.sep + filename
        generate_sql_file(filepath, result, rek_struktura, ilosc)

    elif filetype == 'json':
        filename += '.json'
        filepath = settings.MEDIA_ROOT + os.sep + filename
        generate_json_file(filepath, result, rek_struktura, ilosc)

    else:
        filename += '.txt'
        filepath = settings.MEDIA_ROOT + os.sep + filename
        generate_text_file(filepath, result, ilosc)
    '''
    f = open(filepath+'2', 'w')
    #test:
    f.write(str(wojewodztwa) +'\n')
    f.write(str(powiaty)+'\n')
    f.write(str(gminy)+'\n')
    f.write(str(miejscowosci)+'\n')
    f.write(str(ulica)+'\n')
    f.write(str(kod)+'\n')
    f.write(str(nrdomu)+'\n')
    f.write(str(rek_struktura)+'\n')
    f.write(pola_mysql_txt +'\n')
    f.write(zapytanie_mysql +'\n')
    f.write(str(index_nr_domu) +'\n')
    f.write(str(result) +'\n')
    f.write(str(result[0][:int(index_nr_domu)-1]) +'\n')
    f.write(str(result[0][int(index_nr_domu):]) +'\n')

    f.write(str(max_nr_domu) +'\n')
    f.write(str(delta_nr_domu) +'\n')
    f.close()

    '''

    return str(filename)

