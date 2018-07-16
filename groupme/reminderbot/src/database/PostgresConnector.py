import os
import psycopg2
from ..controllers.Log import Log


class PostgresConnector:

    def __init__(self):
        DATABASE_URL = os.environ['DATABASE_URL']
        self.conn = psycopg2.connect(database=DATABASE_URL,
                                user='liomjizjcckrtw',
                                password='aa34a6b5ee9b3e0d8a945a4413d5479908a1d44cbc987a4f5060840c1d680412',
                                host='ec2-107-22-169-45.compute-1.amazonaws.com',
                                port='5432',
                                sslmode='require')

    def commit(self):
        self.conn.commit()
        self.conn.close()

    def createCursor(self):
        return self.conn.cursor()


    def createNewQuery(self, query):
        return """{};""".format(query)


    def executeQuery(self, query):
        cursor = self.createCursor()
        cursor.execute(query)


    def fetchAll(self, tableName):
        cursor = self.createCursor()
        cursor.execute("""SELECT * from {};""".format(tableName))
        rows = cursor.fetchall()
        Log.debug(rows)