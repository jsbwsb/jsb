__author__ = 'Sylwia'
#mysql --port=3306 --host=mysql.server --user=jsb --password=Testerki@1

import mysql.connector
from mysql.connector import errorcode

#openning data file
DATA_FILE = 'przerobione_pna.txt'
NUMBER_OF_ROWS = 10

file =  open(DATA_FILE, 'r')

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
    cursor.execute("DELETE FROM generator_adresyset;")
    db.commit()

    #row counter
    i = 0

    while i < NUMBER_OF_ROWS:
        line = file.readline()
        line_list = line.split("|")

        #print line_list

        cursor.execute("INSERT INTO generator_adresyset (kod, miejscowosc, ulica, numery, gmina, powiat, wojewodztwo) "
                       "VALUES ('%s','%s','%s','%s','%s','%s','%s'); " % tuple(line_list))
        db.commit()
        i += 1

    db.close()