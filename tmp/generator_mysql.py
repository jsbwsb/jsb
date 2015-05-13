__author__ = 'Sylwia, Beata, Joanna'

import mysql.connector
from mysql.connector import errorcode

#addresses data file
DATA_FILE = 'przerobione_pna.txt'
NUMBER_OF_ROWS = 50

#indexes of the fields in data file
WOJ_FIELD_INDEX = 6

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
    cursor.execute("DELETE FROM generator_wojset;")
    db.commit()

    #row counter
    i = 0

    woj = {}

    while i < NUMBER_OF_ROWS:
        line = file.readline()
        line_list = line.split("|")

        if not woj.has_key(line_list[WOJ_FIELD_INDEX]):
            cursor.execute("INSERT INTO generator_wojset (nazwa) VALUES ('%s'); " % line_list[WOJ_FIELD_INDEX])

            db.commit()

            cursor.execute("SELECT id from generator_wojset where nazwa = '%s'; " % line_list[WOJ_FIELD_INDEX])

            result = cursor.fetchall()

            print int(result[0])

            woj[line_list[WOJ_FIELD_INDEX]] = int(result[0])



        i += 1

    db.close()