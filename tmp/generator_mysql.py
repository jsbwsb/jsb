__author__ = 'Sylwia, Beata, Joanna'

import mysql.connector
from mysql.connector import errorcode

#addresses data file
DATA_FILE = 'przerobione_pna.txt'
NUMBER_OF_ROWS = 50

#indexes of the fields in data file
WOJ_FIELD_INDEX = 6
POW_FIELD_INDEX = 5
GM_FIELD_INDEX = 4
MIEJ_FIELD_INDEX = 1

KOD_FIELD_INDEX = 0
ULICA_FIELD_INDEX = 0

file = open(DATA_FILE, 'r')

#connecting to database
try:
    db = mysql.connector.connect(host='mysql.server',
                                    port=3306,
                                    user='jsb',
                                    password='Testerki@1',
                                    database='jsb$ADRESY')

    print "Connected to database: jsb$ADRESY"

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

    #delete all existing data
    cursor.execute("DELETE FROM generator_adresset;")
    cursor.execute("DELETE FROM generator_miejset;")
    cursor.execute("DELETE FROM generator_gmset;")
    cursor.execute("DELETE FROM generator_powset;")
    cursor.execute("DELETE FROM generator_wojset;")
    db.commit()

    #row counter
    i = 0

    woj = {}
    pow = {}
    gm = {}
    miej = {}
    adres = {}

    while i < NUMBER_OF_ROWS:
        line = file.readline()
        line_list = line.split("|")

        #inserting data to wojset
        if not woj.has_key(line_list[WOJ_FIELD_INDEX]):
            print str(line_list[WOJ_FIELD_INDEX]).strip()
            cursor.execute("INSERT INTO generator_wojset (nazwa) VALUES ('%s'); "
                           % str(line_list[WOJ_FIELD_INDEX]).strip())

            db.commit()

            cursor.execute("SELECT id from generator_wojset where nazwa = '%s'; "
                           % str(line_list[WOJ_FIELD_INDEX]).strip())

            result = cursor.fetchall()

            print "WOJID: %d" % int(result[0][0])

            woj[line_list[WOJ_FIELD_INDEX]] = int(result[0][0])

        wojID = woj[line_list[WOJ_FIELD_INDEX]]

        #inserting data to powset
        if not pow.has_key(line_list[POW_FIELD_INDEX]):
            cursor.execute("INSERT INTO generator_powset (nazwa, woj_id) VALUES ('%s', %d); "
                           % (str(line_list[POW_FIELD_INDEX]).strip(), wojID))

            db.commit()

            cursor.execute("SELECT id from generator_powset where nazwa = '%s'; "
                           % line_list[POW_FIELD_INDEX].strip())

            result = cursor.fetchall()

            print "POWID: %d" % int(result[0][0])

            pow[line_list[POW_FIELD_INDEX]] = int(result[0][0])

        powID = pow[line_list[POW_FIELD_INDEX]]

        #inserting data to gmset
        if not gm.has_key(line_list[GM_FIELD_INDEX]):
            cursor.execute("INSERT INTO generator_gmset (nazwa, pow_id) VALUES ('%s', %d); "
                           % (str(line_list[GM_FIELD_INDEX]).strip(), powID))

            db.commit()

            cursor.execute("SELECT id from generator_gmset where nazwa = '%s'; "
                           % line_list[GM_FIELD_INDEX].strip())

            result = cursor.fetchall()

            print "GMID: %d" % int(result[0][0])

            gm[line_list[GM_FIELD_INDEX]] = int(result[0][0])

        gmID = gm[line_list[GM_FIELD_INDEX]]

        #inserting data to miejset
        if not miej.has_key(line_list[MIEJ_FIELD_INDEX]):
            cursor.execute("INSERT INTO generator_miejset (nazwa, gm_id) VALUES ('%s', %d); "
                           % (str(line_list[MIEJ_FIELD_INDEX]).strip(), gmID))

            db.commit()

            cursor.execute("SELECT id from generator_miejset where nazwa = '%s'; "
                           % line_list[MIEJ_FIELD_INDEX].strip())

            result = cursor.fetchall()

            print "MIEJID: %d" % int(result[0][0])

            miej[line_list[MIEJ_FIELD_INDEX]] = int(result[0][0])

        miejID = miej[line_list[MIEJ_FIELD_INDEX]]

        #inserting data to adresyset
        if not adres.has_key(line_list[KOD_FIELD_INDEX]) \
                or adres[line_list[KOD_FIELD_INDEX]] not in line_list[ULICA_FIELD_INDEX]:
            cursor.execute("INSERT INTO generator_adresset (ulica, kod, miej_id) VALUES ('%s', '%s', %d); "
                           % (str(line_list[ULICA_FIELD_INDEX]).strip(),
                              str(line_list[KOD_FIELD_INDEX]).strip(), miejID))


            db.commit()


        i += 1

    db.close()