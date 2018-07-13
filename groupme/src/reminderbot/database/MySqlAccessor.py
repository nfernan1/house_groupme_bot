import pymysql

class MySqlAccessor:

    # Open database connection
    db = pymysql.connect("localhost", "root", "fun123", "groupme_shared_items" )

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # execute SQL query using execute() method.
    cursor.execute("SELECT VERSION()")

    # Fetch a single row using fetchone() method.
    data = cursor.fetchone()
    print ("Database version : %s " % data)

    # disconnect from server
    db.close()