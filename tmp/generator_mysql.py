__author__ = 'Sylwia'
#mysql --port=3306 --host=mysql.server --user=jsb --password=Testerki@1

import mysql.connector
from mysql.connector import errorcode

try:
  cnx = mysql.connector.connect(host='mysql.server',
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
  cnx.close()